"""
Router para conexão OAuth com Instagram (Meta)
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session
import httpx
import json
from datetime import datetime, timedelta
from typing import Optional

from app.db.session import get_db
from app.db.models.channel import Channel
from app.db.models import Tenant
from app.core.auth import get_current_tenant
from app.config import get_settings

router = APIRouter()


class InstagramAuthUrlResponse(BaseModel):
    auth_url: str


class InstagramAccount(BaseModel):
    page_id: str
    page_name: str
    page_access_token: str
    ig_user_id: Optional[str] = None
    ig_username: Optional[str] = None


class InstagramCallbackResponse(BaseModel):
    accounts: list[InstagramAccount]


class InstagramConnectPayload(BaseModel):
    page_id: str
    page_name: str
    page_access_token: str
    ig_user_id: str
    ig_username: str


@router.get("/auth-url", response_model=InstagramAuthUrlResponse)
def get_instagram_auth_url(
    tenant: Tenant = Depends(get_current_tenant),
):
    """
    Gera a URL de autenticação OAuth do Facebook/Instagram
    """
    settings = get_settings()
    
    # Verificar se as configurações do Instagram estão definidas
    if not hasattr(settings, 'INSTAGRAM_APP_ID') or not settings.INSTAGRAM_APP_ID:
        raise HTTPException(
            status_code=500,
            detail="Configuração do Instagram não encontrada. Configure INSTAGRAM_APP_ID e INSTAGRAM_APP_SECRET."
        )
    
    # URL de redirecionamento após OAuth
    redirect_uri = f"{settings.PUBLIC_BASE_URL}/instagram/callback"
    
    # Permissões necessárias
    scope = ",".join([
        "pages_show_list",
        "pages_messaging",
        "instagram_basic",
        "instagram_manage_messages",
        "instagram_manage_insights",
        "business_management"
    ])
    
    # Gerar URL de autenticação
    auth_url = (
        f"https://www.facebook.com/v20.0/dialog/oauth?"
        f"client_id={settings.INSTAGRAM_APP_ID}&"
        f"redirect_uri={redirect_uri}&"
        f"scope={scope}&"
        f"response_type=code&"
        f"state={tenant.id}"  # Usar tenant_id como state para segurança
    )
    
    return InstagramAuthUrlResponse(auth_url=auth_url)


@router.get("/callback", response_model=InstagramCallbackResponse)
async def instagram_oauth_callback(
    code: str = Query(..., description="Código de autorização retornado pelo Facebook"),
    state: str = Query(..., description="State (tenant_id) para validação"),
    tenant: Tenant = Depends(get_current_tenant),
    db: Session = Depends(get_db)
):
    """
    Callback do OAuth - troca o code por access_token e busca contas disponíveis
    """
    settings = get_settings()
    
    # Validar state (tenant_id)
    if str(tenant.id) != state:
        raise HTTPException(status_code=400, detail="State inválido")
    
    redirect_uri = f"{settings.PUBLIC_BASE_URL}/instagram/callback"
    
    try:
        async with httpx.AsyncClient() as client:
            # 1. Trocar code por access_token
            token_url = "https://graph.facebook.com/v20.0/oauth/access_token"
            token_params = {
                "client_id": settings.INSTAGRAM_APP_ID,
                "client_secret": settings.INSTAGRAM_APP_SECRET,
                "redirect_uri": redirect_uri,
                "code": code
            }
            
            token_response = await client.get(token_url, params=token_params)
            token_data = token_response.json()
            
            if "error" in token_data:
                raise HTTPException(
                    status_code=400,
                    detail=f"Erro ao obter token: {token_data.get('error', {}).get('message', 'Erro desconhecido')}"
                )
            
            user_access_token = token_data.get("access_token")
            
            # 2. Obter dados do usuário para pegar o user_id
            me_response = await client.get(
                "https://graph.facebook.com/v20.0/me",
                params={"access_token": user_access_token}
            )
            me_data = me_response.json()
            user_id = me_data.get("id")
            
            # 3. Buscar páginas do Facebook vinculadas ao usuário
            pages_response = await client.get(
                f"https://graph.facebook.com/v20.0/{user_id}/accounts",
                params={
                    "access_token": user_access_token,
                    "fields": "id,name,access_token"
                }
            )
            pages_data = pages_response.json()
            
            if "error" in pages_data:
                raise HTTPException(
                    status_code=400,
                    detail=f"Erro ao buscar páginas: {pages_data.get('error', {}).get('message', 'Erro desconhecido')}"
                )
            
            accounts = []
            
            # 4. Para cada página, verificar se tem Instagram Business conectado
            for page in pages_data.get("data", []):
                page_id = page.get("id")
                page_name = page.get("name")
                page_access_token = page.get("access_token")
                
                # Trocar por long-lived token
                long_lived_response = await client.get(
                    "https://graph.facebook.com/v20.0/oauth/access_token",
                    params={
                        "grant_type": "fb_exchange_token",
                        "client_id": settings.INSTAGRAM_APP_ID,
                        "client_secret": settings.INSTAGRAM_APP_SECRET,
                        "fb_exchange_token": page_access_token
                    }
                )
                long_lived_data = long_lived_response.json()
                page_access_token = long_lived_data.get("access_token", page_access_token)
                
                # Buscar Instagram conectado à página
                ig_response = await client.get(
                    f"https://graph.facebook.com/v20.0/{page_id}",
                    params={
                        "access_token": page_access_token,
                        "fields": "instagram_business_account{id,username}"
                    }
                )
                ig_data = ig_response.json()
                
                instagram_account = ig_data.get("instagram_business_account")
                
                if instagram_account:
                    accounts.append(InstagramAccount(
                        page_id=page_id,
                        page_name=page_name,
                        page_access_token=page_access_token,
                        ig_user_id=instagram_account.get("id"),
                        ig_username=instagram_account.get("username")
                    ))
            
            if not accounts:
                raise HTTPException(
                    status_code=404,
                    detail="Nenhuma conta Instagram Business encontrada. Certifique-se de ter uma conta Business conectada a uma página do Facebook."
                )
            
            return InstagramCallbackResponse(accounts=accounts)
    
    except httpx.HTTPError as e:
        print(f"Erro HTTP ao conectar Instagram: {e}")
        raise HTTPException(status_code=500, detail="Erro ao comunicar com Facebook API")
    except Exception as e:
        print(f"Erro inesperado ao conectar Instagram: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/connect")
async def connect_instagram_account(
    payload: InstagramConnectPayload,
    tenant: Tenant = Depends(get_current_tenant),
    db: Session = Depends(get_db)
):
    """
    Conecta uma conta Instagram Business ao tenant
    """
    settings = get_settings()
    
    try:
        # Verificar se já existe um canal Instagram com este page_id
        existing_channel = db.query(Channel).filter(
            Channel.tenant_id == tenant.id,
            Channel.type == "instagram"
        ).first()
        
        # Preparar configuração
        config = {
            "fb_page_id": payload.page_id,
            "ig_user_id": payload.ig_user_id,
            "ig_username": payload.ig_username,
            "page_access_token": payload.page_access_token,
            "page_access_token_expires_at": (datetime.utcnow() + timedelta(days=60)).isoformat(),
            "app_id": settings.INSTAGRAM_APP_ID,
        }
        
        if existing_channel:
            # Atualizar canal existente
            existing_channel.name = f"Instagram - {payload.ig_username}"
            existing_channel.config = json.dumps(config)
            existing_channel.is_active = True
            print(f"✅ Canal Instagram atualizado: {payload.ig_username}")
        else:
            # Criar novo canal
            new_channel = Channel(
                tenant_id=tenant.id,
                type="instagram",
                name=f"Instagram - {payload.ig_username}",
                config=json.dumps(config),
                is_active=True
            )
            db.add(new_channel)
            print(f"✅ Novo canal Instagram criado: {payload.ig_username}")
        
        db.commit()
        
        # TODO: Registrar webhook no Facebook (se necessário)
        # Isso geralmente é feito manualmente no painel do Facebook Developers
        # ou pode ser automatizado via API
        
        return {
            "status": "success",
            "message": f"Instagram @{payload.ig_username} conectado com sucesso!"
        }
    
    except Exception as e:
        db.rollback()
        print(f"❌ Erro ao conectar Instagram: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/accounts")
def list_instagram_accounts(
    tenant: Tenant = Depends(get_current_tenant),
    db: Session = Depends(get_db)
):
    """
    Lista todas as contas Instagram conectadas do tenant
    """
    channels = db.query(Channel).filter(
        Channel.tenant_id == tenant.id,
        Channel.type == "instagram",
        Channel.is_active == True
    ).all()
    
    accounts = []
    for channel in channels:
        try:
            config = json.loads(channel.config) if channel.config else {}
            accounts.append({
                "id": channel.id,
                "name": channel.name,
                "ig_username": config.get("ig_username"),
                "ig_user_id": config.get("ig_user_id"),
                "page_id": config.get("fb_page_id"),
                "is_active": channel.is_active
            })
        except json.JSONDecodeError:
            continue
    
    return {"accounts": accounts}

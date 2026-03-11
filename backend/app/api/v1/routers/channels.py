from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
import json
import uuid
import httpx

from app.db.session import get_db
from app.db.models.channel import Channel
from app.db.models import Tenant
from app.core.auth import get_current_tenant
from app.config import get_settings

router = APIRouter()


class ChannelOut(BaseModel):
    id: int
    tenant_id: int
    type: str
    name: str
    config: str | None = None
    is_active: bool

    model_config = {"from_attributes": True}


class ChannelCreate(BaseModel):
    """Schema para criar canal (tenant_id vem do usuário autenticado)"""
    type: str
    name: str
    config: str | None = None


class ChannelUpdate(BaseModel):
    """Schema para atualizar canal"""
    name: str | None = None
    is_active: bool | None = None
    bot_token: str | None = None  # Para atualizar o token do bot Telegram
    bot_username: str | None = None  # Para atualizar o username do bot Telegram
    admin_telegram_chat_id: str | None = None  # Chat ID do admin para notify_admin


class TelegramConfigPayload(BaseModel):
    bot_token: str
    bot_username: str | None = None


@router.get("/", response_model=list[ChannelOut])
def list_channels(
    include_inactive: bool = True,
    tenant: Tenant = Depends(get_current_tenant),
    db: Session = Depends(get_db)
):
    """
    Lista canais do tenant autenticado.

    include_inactive:
      - True (default): retorna TODOS os canais (ativos e inativos)
      - False: retorna somente canais ativos
    """
    query = db.query(Channel).filter(Channel.tenant_id == tenant.id)

    if not include_inactive:
        query = query.filter(Channel.is_active == True)

    channels = query.all()
    return channels


@router.post("/", response_model=ChannelOut)
def create_channel(
    data: ChannelCreate,
    tenant: Tenant = Depends(get_current_tenant),
    db: Session = Depends(get_db)
):
    """Cria canal para o tenant autenticado"""
    channel = Channel(
        tenant_id=tenant.id,
        type=data.type,
        name=data.name,
        config=data.config,
    )
    db.add(channel)
    db.commit()
    db.refresh(channel)
    return channel


@router.put("/{channel_id}/telegram-config", response_model=ChannelOut)
def update_telegram_config(
    channel_id: int,
    payload: TelegramConfigPayload,
    db: Session = Depends(get_db)
):
    """Configura bot Telegram para um canal"""
    settings = get_settings()
    
    # Buscar canal
    channel = db.query(Channel).filter(Channel.id == channel_id).first()
    if not channel:
        raise HTTPException(status_code=404, detail="Canal não encontrado")
    
    # Validar que é um canal Telegram
    if channel.type != "telegram":
        raise HTTPException(status_code=400, detail="Canal não é do tipo Telegram")
    
    # Carregar config existente ou criar novo
    try:
        config = json.loads(channel.config) if channel.config else {}
    except json.JSONDecodeError:
        config = {}
    
    # Gerar ou manter webhook_secret
    if "webhook_secret" not in config or not config["webhook_secret"]:
        config["webhook_secret"] = str(uuid.uuid4())
    
    # Atualizar configurações
    config["bot_token"] = payload.bot_token
    if payload.bot_username:
        config["bot_username"] = payload.bot_username
    config["webhook_url"] = f"{settings.PUBLIC_BASE_URL}/api/v1/webhooks/telegram/{config['webhook_secret']}"
    
    # Ativar o canal ao conectar o bot
    channel.is_active = True
    
    # Salvar no banco
    channel.config = json.dumps(config)
    db.commit()
    db.refresh(channel)
    
    # Registrar webhook automaticamente no Telegram
    try:
        telegram_api_url = f"https://api.telegram.org/bot{payload.bot_token}/setWebhook"
        webhook_response = httpx.post(
            telegram_api_url,
            json={"url": config["webhook_url"]},
            timeout=10.0
        )
        webhook_result = webhook_response.json()
        
        if not webhook_result.get("ok"):
            print(f"⚠️ Aviso: Não foi possível registrar webhook no Telegram: {webhook_result.get('description')}")
        else:
            print(f"✅ Webhook registrado automaticamente no Telegram: {config['webhook_url']}")
    except Exception as e:
        print(f"⚠️ Erro ao registrar webhook no Telegram: {e}")
        # Não falha a operação, apenas loga o erro
    
    return channel


@router.put("/{channel_id}", response_model=ChannelOut)
def update_channel(
    channel_id: int,
    data: ChannelUpdate,
    tenant: Tenant = Depends(get_current_tenant),
    db: Session = Depends(get_db)
):
    """Atualiza informações do canal"""
    channel = db.query(Channel).filter(
        Channel.id == channel_id,
        Channel.tenant_id == tenant.id
    ).first()
    
    if not channel:
        raise HTTPException(status_code=404, detail="Canal não encontrado")
    
    # Atualizar campos
    if data.name is not None:
        channel.name = data.name
    if data.is_active is not None:
        channel.is_active = data.is_active
    
    # Atualizar token do bot Telegram (se fornecido)
    if channel.type == "telegram" and (
        data.bot_token is not None or
        data.bot_username is not None or
        data.admin_telegram_chat_id is not None
    ):
        try:
            config = json.loads(channel.config) if channel.config else {}
        except json.JSONDecodeError:
            config = {}
        
        # Atualizar o token
        if data.bot_token is not None:
            config["bot_token"] = data.bot_token

        # Atualizar o username (opcional)
        if data.bot_username is not None:
            config["bot_username"] = data.bot_username

        # Atualizar o admin chat ID (opcional)
        if data.admin_telegram_chat_id is not None:
            config["admin_telegram_chat_id"] = data.admin_telegram_chat_id

        channel.config = json.dumps(config)
        
        # Reregistrar webhook com o novo token
        if data.bot_token is not None:
            settings = get_settings()
            webhook_secret = config.get("webhook_secret")
            if webhook_secret:
                webhook_url = f"{settings.PUBLIC_BASE_URL}/api/v1/webhooks/telegram/{webhook_secret}"
                try:
                    telegram_api_url = f"https://api.telegram.org/bot{data.bot_token}/setWebhook"
                    webhook_response = httpx.post(
                        telegram_api_url,
                        json={"url": webhook_url},
                        timeout=10.0
                    )
                    webhook_result = webhook_response.json()
                    
                    if not webhook_result.get("ok"):
                        print(f"⚠️ Aviso: Não foi possível registrar webhook com novo token: {webhook_result.get('description')}")
                    else:
                        print(f"✅ Webhook re-registrado com novo token: {webhook_url}")
                except Exception as e:
                    print(f"⚠️ Erro ao re-registrar webhook: {e}")
    
    db.commit()
    db.refresh(channel)
    return channel


@router.delete("/{channel_id}")
def delete_channel(channel_id: int, db: Session = Depends(get_db)):
    """
    Deleta (desativa) um canal
    """
    channel = db.query(Channel).filter(Channel.id == channel_id).first()
    
    if not channel:
        raise HTTPException(status_code=404, detail="Canal não encontrado")
    
    # Desativar ao invés de deletar (mantém histórico)
    channel.is_active = False
    db.commit()
    
    return {"status": "ok", "message": "Canal desconectado com sucesso"}

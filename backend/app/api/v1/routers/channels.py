import json
import logging
import uuid

import httpx
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)

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


class ChannelListOut(BaseModel):
    """Schema para listagem — exclui config (contém bot_token sensível) mas expõe bot_username"""
    id: int
    tenant_id: int
    type: str
    name: str
    is_active: bool
    bot_username: str | None = None  # extraído do config server-side, sem expor bot_token

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


class TelegramWebhookInfoOut(BaseModel):
    expected_url: str | None = None
    telegram: dict | None = None


@router.get("/", response_model=list[ChannelListOut])
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
    result = []
    for ch in channels:
        bot_username = None
        if ch.type == "telegram" and ch.config:
            try:
                cfg = json.loads(ch.config)
                bot_username = cfg.get("bot_username") or None
            except (json.JSONDecodeError, AttributeError):
                pass
        result.append(ChannelListOut(
            id=ch.id,
            tenant_id=ch.tenant_id,
            type=ch.type,
            name=ch.name,
            is_active=ch.is_active,
            bot_username=bot_username,
        ))
    return result


@router.get("/{channel_id}", response_model=ChannelOut)
def get_channel(
    channel_id: int,
    tenant: Tenant = Depends(get_current_tenant),
    db: Session = Depends(get_db),
):
    """Retorna um canal pelo ID (inclui config completo para edição)."""
    ch = db.query(Channel).filter(Channel.id == channel_id, Channel.tenant_id == tenant.id).first()
    if not ch:
        raise HTTPException(status_code=404, detail="Canal não encontrado")
    return ch


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
    
    # Salvar no banco (coluna desnormalizada + JSON completo)
    channel.webhook_secret = config["webhook_secret"]
    channel.config = json.dumps(config)
    db.commit()
    db.refresh(channel)
    
    # Registrar webhook automaticamente no Telegram
    try:
        telegram_api_url = f"https://api.telegram.org/bot{payload.bot_token}/setWebhook"
        webhook_response = httpx.post(
            telegram_api_url,
            json={"url": config["webhook_url"], "allowed_updates": ["message", "callback_query", "chat_member", "chat_join_request"]},
            timeout=10.0
        )
        webhook_result = webhook_response.json()

        if not webhook_result.get("ok"):
            logger.warning("Não foi possível registrar webhook no Telegram: %s", webhook_result.get("description"))
        else:
            logger.info("Webhook registrado automaticamente no Telegram: %s", config["webhook_url"])
    except Exception as e:
        logger.warning("Erro ao registrar webhook no Telegram: %s", e)
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

    # Log leve para troubleshooting em produção (502 no proxy geralmente esconde o erro real)
    try:
        logger.debug("update_channel channel_id=%s tenant_id=%s payload=%s", channel_id, tenant.id, data.model_dump(exclude_none=True))
    except Exception:
        pass
    
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
                # Manter o config coerente com o .env atual
                config["webhook_url"] = webhook_url
                try:
                    telegram_api_url = f"https://api.telegram.org/bot{data.bot_token}/setWebhook"
                    webhook_response = httpx.post(
                        telegram_api_url,
                        json={"url": webhook_url, "allowed_updates": ["message", "callback_query", "chat_member", "chat_join_request"]},
                        timeout=10.0
                    )
                    webhook_result = webhook_response.json()

                    if not webhook_result.get("ok"):
                        logger.warning("Não foi possível registrar webhook com novo token: %s", webhook_result.get("description"))
                    else:
                        logger.info("Webhook re-registrado com novo token: %s", webhook_url)
                except Exception as e:
                    logger.warning("Erro ao re-registrar webhook: %s", e)

    # Ao ligar/desligar o bot, re-registrar (ou remover) o webhook no Telegram.
    # Importante: não falhar a operação caso o Telegram esteja indisponível.
    if channel.type == "telegram" and data.is_active is not None:
        settings = get_settings()
        try:
            config = json.loads(channel.config) if channel.config else {}
        except json.JSONDecodeError:
            config = {}

        bot_token = config.get("bot_token")
        webhook_secret = config.get("webhook_secret")

        if bot_token:
            # Sempre usar a URL derivada do .env (PUBLIC_BASE_URL) para evitar ficar preso
            # em webhook_url antigo salvo no banco.
            if not webhook_secret:
                webhook_secret = str(uuid.uuid4())
                config["webhook_secret"] = webhook_secret

            webhook_url = f"{settings.PUBLIC_BASE_URL}/api/v1/webhooks/telegram/{webhook_secret}"
            config["webhook_url"] = webhook_url
            channel.config = json.dumps(config)

            try:
                if data.is_active:
                    telegram_api_url = f"https://api.telegram.org/bot{bot_token}/setWebhook"
                    webhook_response = httpx.post(
                        telegram_api_url,
                        json={"url": webhook_url, "allowed_updates": ["message", "callback_query", "chat_member", "chat_join_request"]},
                        timeout=5.0,
                    )
                    webhook_result = webhook_response.json()
                    if not webhook_result.get("ok"):
                        logger.warning("Não foi possível (re)registrar webhook ao ativar: %s", webhook_result.get("description"))
                    else:
                        logger.info("Webhook (re)registrado ao ativar: %s", webhook_url)
                else:
                    telegram_api_url = f"https://api.telegram.org/bot{bot_token}/deleteWebhook"
                    webhook_response = httpx.post(
                        telegram_api_url,
                        json={"drop_pending_updates": True},
                        timeout=5.0,
                    )
                    webhook_result = webhook_response.json()
                    if not webhook_result.get("ok"):
                        logger.warning("Não foi possível remover webhook ao desativar: %s", webhook_result.get("description"))
                    else:
                        logger.info("Webhook removido ao desativar canal %s", channel_id)
            except Exception as e:
                logger.warning("Erro ao sincronizar webhook ao alternar status: %s", e)

    try:
        db.commit()
        db.refresh(channel)
        return channel
    except Exception as exc:
        try:
            db.rollback()
        except Exception:
            pass
        logger.error("update_channel commit error channel_id=%s tenant_id=%s: %s", channel_id, tenant.id, exc)
        raise HTTPException(status_code=500, detail="Erro ao atualizar canal")


@router.get("/{channel_id}/telegram-webhook-info", response_model=TelegramWebhookInfoOut)
def get_telegram_webhook_info(
    channel_id: int,
    tenant: Tenant = Depends(get_current_tenant),
    db: Session = Depends(get_db),
):
    """Diagnóstico: consulta getWebhookInfo do Telegram para o bot do canal."""
    channel = db.query(Channel).filter(
        Channel.id == channel_id,
        Channel.tenant_id == tenant.id,
        Channel.type == "telegram",
    ).first()
    if not channel:
        raise HTTPException(status_code=404, detail="Canal não encontrado")

    try:
        config = json.loads(channel.config) if channel.config else {}
    except json.JSONDecodeError:
        config = {}

    bot_token = config.get("bot_token")
    webhook_secret = config.get("webhook_secret")
    settings = get_settings()
    expected_url = None
    if webhook_secret:
        expected_url = f"{settings.PUBLIC_BASE_URL}/api/v1/webhooks/telegram/{webhook_secret}"

    if not bot_token:
        return TelegramWebhookInfoOut(expected_url=expected_url, telegram={"ok": False, "description": "bot_token ausente no canal"})

    try:
        res = httpx.get(
            f"https://api.telegram.org/bot{bot_token}/getWebhookInfo",
            timeout=8.0,
        )
        return TelegramWebhookInfoOut(expected_url=expected_url, telegram=res.json())
    except Exception as exc:
        return TelegramWebhookInfoOut(expected_url=expected_url, telegram={"ok": False, "description": f"Falha ao consultar Telegram: {exc}"})


@router.post("/{channel_id}/telegram-sync-webhook", response_model=TelegramWebhookInfoOut)
def telegram_sync_webhook(
    channel_id: int,
    tenant: Tenant = Depends(get_current_tenant),
    db: Session = Depends(get_db),
):
    """Força setWebhook usando URL derivada do .env (PUBLIC_BASE_URL + webhook_secret)."""
    channel = db.query(Channel).filter(
        Channel.id == channel_id,
        Channel.tenant_id == tenant.id,
        Channel.type == "telegram",
    ).first()
    if not channel:
        raise HTTPException(status_code=404, detail="Canal não encontrado")

    settings = get_settings()
    try:
        config = json.loads(channel.config) if channel.config else {}
    except json.JSONDecodeError:
        config = {}

    bot_token = config.get("bot_token")
    if not bot_token:
        raise HTTPException(status_code=400, detail="bot_token ausente no canal")

    webhook_secret = config.get("webhook_secret")
    if not webhook_secret:
        webhook_secret = str(uuid.uuid4())
        config["webhook_secret"] = webhook_secret

    expected_url = f"{settings.PUBLIC_BASE_URL}/api/v1/webhooks/telegram/{webhook_secret}"
    config["webhook_url"] = expected_url
    channel.config = json.dumps(config)

    try:
        telegram_api_url = f"https://api.telegram.org/bot{bot_token}/setWebhook"
        res = httpx.post(
            telegram_api_url,
            json={"url": expected_url, "allowed_updates": ["message", "callback_query", "chat_member", "chat_join_request"]},
            timeout=8.0,
        )
        tg = res.json()
    except Exception as exc:
        tg = {"ok": False, "description": f"Falha ao chamar Telegram setWebhook: {exc}"}

    try:
        db.commit()
        db.refresh(channel)
    except Exception:
        db.rollback()

    return TelegramWebhookInfoOut(expected_url=expected_url, telegram=tg)


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

"""
Router de Integrações Externas — Blackchat

Endpoints:
  GET  /api/v1/integrations/token          → retorna/gera o token do tenant autenticado
  POST /api/v1/integrations/token/regenerate → regenera o token
  GET  /api/v1/integrations/token/validate  → valida um token (sem autenticação JWT)
  POST /api/v1/integrations/tracking        → recebe evento de entrada/saída de grupo
"""
import secrets
import logging
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Header
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import Optional

from app.core.auth import get_current_tenant
from app.db.session import get_db
from app.db.models.tenant import Tenant
from app.db.models.contact import Contact
from app.db.models.tag import ContactTag
from app.db.models.channel import Channel
from app.db.models.flow import Flow
from app.db.models.tracking_automation import TrackingAutomation

logger = logging.getLogger(__name__)
router = APIRouter()


# ─── Schemas ──────────────────────────────────────────────────────────────────

class TokenOut(BaseModel):
    api_token: str
    tenant_name: str


class ValidateOut(BaseModel):
    valid: bool
    tenant_name: Optional[str] = None


class TrackingEvent(BaseModel):
    telegram_user_id: str
    first_name: str
    last_name: Optional[str] = ""
    username: Optional[str] = ""
    telegram_username: Optional[str] = ""  # alias usado por alguns sistemas externos
    bot_username: Optional[str] = ""       # bot que interagiu com o lead
    event: str  # "entrou" | "saiu" | "entry" | "exit"

    model_config = {"extra": "ignore"}  # ignora campos desconhecidos como funnel_id, channel_id


class TrackingOut(BaseModel):
    ok: bool
    contact_id: int
    action: str   # "created" | "updated"
    tags: list[str]


class BatchTrackingOut(BaseModel):
    ok: bool
    processed: int
    results: list[TrackingOut]


class RegisterBotIn(BaseModel):
    bot_token: str
    bot_username: str
    bot_name: Optional[str] = ""


class AutomationIn(BaseModel):
    channel_id: int
    flow_id_entrou: Optional[int] = None   # None = desativado
    flow_id_saiu: Optional[int] = None


class AutomationOut(BaseModel):
    channel_id: int
    channel_name: str
    bot_username: Optional[str] = None
    flow_id_entrou: Optional[int] = None
    flow_id_saiu: Optional[int] = None


# ─── Helpers ──────────────────────────────────────────────────────────────────

def _generate_token() -> str:
    """Gera um token único prefixado com bc_live_"""
    return f"bc_live_{secrets.token_hex(24)}"


def _get_tenant_by_token(token: str, db: Session) -> Optional[Tenant]:
    """Busca tenant pelo api_token."""
    return db.query(Tenant).filter(
        Tenant.api_token == token,
        Tenant.is_active == True  # noqa: E712
    ).first()


def _ensure_token(tenant: Tenant, db: Session) -> str:
    """Garante que o tenant tem um api_token, gerando um se não tiver."""
    if not tenant.api_token:
        while True:
            token = _generate_token()
            existing = db.query(Tenant).filter(Tenant.api_token == token).first()
            if not existing:
                break
        tenant.api_token = token
        db.add(tenant)
        db.commit()
        db.refresh(tenant)
    return tenant.api_token


# ─── Endpoints autenticados (JWT) ─────────────────────────────────────────────

@router.get("/token", response_model=TokenOut)
def get_integration_token(
    tenant: Tenant = Depends(get_current_tenant),
    db: Session = Depends(get_db),
):
    """Retorna (ou gera) o API Token do tenant para uso em integrações externas."""
    token = _ensure_token(tenant, db)
    return TokenOut(api_token=token, tenant_name=tenant.name)


@router.post("/token/regenerate", response_model=TokenOut)
def regenerate_integration_token(
    tenant: Tenant = Depends(get_current_tenant),
    db: Session = Depends(get_db),
):
    """Regenera o API Token do tenant. O token anterior para de funcionar imediatamente."""
    # Precisa buscar o tenant real do DB (não o SimpleNamespace do cache)
    db_tenant = db.query(Tenant).filter(Tenant.id == tenant.id).first()
    if not db_tenant:
        raise HTTPException(status_code=404, detail="Tenant não encontrado")

    while True:
        token = _generate_token()
        existing = db.query(Tenant).filter(Tenant.api_token == token).first()
        if not existing:
            break

    db_tenant.api_token = token
    db.add(db_tenant)
    db.commit()
    db.refresh(db_tenant)
    return TokenOut(api_token=db_tenant.api_token, tenant_name=db_tenant.name)


# ─── Endpoints públicos (autenticação por api_token) ──────────────────────────

@router.get("/token/validate", response_model=ValidateOut)
def validate_token(
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db),
):
    """
    Valida um API Token sem precisar de JWT.
    Usado pelo sistema externo ao conectar a integração.
    Header: Authorization: Bearer bc_live_xxxx
    """
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Token não fornecido")

    token = authorization.removeprefix("Bearer ").strip()
    tenant = _get_tenant_by_token(token, db)

    if not tenant:
        return ValidateOut(valid=False)

    return ValidateOut(valid=True, tenant_name=tenant.name)


def _process_single_event(payload: TrackingEvent, tenant: Tenant, db: Session) -> TrackingOut:
    """Processa um único evento de tracking. Reutilizado pelo endpoint single e batch."""

    # Normaliza evento: aceita inglês (entry/exit) e português (entrou/saiu)
    EVENT_NORMALIZE = {
        "entry": "entrou", "entrou": "entrou",
        "exit":  "saiu",   "saiu":   "saiu",
    }
    TAG_MAP = {
        "entrou": {"apply": "entrou-grupo", "remove": "saiu-grupo"},
        "saiu":   {"apply": "saiu-grupo",   "remove": "entrou-grupo"},
    }

    event = EVENT_NORMALIZE.get(payload.event.strip().lower(), payload.event.strip().lower())
    tag_apply  = TAG_MAP[event]["apply"]
    tag_remove = TAG_MAP[event]["remove"]

    # Normaliza username: aceita "username" ou "telegram_username"
    username = payload.username or payload.telegram_username or ""

    logger.info("Tracking payload: event=%s bot_username=%s telegram_user_id=%s", event, payload.bot_username, payload.telegram_user_id)

    # ── Buscar ou criar contato ─────────────────────────────────────────
    contact = db.query(Contact).filter(
        Contact.tenant_id == tenant.id,
        Contact.telegram_user_id == str(payload.telegram_user_id)
    ).first()

    action = "updated"
    if not contact:
        contact = Contact(
            tenant_id=tenant.id,
            first_name=payload.first_name,
            last_name=payload.last_name or None,
            username=username or None,
            telegram_user_id=str(payload.telegram_user_id),
            custom_fields={},
            last_interaction_at=datetime.utcnow(),
        )
        db.add(contact)
        db.flush()
        action = "created"
        logger.info("Novo contato via tracking: %s (tenant %d)", payload.telegram_user_id, tenant.id)
    else:
        contact.first_name = payload.first_name
        if payload.last_name:
            contact.last_name = payload.last_name
        if username:
            contact.username = username
        contact.last_interaction_at = datetime.utcnow()
        db.add(contact)

    # ── Vincular canal e salvar bot_username ────────────────────────────
    import json as _json
    bot_username = (payload.bot_username or "").strip().lstrip("@").lower()
    if bot_username:
        # Salva bot de origem nos custom_fields para exibição
        raw_cf = contact.custom_fields
        if isinstance(raw_cf, str):
            try:
                raw_cf = _json.loads(raw_cf) if raw_cf else {}
            except Exception:
                raw_cf = {}
        custom = dict(raw_cf) if isinstance(raw_cf, dict) else {}
        custom["_source_bot"] = bot_username
        contact.custom_fields = custom
        db.add(contact)

        # Sempre atualiza o canal quando bot_username vier no evento
        channels = db.query(Channel).filter(
            Channel.tenant_id == tenant.id,
            Channel.type == "telegram",
            Channel.is_active == True  # noqa: E712
        ).all()
        for ch in channels:
            try:
                cfg = _json.loads(ch.config or "{}")
                ch_bot = (cfg.get("bot_username") or cfg.get("username") or "").strip().lstrip("@").lower()
                if ch_bot and ch_bot == bot_username:
                    contact.default_channel_id = ch.id
                    db.add(contact)
                    break
            except Exception:
                continue

    # ── Remover tag oposta ──────────────────────────────────────────────
    db.query(ContactTag).filter(
        ContactTag.contact_id == contact.id,
        ContactTag.tag_name == tag_remove
    ).delete(synchronize_session=False)

    # ── Aplicar nova tag ────────────────────────────────────────────────
    existing_tag = db.query(ContactTag).filter(
        ContactTag.contact_id == contact.id,
        ContactTag.tag_name == tag_apply
    ).first()

    if not existing_tag:
        db.add(ContactTag(
            tenant_id=tenant.id,
            contact_id=contact.id,
            tag_name=tag_apply,
        ))

    db.flush()

    current_tags = [t.tag_name for t in db.query(ContactTag).filter(
        ContactTag.contact_id == contact.id
    ).all()]

    # ── Automação de tracking: dispara fluxo configurado para o bot/evento ──
    if contact.default_channel_id:
        automation = db.query(TrackingAutomation).filter(
            TrackingAutomation.tenant_id == tenant.id,
            TrackingAutomation.channel_id == contact.default_channel_id,
            TrackingAutomation.event == event,
        ).first()
        if automation and automation.flow_id:
            try:
                from app.db.models.flow_execution import FlowExecution
                import json as _j
                flow = db.query(Flow).filter(
                    Flow.id == automation.flow_id,
                    Flow.tenant_id == tenant.id,
                    Flow.is_active == True,  # noqa: E712
                ).first()
                ch_obj = db.query(Channel).filter(Channel.id == contact.default_channel_id).first()
                if flow and ch_obj and contact.telegram_user_id:
                    existing_exec = db.query(FlowExecution).filter(
                        FlowExecution.contact_id == contact.id,
                        FlowExecution.flow_id == flow.id,
                        FlowExecution.status.in_(["active", "waiting_response"]),
                    ).first()
                    if not existing_exec:
                        cfg = _j.loads(ch_obj.config or "{}")
                        bot_token_cfg = cfg.get("bot_token", "")
                        exec_obj = FlowExecution(
                            tenant_id=tenant.id,
                            contact_id=contact.id,
                            flow_id=flow.id,
                            trigger_type="tracking",
                            status="active",
                        )
                        db.add(exec_obj)
                        db.flush()

                        logger.info(
                            "Automação tracking: fluxo %d disparado para contato %d (evento=%s)",
                            flow.id, contact.id, event,
                        )

                        # Dispara via threading (endpoint é síncrono)
                        import threading as _t
                        from app.api.v1.routers.telegram import run_flow_background
                        _t.Thread(
                            target=run_flow_background,
                            args=(ch_obj.id, contact.id, flow.id, contact.telegram_user_id, bot_token_cfg, exec_obj.id, None),
                            daemon=True,
                        ).start()
            except Exception as exc:
                logger.warning("Erro ao disparar automação tracking: %s", exc)

    return TrackingOut(ok=True, contact_id=contact.id, action=action, tags=current_tags)


def _authenticate(authorization: Optional[str], db: Session) -> Tenant:
    """Valida o Bearer token e retorna o tenant."""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Token não fornecido")
    token = authorization.removeprefix("Bearer ").strip()
    tenant = _get_tenant_by_token(token, db)
    if not tenant:
        raise HTTPException(status_code=401, detail="Token inválido")
    return tenant


@router.post("/tracking", response_model=TrackingOut)
def receive_tracking_event(
    payload: TrackingEvent,
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db),
):
    """
    Recebe um único evento de entrada/saída de grupo.
    Header: Authorization: Bearer bc_live_xxxx
    """
    tenant = _authenticate(authorization, db)

    event = payload.event.strip().lower()
    if event not in ("entrou", "saiu", "entry", "exit"):
        raise HTTPException(status_code=422, detail="Campo 'event' deve ser 'entrou', 'saiu', 'entry' ou 'exit'")
    if not payload.telegram_user_id or not payload.first_name:
        raise HTTPException(status_code=422, detail="Campos 'telegram_user_id' e 'first_name' são obrigatórios")

    try:
        result = _process_single_event(payload, tenant, db)
        db.commit()
    except IntegrityError:
        db.rollback()
        logger.warning("IntegrityError ao salvar tracking event para %s", payload.telegram_user_id)
        raise HTTPException(status_code=500, detail="Erro ao salvar evento")

    return result


@router.post("/tracking/batch", response_model=BatchTrackingOut)
def receive_tracking_batch(
    events: list[TrackingEvent],
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db),
):
    """
    Recebe múltiplos eventos de entrada/saída em uma única requisição.
    Máximo de 500 eventos por batch.
    Header: Authorization: Bearer bc_live_xxxx
    """
    tenant = _authenticate(authorization, db)

    if not events:
        raise HTTPException(status_code=422, detail="Lista de eventos não pode ser vazia")

    if len(events) > 500:
        raise HTTPException(status_code=422, detail="Máximo de 500 eventos por batch")

    results = []
    for payload in events:
        event = payload.event.strip().lower()
        if event not in ("entrou", "saiu", "entry", "exit"):
            logger.warning("Evento inválido ignorado: %s", payload.event)
            continue
        if not payload.telegram_user_id or not payload.first_name:
            logger.warning("Evento sem campos obrigatórios ignorado: %s", payload.telegram_user_id)
            continue
        try:
            result = _process_single_event(payload, tenant, db)
            results.append(result)
        except Exception as e:
            logger.warning("Erro ao processar evento batch para %s: %s", payload.telegram_user_id, e)
            db.rollback()

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        logger.error("IntegrityError no commit do batch (tenant %d)", tenant.id)
        raise HTTPException(status_code=500, detail="Erro ao salvar batch")

    logger.info("Batch processado: %d eventos (tenant %d)", len(results), tenant.id)

    return BatchTrackingOut(ok=True, processed=len(results), results=results)


# ─── Auto-registro de bot via TrackLeadPro ────────────────────────────────────

@router.post("/register-bot")
def register_bot_from_external(
    body: RegisterBotIn,
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db),
):
    """
    Registra automaticamente um bot Telegram no Blackchat.
    Chamado pelo TrackLeadPro quando o usuário conecta a integração.

    Se o canal já existir (mesmo bot_username) apenas garante que está ativo.
    Se não existir, cria o canal e registra no CORE.

    Header: Authorization: Bearer bc_live_xxxx
    Body: { "bot_token": "...", "bot_username": "...", "bot_name": "..." }
    """
    import json as _j
    import secrets as _s

    tenant = _authenticate(authorization, db)

    bot_username = body.bot_username.strip().lstrip("@").lower()
    bot_name = body.bot_name.strip() if body.bot_name else bot_username
    bot_token = body.bot_token.strip()

    if not bot_username or not bot_token:
        raise HTTPException(status_code=422, detail="bot_token e bot_username são obrigatórios")

    # Verificar se canal com esse bot já existe (por username ou token)
    channels = db.query(Channel).filter(
        Channel.tenant_id == tenant.id,
        Channel.type == "telegram",
    ).all()

    existing_channel = None
    for ch in channels:
        try:
            cfg = _j.loads(ch.config or "{}")
            ch_bot = (cfg.get("bot_username") or cfg.get("username") or "").strip().lstrip("@").lower()
            ch_token = (cfg.get("bot_token") or "").strip()
            if ch_bot == bot_username or ch_token == bot_token:
                existing_channel = ch
                break
        except Exception:
            continue

    # Se já existe, retorna imediatamente sem criar duplicata
    if existing_channel:
        logger.info("[register-bot] Canal já existe: %s (tenant %d)", bot_username, tenant.id)
        return {
            "ok": True,
            "channel_id": existing_channel.id,
            "bot_username": bot_username,
            "action": "already_exists",
        }

    webhook_secret = _s.token_hex(16)

    config = {
        "bot_token": bot_token,
        "bot_username": bot_username,
        "webhook_secret": webhook_secret,
    }

    # Criar novo canal
    channel = Channel(
        tenant_id=tenant.id,
        type="telegram",
        name=bot_name or bot_username,
        config=_j.dumps(config),
        webhook_secret=webhook_secret,
        is_active=True,
    )
    db.add(channel)
    db.flush()
    logger.info("[register-bot] Novo canal criado: %s (tenant %d)", bot_username, tenant.id)

    # NÃO registrar webhook no Telegram diretamente — o CORE já é o webhook.
    # O Blackchat recebe os updates via Redis Pub/Sub publicado pelo CORE.

    # Registrar no CORE e obter core_bot_id real via getWebhookInfo
    try:
        from app.api.v1.routers.channels import _register_bot_in_core
        _register_bot_in_core(channel, bot_token, config, db)
    except Exception as e:
        logger.warning("[register-bot] Erro ao registrar no CORE: %s", e)

    db.commit()

    # Iniciar listener Redis para o novo canal sem precisar reiniciar o backend
    try:
        from app.workers.core_listener import _listen_bot_sync
        import threading
        if channel.core_bot_id and channel.webhook_secret:
            t = threading.Thread(
                target=_listen_bot_sync,
                args=(channel.core_bot_id, channel.webhook_secret),
                daemon=True,
                name=f"core-{channel.core_bot_id}",
            )
            t.start()
            logger.info("[register-bot] Listener CORE iniciado: %s", channel.core_bot_id)
    except Exception as e:
        logger.warning("[register-bot] Erro ao iniciar listener CORE: %s", e)

    return {
        "ok": True,
        "channel_id": channel.id,
        "bot_username": bot_username,
        "action": "created",
    }


# ─── Automações de Tracking (por bot/canal) ────────────────────────────────────

import json as _json_mod

@router.get("/automations", response_model=list[AutomationOut])
def list_automations(
    tenant: Tenant = Depends(get_current_tenant),
    db: Session = Depends(get_db),
):
    """Retorna automações de tracking configuradas por canal (bot)."""
    channels = db.query(Channel).filter(
        Channel.tenant_id == tenant.id,
        Channel.type == "telegram",
    ).all()

    result = []
    for ch in channels:
        bot_username = None
        try:
            cfg = _json_mod.loads(ch.config or "{}")
            bot_username = cfg.get("bot_username") or cfg.get("username") or None
        except Exception:
            pass

        flow_id_entrou = None
        flow_id_saiu = None
        automations = db.query(TrackingAutomation).filter(
            TrackingAutomation.tenant_id == tenant.id,
            TrackingAutomation.channel_id == ch.id,
        ).all()
        for a in automations:
            if a.event == "entrou":
                flow_id_entrou = a.flow_id
            elif a.event == "saiu":
                flow_id_saiu = a.flow_id

        result.append(AutomationOut(
            channel_id=ch.id,
            channel_name=ch.name,
            bot_username=bot_username,
            flow_id_entrou=flow_id_entrou,
            flow_id_saiu=flow_id_saiu,
        ))

    return result


@router.put("/automations", response_model=AutomationOut)
def save_automation(
    body: AutomationIn,
    tenant: Tenant = Depends(get_current_tenant),
    db: Session = Depends(get_db),
):
    """Salva (cria ou atualiza) automações de tracking para um canal."""
    ch = db.query(Channel).filter(
        Channel.id == body.channel_id,
        Channel.tenant_id == tenant.id,
    ).first()
    if not ch:
        raise HTTPException(status_code=404, detail="Canal não encontrado")

    for event, flow_id in [("entrou", body.flow_id_entrou), ("saiu", body.flow_id_saiu)]:
        existing = db.query(TrackingAutomation).filter(
            TrackingAutomation.tenant_id == tenant.id,
            TrackingAutomation.channel_id == body.channel_id,
            TrackingAutomation.event == event,
        ).first()
        if existing:
            existing.flow_id = flow_id
        else:
            db.add(TrackingAutomation(
                tenant_id=tenant.id,
                channel_id=body.channel_id,
                event=event,
                flow_id=flow_id,
            ))

    db.commit()

    bot_username = None
    try:
        cfg = _json_mod.loads(ch.config or "{}")
        bot_username = cfg.get("bot_username") or cfg.get("username") or None
    except Exception:
        pass

    return AutomationOut(
        channel_id=ch.id,
        channel_name=ch.name,
        bot_username=bot_username,
        flow_id_entrou=body.flow_id_entrou,
        flow_id_saiu=body.flow_id_saiu,
    )

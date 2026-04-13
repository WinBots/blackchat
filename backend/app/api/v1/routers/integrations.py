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

    # ── Vincular canal pelo bot_username ────────────────────────────────
    bot_username = (payload.bot_username or "").strip().lstrip("@").lower()
    if bot_username and not contact.default_channel_id:
        channels = db.query(Channel).filter(
            Channel.tenant_id == tenant.id,
            Channel.type == "telegram",
            Channel.is_active == True  # noqa: E712
        ).all()
        for ch in channels:
            try:
                import json
                cfg = json.loads(ch.config or "{}")
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

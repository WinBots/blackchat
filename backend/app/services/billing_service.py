"""
Serviço de Billing VPM (Valor por Mil contatos ativos).

Implementa:
- Contagem de contatos ativos (últimos 30 dias)
- Cálculo VPM + mínimo mensal
- Checagem de limites do plano
- Resposta padronizada de limite excedido
"""
from __future__ import annotations

import math
from datetime import datetime, timedelta, timezone
from typing import Optional

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.db.models.contact import Contact
from app.db.models.plan import Plan
from app.db.models.subscription import Subscription, SubscriptionStatus

import logging
logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────────────────────
# Constantes de limites por plano
# ─────────────────────────────────────────────────────────────
PLAN_LIMITS: dict[str, dict] = {
    "free": {
        "max_contacts": 100,
        "max_flows": 1,
        "max_tags": 1,
        "max_sequences": 1,
        "vpm_price": None,
        "min_monthly": None,
    },
    "pro": {
        "max_contacts": None,   # Ilimitado (pago por VPM)
        "max_flows": None,
        "max_tags": None,
        "max_sequences": None,
        "vpm_price": 49.0,
        "min_monthly": 99.0,
    },
    "unlimited": {
        "max_contacts": None,
        "max_flows": None,
        "max_tags": None,
        "max_sequences": None,
        "vpm_price": 29.0,
        "min_monthly": 999.0,
    },
}


# ─────────────────────────────────────────────────────────────
# Contagem de contatos ativos
# ─────────────────────────────────────────────────────────────
def count_active_contacts(db: Session, tenant_id: int) -> int:
    """
    Conta contatos que interagiram nos últimos 30 dias (base do VPM).

    Regra do PLANOS.md:
    - Contato ativo = interagiu com o bot nos últimos 30 dias OR recebeu/enviou mensagem no mês.
    - Aqui usamos last_interaction_at (atualizado pelo handler de mensagens).
    - Fallback: se last_interaction_at for NULL (contatos antigos), conta todos com created_at
      nos últimos 30 dias para não penalizar dados legados.
    """
    cutoff = datetime.now(timezone.utc) - timedelta(days=30)

    count = (
        db.query(func.count(Contact.id))
        .filter(
            Contact.tenant_id == tenant_id,
            Contact.last_interaction_at >= cutoff,
        )
        .scalar()
        or 0
    )
    return int(count)


def count_total_contacts(db: Session, tenant_id: int) -> int:
    """Conta total de contatos do tenant (para exibição e controle do Free)."""
    return int(
        db.query(func.count(Contact.id)).filter(Contact.tenant_id == tenant_id).scalar() or 0
    )


# ─────────────────────────────────────────────────────────────
# Cálculo VPM
# ─────────────────────────────────────────────────────────────
def calculate_vpm(
    vpm_price: float,
    min_monthly: float,
    active_contacts: int,
) -> dict:
    """
    Calcula o valor mensal com base no modelo VPM.

    Fórmula (PLANOS.md §3.1):
        blocos = ceil(active_contacts / 1000)
        valor_calculado = blocos * vpm_price
        valor_final = max(valor_calculado, min_monthly)

    Returns dict com:
        - thousand_blocks: int
        - calculated_amount: float
        - minimum_applied: bool
        - final_amount: float
    """
    blocks = math.ceil(active_contacts / 1000) if active_contacts > 0 else 1
    calculated = blocks * vpm_price
    minimum_applied = calculated < min_monthly
    final = max(calculated, min_monthly)

    return {
        "thousand_blocks": blocks,
        "calculated_amount": round(calculated, 2),
        "minimum_applied": minimum_applied,
        "final_amount": round(final, 2),
    }


def estimate_billing(db: Session, tenant_id: int, plan: Plan) -> Optional[dict]:
    """
    Retorna estimativa de billing VPM para o tenant com base no plano atual.
    Retorna None se o plano não é VPM (ex.: Free).
    """
    vpm_price = float(plan.vpm_price or 0) if plan.vpm_price else None
    min_monthly = float(plan.min_monthly or 0) if plan.min_monthly else None

    if not vpm_price or not min_monthly:
        return None  # Plano Free não tem VPM

    active = count_active_contacts(db, tenant_id)
    result = calculate_vpm(vpm_price, min_monthly, active)
    result["active_contacts"] = active
    result["vpm_price"] = vpm_price
    result["min_monthly"] = min_monthly
    return result


# ─────────────────────────────────────────────────────────────
# Checagem de limites
# ─────────────────────────────────────────────────────────────
class LimitExceededError(Exception):
    """Levantada quando uma ação ultrapassa o limite do plano."""

    def __init__(
        self,
        limit_type: str,
        current: int,
        limit: int,
        action_blocked: str,
        suggested_plan: str = "pro",
    ):
        self.limit_type = limit_type
        self.current = current
        self.limit = limit
        self.action_blocked = action_blocked
        self.suggested_plan = suggested_plan
        super().__init__(f"PLAN_LIMIT_EXCEEDED: {limit_type} ({current}/{limit})")

    def to_dict(self) -> dict:
        return {
            "code": "PLAN_LIMIT_EXCEEDED",
            "limit_type": self.limit_type,
            "current": self.current,
            "limit": self.limit,
            "action_blocked": self.action_blocked,
            "upgrade_required": True,
            "suggested_plan": self.suggested_plan,
        }


def get_active_subscription(db: Session, tenant_id: int) -> Optional[Subscription]:
    return (
        db.query(Subscription)
        .filter(Subscription.tenant_id == tenant_id)
        .order_by(Subscription.id.desc())
        .first()
    )


def _fire_limit_email_once(db: Session, tenant_id: int, err: "LimitExceededError") -> None:
    """
    Envia e-mail de limite atingido uma vez a cada 24 h por tipo de limite.
    Usa LimitEvent como registro de deduplicacao (sessao propria para nao interferir na transacao pai).
    """
    try:
        from app.db.session import SessionLocal
        from app.db.models.limit_event import LimitEvent
        from app.db.models.user import User as UserModel
        from app.services.email_sender import send_plan_limit_reached_email_background

        inner_db = SessionLocal()
        try:
            cutoff = datetime.now(timezone.utc) - timedelta(hours=24)
            already = inner_db.query(LimitEvent).filter(
                LimitEvent.tenant_id == tenant_id,
                LimitEvent.limit_type == err.limit_type,
                LimitEvent.detected_at >= cutoff,
            ).first()
            if already:
                return

            ev = LimitEvent(
                tenant_id=tenant_id,
                limit_type=err.limit_type,
                limit_value=err.limit,
                current_value=err.current,
                status="warning",
            )
            inner_db.add(ev)

            plan = get_plan_for_tenant(inner_db, tenant_id)
            user = (
                inner_db.query(UserModel)
                .filter(UserModel.tenant_id == tenant_id, UserModel.is_active == True)  # noqa: E712
                .order_by(UserModel.id.asc())
                .first()
            )
            inner_db.commit()

            if user:
                send_plan_limit_reached_email_background(
                    to_email=user.email,
                    full_name=user.full_name,
                    limit_type=err.limit_type,
                    current=err.current,
                    limit=err.limit,
                    plan_name=getattr(plan, "display_name", plan.name) if plan else "",
                )
        finally:
            inner_db.close()
    except Exception:
        logger.exception("Falha ao notificar limite de plano para tenant_id=%s", tenant_id)


def check_contact_limit(db: Session, tenant_id: int, plan: Plan) -> None:
    """
    Verifica limite de contatos para plano Free (100 contatos ATIVOS — últimos 30 dias).
    Levanta LimitExceededError se ultrapassado.

    Usa contatos ATIVOS (last_interaction_at >= agora-30d) para ser consistente
    com a régua de billing VPM. Pro/Enterprise não bloqueiam (cobrança via VPM).
    """
    max_contacts = plan.max_contacts
    if max_contacts is None:
        return  # Ilimitado (Pro / Enterprise)

    # Free: mede por contatos ativos (mesma régua do VPM)
    active = count_active_contacts(db, tenant_id)
    if active >= max_contacts:
        err = LimitExceededError(
            limit_type="contacts",
            current=active,
            limit=max_contacts,
            action_blocked="new_contact_entry",
            suggested_plan="pro",
        )
        _fire_limit_email_once(db, tenant_id, err)
        raise err


def check_flow_limit(db: Session, tenant_id: int, plan: Plan, current_flows: int) -> None:
    """Verifica limite de fluxos. Levanta LimitExceededError se ultrapassado."""
    max_flows = plan.max_flows
    if max_flows is None:
        return
    if current_flows >= max_flows:
        err = LimitExceededError(
            limit_type="flows",
            current=current_flows,
            limit=max_flows,
            action_blocked="create_flow",
            suggested_plan="pro",
        )
        _fire_limit_email_once(db, tenant_id, err)
        raise err


def check_sequence_limit(db: Session, tenant_id: int, plan: Plan, current_sequences: int) -> None:
    """Verifica limite de sequências. Levanta LimitExceededError se ultrapassado."""
    max_sequences = getattr(plan, "max_sequences", None)
    if max_sequences is None:
        return
    if current_sequences >= max_sequences:
        raise LimitExceededError(
            limit_type="sequences",
            current=current_sequences,
            limit=max_sequences,
            action_blocked="create_sequence",
            suggested_plan="pro",
        )


def check_tag_limit(db: Session, tenant_id: int, plan: Plan, current_tags: int) -> None:
    """Verifica limite de tags. Levanta LimitExceededError se ultrapassado."""
    max_tags = getattr(plan, "max_tags", None)
    if max_tags is None:
        return
    if current_tags >= max_tags:
        raise LimitExceededError(
            limit_type="tags",
            current=current_tags,
            limit=max_tags,
            action_blocked="create_tag",
            suggested_plan="pro",
        )


def get_plan_for_tenant(db: Session, tenant_id: int) -> Optional[Plan]:
    """
    Retorna o plano ativo do tenant via subscrição mais recente.
    Faz fallback para o plano Free se não houver assinatura.
    """
    sub = get_active_subscription(db, tenant_id)
    if sub and sub.plan_id:
        plan = db.query(Plan).filter(Plan.id == sub.plan_id).first()
        if plan:
            return plan
    # Fallback: plano Free
    return db.query(Plan).filter(Plan.name == "free").first()

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.auth import get_current_tenant
from app.db.session import get_db
from app.db.models import Tenant
from app.db.models.subscription import Subscription, SubscriptionStatus
from app.db.models.plan import Plan
from app.db.models.channel import Channel
from app.db.models.contact import Contact
from app.db.models.message import Message
from app.services.billing_service import count_active_contacts, estimate_billing

router = APIRouter()


class UsageItem(BaseModel):
    used: int
    limit: Optional[int] = None


class VpmEstimateOut(BaseModel):
    active_contacts: int
    thousand_blocks: int
    vpm_price: Optional[float]
    min_monthly: Optional[float]
    calculated_amount: Optional[float]
    minimum_applied: Optional[bool]
    final_amount: Optional[float]


class SubscriptionMeOut(BaseModel):
    subscription_id: Optional[int] = None
    status: Optional[str] = None
    started_at: Optional[str] = None
    trial_ends_at: Optional[str] = None
    current_period_start: Optional[str] = None
    current_period_end: Optional[str] = None

    plan: Optional[dict] = None
    usage: dict
    contracted_contacts: Optional[int] = None
    estimate: Optional[VpmEstimateOut] = None


def _iso(dt) -> Optional[str]:
    if not dt:
        return None
    try:
        return dt.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")
    except Exception:
        try:
            return dt.isoformat()
        except Exception:
            return None


@router.get("/me", response_model=SubscriptionMeOut)
def get_my_subscription(
    tenant: Tenant = Depends(get_current_tenant),
    db: Session = Depends(get_db),
):
    """Assinatura atual + uso real do tenant e estimativa VPM."""

    sub = (
        db.query(Subscription)
        .filter(Subscription.tenant_id == tenant.id)
        .order_by(Subscription.id.desc())
        .first()
    )

    plan: Optional[Plan] = None
    if sub:
        plan = db.query(Plan).filter(Plan.id == sub.plan_id).first()

    if not sub:
        # Garante uma assinatura padrão (trial free) para o tenant se ele não tiver
        free_plan = db.query(Plan).filter(Plan.name == "free").first()
        if not free_plan:
            free_plan = db.query(Plan).order_by(Plan.price_monthly.asc()).first()

        if free_plan:
            now = datetime.now(timezone.utc)
            sub = Subscription(
                tenant_id=tenant.id,
                plan_id=free_plan.id,
                status=SubscriptionStatus.TRIAL,
                started_at=now,
                trial_ends_at=now + timedelta(days=14),
                current_period_start=now,
                current_period_end=now + timedelta(days=14),
            )
            db.add(sub)
            db.commit()
            db.refresh(sub)
            plan = free_plan

    bots_used = int((db.query(func.count(Channel.id)).filter(Channel.tenant_id == tenant.id).scalar() or 0))
    contacts_used = int((db.query(func.count(Contact.id)).filter(Contact.tenant_id == tenant.id).scalar() or 0))
    
    # Contatos ativos (VPM)
    active_contacts_used = count_active_contacts(db, tenant.id)

    # Mensagens do mês corrente (UTC)
    now = datetime.now(timezone.utc)
    month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    messages_used = int(
        (
            db.query(func.count(Message.id))
            .filter(Message.tenant_id == tenant.id, Message.created_at >= month_start)
            .scalar()
            or 0
        )
    )

    usage = {
        "bots": UsageItem(used=bots_used, limit=(plan.max_bots if plan else None)).model_dump(),
        "contacts": UsageItem(used=contacts_used, limit=(plan.max_contacts if plan else None)).model_dump(),
        "active_contacts": UsageItem(used=active_contacts_used, limit=None).model_dump(),
        "messages_per_month": UsageItem(
            used=messages_used,
            limit=(plan.max_messages_per_month if plan else None),
        ).model_dump(),
        "flows": UsageItem(used=0, limit=(plan.max_flows if plan else None)).model_dump(),
    }

    plan_out = None
    estimate_out = None

    if plan:
        plan_out = {
            "id": plan.id,
            "name": plan.name,
            "display_name": plan.display_name,
            "description": plan.description,
            "price_monthly": float(plan.price_monthly or 0),
            "max_bots": plan.max_bots,
            "max_contacts": plan.max_contacts,
            "max_messages_per_month": plan.max_messages_per_month,
            "max_flows": plan.max_flows,
            "vpm_price": float(plan.vpm_price) if plan.vpm_price else None,
            "min_monthly": float(plan.min_monthly) if plan.min_monthly else None,
        }
        
        estimate_dict = estimate_billing(db, tenant.id, plan)
        if estimate_dict:
            estimate_out = VpmEstimateOut(**estimate_dict)

    # Contatos contratados: Enterprise usa o valor salvo no checkout; Pro usa plan.max_contacts
    contracted = None
    if sub:
        contracted = sub.contracted_contacts
    if contracted is None and plan:
        contracted = plan.max_contacts  # Pro=2500, Free=500, Enterprise=None

    return SubscriptionMeOut(
        subscription_id=(sub.id if sub else None),
        status=(str(sub.status.value) if sub and getattr(sub, "status", None) else None),
        started_at=_iso(getattr(sub, "started_at", None) if sub else None),
        trial_ends_at=_iso(getattr(sub, "trial_ends_at", None) if sub else None),
        current_period_start=_iso(getattr(sub, "current_period_start", None) if sub else None),
        current_period_end=_iso(getattr(sub, "current_period_end", None) if sub else None),
        plan=plan_out,
        usage=usage,
        contracted_contacts=contracted,
        estimate=estimate_out,
    )

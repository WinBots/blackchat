"""
Router de administração (gerenciar planos, etc)
"""
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import or_, func as sa_func
from typing import List, Optional

from app.db.session import get_db
from app.db.models import (
    Plan, User, Tenant, Subscription,
    SubscriptionHistory, StripeWebhookEvent, LimitEvent,
)
from app.db.models.subscription import SubscriptionStatus
from app.core.auth import get_current_user

router = APIRouter()


# Schemas
class PlanBase(BaseModel):
    name: str
    display_name: str
    description: str | None = None
    price_monthly: float
    max_bots: int | None = None
    max_contacts: int | None = None
    max_messages_per_month: int | None = None
    max_flows: int | None = None
    has_advanced_flows: bool = True
    has_api_access: bool = False
    has_webhooks: bool = False
    has_priority_support: bool = False
    has_whitelabel: bool = False
    is_active: bool = True
    stripe_price_id_monthly: str | None = None


class PlanCreate(PlanBase):
    pass


class PlanUpdate(BaseModel):
    display_name: str | None = None
    description: str | None = None
    price_monthly: float | None = None
    max_bots: int | None = None
    max_contacts: int | None = None
    max_messages_per_month: int | None = None
    max_flows: int | None = None
    has_advanced_flows: bool | None = None
    has_api_access: bool | None = None
    has_webhooks: bool | None = None
    has_priority_support: bool | None = None
    has_whitelabel: bool | None = None
    is_active: bool | None = None
    stripe_price_id_monthly: str | None = None


class PlanOut(PlanBase):
    id: int
    
    model_config = {"from_attributes": True}


# Dependency para verificar se é admin
def get_admin_user(user: User = Depends(get_current_user)):
    """Verifica se o usuário é admin"""
    if not (user.is_admin or bool(getattr(user, "is_super_admin", False))):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso restrito a administradores"
        )
    return user


def get_super_admin_user(user: User = Depends(get_current_user)):
    """Verifica se o usuário é super admin (admin global)."""
    if not bool(getattr(user, "is_super_admin", False)):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso restrito ao super admin"
        )
    return user


def _parse_dt(value: str | None) -> datetime | None:
    if not value:
        return None
    v = value.strip()
    if not v:
        return None
    try:
        # Aceita ISO com Z
        if v.endswith("Z"):
            v = v[:-1] + "+00:00"
        return datetime.fromisoformat(v)
    except Exception:
        return None


class TenantOut(BaseModel):
    id: int
    name: str
    email: str
    timezone: str | None = None
    is_active: bool
    stripe_customer_id: str | None = None


class SubscriptionOut(BaseModel):
    id: int
    tenant_id: int
    plan_id: int
    status: str
    started_at: str | None = None
    trial_ends_at: str | None = None
    current_period_start: str | None = None
    current_period_end: str | None = None
    canceled_at: str | None = None
    stripe_subscription_id: str | None = None
    stripe_price_id: str | None = None


class TenantWithSubscriptionOut(BaseModel):
    tenant: TenantOut
    subscription: SubscriptionOut | None = None
    plan: PlanOut | None = None


class TenantUpdateIn(BaseModel):
    name: str | None = None
    email: str | None = None
    timezone: str | None = None
    is_active: bool | None = None


class SubscriptionUpdateIn(BaseModel):
    plan_id: int | None = None
    status: str | None = None
    trial_ends_at: str | None = None
    current_period_start: str | None = None
    current_period_end: str | None = None
    canceled_at: str | None = None


class UserOut(BaseModel):
    id: int
    tenant_id: int
    email: str
    full_name: str
    is_active: bool
    is_admin: bool
    is_super_admin: bool


class UserUpdateIn(BaseModel):
    full_name: str | None = None
    is_active: bool | None = None
    is_admin: bool | None = None
    is_super_admin: bool | None = None


@router.get("/plans", response_model=List[PlanOut])
def list_plans(
    user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """Lista todos os planos (admin)"""
    plans = db.query(Plan).all()
    return plans


@router.post("/plans", response_model=PlanOut)
def create_plan(
    data: PlanCreate,
    user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """Cria novo plano (admin)"""
    # Verificar se já existe plano com esse nome
    existing = db.query(Plan).filter(Plan.name == data.name).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Já existe um plano com este nome"
        )
    
    plan = Plan(**data.model_dump())
    db.add(plan)
    db.commit()
    db.refresh(plan)
    return plan


@router.put("/plans/{plan_id}", response_model=PlanOut)
def update_plan(
    plan_id: int,
    data: PlanUpdate,
    user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """Atualiza plano (admin)"""
    plan = db.query(Plan).filter(Plan.id == plan_id).first()
    if not plan:
        raise HTTPException(status_code=404, detail="Plano não encontrado")
    
    # Atualizar campos fornecidos
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(plan, field, value)
    
    db.commit()
    db.refresh(plan)
    return plan


@router.delete("/plans/{plan_id}")
def delete_plan(
    plan_id: int,
    user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """Desativa plano (admin)"""
    plan = db.query(Plan).filter(Plan.id == plan_id).first()
    if not plan:
        raise HTTPException(status_code=404, detail="Plano não encontrado")
    
    # Desativar ao invés de deletar
    plan.is_active = False
    db.commit()
    
    return {"status": "ok", "message": "Plano desativado"}


@router.get("/tenants", response_model=List[TenantWithSubscriptionOut])
def admin_list_tenants(
    user: User = Depends(get_super_admin_user),
    db: Session = Depends(get_db),
):
    """Lista tenants (super admin), incluindo assinatura atual e plano."""
    tenants = db.query(Tenant).order_by(Tenant.id.asc()).all()
    out: List[TenantWithSubscriptionOut] = []
    for t in tenants:
        sub = (
            db.query(Subscription)
            .filter(Subscription.tenant_id == t.id)
            .order_by(Subscription.id.desc())
            .first()
        )
        plan = db.query(Plan).filter(Plan.id == sub.plan_id).first() if sub else None

        out.append(
            TenantWithSubscriptionOut(
                tenant=TenantOut(
                    id=t.id,
                    name=t.name,
                    email=t.email,
                    timezone=getattr(t, "timezone", None),
                    is_active=bool(t.is_active),
                    stripe_customer_id=getattr(t, "stripe_customer_id", None),
                ),
                subscription=(
                    SubscriptionOut(
                        id=sub.id,
                        tenant_id=sub.tenant_id,
                        plan_id=sub.plan_id,
                        status=str(getattr(sub.status, "value", sub.status)),
                        started_at=sub.started_at.strftime("%Y-%m-%d %H:%M:%S") if sub.started_at else None,
                        trial_ends_at=sub.trial_ends_at.strftime("%Y-%m-%d %H:%M:%S") if sub.trial_ends_at else None,
                        current_period_start=sub.current_period_start.strftime("%Y-%m-%d %H:%M:%S") if sub.current_period_start else None,
                        current_period_end=sub.current_period_end.strftime("%Y-%m-%d %H:%M:%S") if sub.current_period_end else None,
                        canceled_at=sub.canceled_at.strftime("%Y-%m-%d %H:%M:%S") if sub.canceled_at else None,
                        stripe_subscription_id=getattr(sub, "stripe_subscription_id", None),
                        stripe_price_id=getattr(sub, "stripe_price_id", None),
                    )
                    if sub
                    else None
                ),
                plan=(PlanOut.model_validate(plan) if plan else None),
            )
        )
    return out


@router.put("/tenants/{tenant_id}", response_model=TenantOut)
def admin_update_tenant(
    tenant_id: int,
    data: TenantUpdateIn,
    user: User = Depends(get_super_admin_user),
    db: Session = Depends(get_db),
):
    """Atualiza dados gerais do tenant (super admin)."""
    t = db.query(Tenant).filter(Tenant.id == tenant_id).first()
    if not t:
        raise HTTPException(status_code=404, detail="Tenant não encontrado")

    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(t, field, value)
    db.commit()
    db.refresh(t)

    return TenantOut(
        id=t.id,
        name=t.name,
        email=t.email,
        timezone=getattr(t, "timezone", None),
        is_active=bool(t.is_active),
        stripe_customer_id=getattr(t, "stripe_customer_id", None),
    )


@router.put("/tenants/{tenant_id}/subscription", response_model=SubscriptionOut)
def admin_update_tenant_subscription(
    tenant_id: int,
    data: SubscriptionUpdateIn,
    user: User = Depends(get_super_admin_user),
    db: Session = Depends(get_db),
):
    """Cria/atualiza assinatura do tenant (super admin).

    Permite ajustar plano, status e períodos (trial/current period).
    """
    tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant não encontrado")

    sub = (
        db.query(Subscription)
        .filter(Subscription.tenant_id == tenant_id)
        .order_by(Subscription.id.desc())
        .first()
    )
    if not sub:
        # cria uma assinatura base
        plan_id = data.plan_id
        if not plan_id:
            p = db.query(Plan).order_by(Plan.price_monthly.asc()).first()
            if not p:
                raise HTTPException(status_code=400, detail="Nenhum plano cadastrado")
            plan_id = p.id
        sub = Subscription(tenant_id=tenant_id, plan_id=int(plan_id), status=SubscriptionStatus.TRIAL)
        db.add(sub)
        db.flush()

    # plano
    if data.plan_id is not None:
        plan = db.query(Plan).filter(Plan.id == int(data.plan_id)).first()
        if not plan:
            raise HTTPException(status_code=404, detail="Plano não encontrado")
        sub.plan_id = int(data.plan_id)

    # status
    if data.status is not None:
        try:
            sub.status = SubscriptionStatus(str(data.status))
        except Exception:
            raise HTTPException(status_code=400, detail="Status de assinatura inválido")

    # datas
    dt_trial = _parse_dt(data.trial_ends_at)
    dt_ps = _parse_dt(data.current_period_start)
    dt_pe = _parse_dt(data.current_period_end)
    dt_c = _parse_dt(data.canceled_at)
    if data.trial_ends_at is not None:
        sub.trial_ends_at = dt_trial
    if data.current_period_start is not None:
        sub.current_period_start = dt_ps
    if data.current_period_end is not None:
        sub.current_period_end = dt_pe
    if data.canceled_at is not None:
        sub.canceled_at = dt_c

    db.commit()
    db.refresh(sub)

    return SubscriptionOut(
        id=sub.id,
        tenant_id=sub.tenant_id,
        plan_id=sub.plan_id,
        status=str(getattr(sub.status, "value", sub.status)),
        started_at=sub.started_at.isoformat() if sub.started_at else None,
        trial_ends_at=sub.trial_ends_at.isoformat() if sub.trial_ends_at else None,
        current_period_start=sub.current_period_start.isoformat() if sub.current_period_start else None,
        current_period_end=sub.current_period_end.isoformat() if sub.current_period_end else None,
        canceled_at=sub.canceled_at.isoformat() if sub.canceled_at else None,
        stripe_subscription_id=getattr(sub, "stripe_subscription_id", None),
        stripe_price_id=getattr(sub, "stripe_price_id", None),
    )


@router.get("/users", response_model=List[UserOut])
def admin_list_users(
    user: User = Depends(get_super_admin_user),
    db: Session = Depends(get_db),
):
    users = db.query(User).order_by(User.id.asc()).all()
    return [
        UserOut(
            id=u.id,
            tenant_id=u.tenant_id,
            email=u.email,
            full_name=u.full_name,
            is_active=bool(u.is_active),
            is_admin=bool(u.is_admin),
            is_super_admin=bool(getattr(u, "is_super_admin", False)),
        )
        for u in users
    ]


@router.put("/users/{user_id}", response_model=UserOut)
def admin_update_user(
    user_id: int,
    data: UserUpdateIn,
    user: User = Depends(get_super_admin_user),
    db: Session = Depends(get_db),
):
    u = db.query(User).filter(User.id == user_id).first()
    if not u:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")

    payload = data.model_dump(exclude_unset=True)
    # não permitir tirar o próprio super admin sem querer? mantém simples.
    for field, value in payload.items():
        setattr(u, field, value)
    db.commit()
    db.refresh(u)

    return UserOut(
        id=u.id,
        tenant_id=u.tenant_id,
        email=u.email,
        full_name=u.full_name,
        is_active=bool(u.is_active),
        is_admin=bool(u.is_admin),
        is_super_admin=bool(getattr(u, "is_super_admin", False)),
    )


# ═══════════════════════════════════════════════════════════════════════════════
#  Assinaturas — listagem paginada com filtros
# ═══════════════════════════════════════════════════════════════════════════════

@router.get("/subscriptions")
def admin_list_subscriptions(
    page: int = Query(1, ge=1),
    page_size: int = Query(25, ge=1, le=100),
    search: Optional[str] = Query(None, description="Busca por nome ou email do tenant"),
    status_filter: Optional[str] = Query(None, alias="status", description="Filtrar por status"),
    plan_id: Optional[int] = Query(None, description="Filtrar por plano"),
    stripe_mode: Optional[str] = Query(None, description="Filtrar por modo stripe (test/live)"),
    date_from: Optional[str] = Query(None, description="Data início (YYYY-MM-DD)"),
    date_to: Optional[str] = Query(None, description="Data fim (YYYY-MM-DD)"),
    user: User = Depends(get_super_admin_user),
    db: Session = Depends(get_db),
):
    """Lista todas as assinaturas com dados do tenant, plano e owner. Paginação server-side."""
    q = (
        db.query(Subscription, Tenant, Plan)
        .join(Tenant, Subscription.tenant_id == Tenant.id)
        .outerjoin(Plan, Subscription.plan_id == Plan.id)
    )

    # Filtros
    if search:
        pattern = f"%{search}%"
        q = q.filter(or_(Tenant.name.ilike(pattern), Tenant.email.ilike(pattern)))

    if status_filter:
        try:
            q = q.filter(Subscription.status == SubscriptionStatus(status_filter))
        except ValueError:
            pass

    if plan_id:
        q = q.filter(Subscription.plan_id == plan_id)

    if stripe_mode:
        q = q.filter(Subscription.stripe_mode == stripe_mode)

    if date_from:
        try:
            dt = datetime.fromisoformat(date_from)
            q = q.filter(Subscription.started_at >= dt)
        except ValueError:
            pass

    if date_to:
        try:
            dt = datetime.fromisoformat(date_to + "T23:59:59")
            q = q.filter(Subscription.started_at <= dt)
        except ValueError:
            pass

    total = q.count()
    rows = (
        q.order_by(Subscription.id.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )

    def _fmt(dt_val):
        return dt_val.strftime("%Y-%m-%d %H:%M:%S") if dt_val else None

    # Owner de cada tenant
    owner_cache: dict[int, str | None] = {}

    def _get_owner(tid: int) -> str | None:
        if tid not in owner_cache:
            owner = db.query(User).filter(User.tenant_id == tid).order_by(User.id.asc()).first()
            owner_cache[tid] = (owner.full_name or owner.email) if owner else None
        return owner_cache[tid]

    items = []
    for sub, t, p in rows:
        items.append({
            "id": sub.id,
            "tenant_id": sub.tenant_id,
            "tenant_name": t.name if t else None,
            "tenant_email": t.email if t else None,
            "owner_name": _get_owner(sub.tenant_id),
            "plan_id": sub.plan_id,
            "plan_name": p.display_name if p else (p.name if p else None),
            "status": str(getattr(sub.status, "value", sub.status)),
            "started_at": _fmt(sub.started_at),
            "trial_ends_at": _fmt(sub.trial_ends_at),
            "current_period_start": _fmt(sub.current_period_start),
            "current_period_end": _fmt(sub.current_period_end),
            "canceled_at": _fmt(sub.canceled_at),
            "stripe_subscription_id": getattr(sub, "stripe_subscription_id", None),
            "stripe_mode": getattr(sub, "stripe_mode", None),
            "monthly_amount_cents": getattr(sub, "monthly_amount_cents", None),
            "contracted_contacts": getattr(sub, "contracted_contacts", None),
        })

    return {
        "items": items,
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": max(1, -(-total // page_size)),
    }


# ═══════════════════════════════════════════════════════════════════════════════
#  Log de Eventos — combina subscription_history, stripe_webhook_events, limit_events
# ═══════════════════════════════════════════════════════════════════════════════

@router.get("/event-log")
def admin_event_log(
    page: int = Query(1, ge=1),
    page_size: int = Query(25, ge=1, le=100),
    source: Optional[str] = Query(None, description="Filtrar por fonte: subscription, stripe, limit"),
    search: Optional[str] = Query(None, description="Busca texto livre"),
    date_from: Optional[str] = Query(None),
    date_to: Optional[str] = Query(None),
    user: User = Depends(get_super_admin_user),
    db: Session = Depends(get_db),
):
    """Log de eventos unificado (subscription_history + stripe_webhook_events + limit_events)."""

    dt_from = None
    dt_to = None
    if date_from:
        try:
            dt_from = datetime.fromisoformat(date_from)
        except ValueError:
            pass
    if date_to:
        try:
            dt_to = datetime.fromisoformat(date_to + "T23:59:59")
        except ValueError:
            pass

    events: list[dict] = []

    # ── subscription_history ──────────────────────────────────────────────
    if not source or source == "subscription":
        q = db.query(SubscriptionHistory)
        if dt_from:
            q = q.filter(SubscriptionHistory.created_at >= dt_from)
        if dt_to:
            q = q.filter(SubscriptionHistory.created_at <= dt_to)
        if search:
            pat = f"%{search}%"
            q = q.filter(
                or_(
                    SubscriptionHistory.event_type.ilike(pat),
                    SubscriptionHistory.old_plan_name.ilike(pat),
                    SubscriptionHistory.new_plan_name.ilike(pat),
                    SubscriptionHistory.note.ilike(pat),
                )
            )
        for h in q.all():
            tenant = db.query(Tenant).filter(Tenant.id == h.tenant_id).first() if h.tenant_id else None
            desc_parts = []
            if h.old_plan_name or h.new_plan_name:
                desc_parts.append(f"{h.old_plan_name or '—'} → {h.new_plan_name or '—'}")
            if h.old_status or h.new_status:
                desc_parts.append(f"status: {h.old_status or '—'} → {h.new_status or '—'}")
            if h.note:
                desc_parts.append(h.note)

            events.append({
                "source": "subscription",
                "event_type": h.event_type,
                "description": " | ".join(desc_parts) if desc_parts else h.event_type,
                "tenant_id": h.tenant_id,
                "tenant_name": tenant.name if tenant else None,
                "stripe_mode": h.stripe_mode,
                "created_at": h.created_at.strftime("%Y-%m-%d %H:%M:%S") if h.created_at else None,
                "extra": None,
            })

    # ── stripe_webhook_events ─────────────────────────────────────────────
    if not source or source == "stripe":
        q = db.query(StripeWebhookEvent)
        if dt_from:
            q = q.filter(StripeWebhookEvent.received_at >= dt_from)
        if dt_to:
            q = q.filter(StripeWebhookEvent.received_at <= dt_to)
        if search:
            pat = f"%{search}%"
            q = q.filter(
                or_(
                    StripeWebhookEvent.event_type.ilike(pat),
                    StripeWebhookEvent.stripe_event_id.ilike(pat),
                    StripeWebhookEvent.error_message.ilike(pat),
                )
            )
        for ev in q.all():
            events.append({
                "source": "stripe",
                "event_type": ev.event_type,
                "description": f"{ev.stripe_event_id} — {ev.status}" + (f" | {ev.error_message}" if ev.error_message else ""),
                "tenant_id": None,
                "tenant_name": None,
                "stripe_mode": ev.stripe_mode,
                "created_at": ev.received_at.strftime("%Y-%m-%d %H:%M:%S") if ev.received_at else None,
                "extra": {
                    "status": ev.status,
                    "processed_at": ev.processed_at.strftime("%Y-%m-%d %H:%M:%S") if ev.processed_at else None,
                },
            })

    # ── limit_events ──────────────────────────────────────────────────────
    if not source or source == "limit":
        q = db.query(LimitEvent)
        if dt_from:
            q = q.filter(LimitEvent.detected_at >= dt_from)
        if dt_to:
            q = q.filter(LimitEvent.detected_at <= dt_to)
        if search:
            pat = f"%{search}%"
            q = q.filter(
                or_(
                    LimitEvent.limit_type.ilike(pat),
                    LimitEvent.status.ilike(pat),
                )
            )
        for le in q.all():
            tenant = db.query(Tenant).filter(Tenant.id == le.tenant_id).first() if le.tenant_id else None
            events.append({
                "source": "limit",
                "event_type": f"limit_{le.limit_type}",
                "description": f"{le.limit_type}: {le.current_value}/{le.limit_value} — {le.status}",
                "tenant_id": le.tenant_id,
                "tenant_name": tenant.name if tenant else None,
                "stripe_mode": None,
                "created_at": le.detected_at.strftime("%Y-%m-%d %H:%M:%S") if le.detected_at else None,
                "extra": {
                    "status": le.status,
                    "resolved_at": le.resolved_at.strftime("%Y-%m-%d %H:%M:%S") if le.resolved_at else None,
                },
            })

    # Ordenar por data desc
    events.sort(key=lambda e: e["created_at"] or "", reverse=True)

    total = len(events)
    start = (page - 1) * page_size
    paged = events[start : start + page_size]

    return {
        "items": paged,
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": max(1, -(-total // page_size)),
    }


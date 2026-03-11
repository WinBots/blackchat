"""
Router de administração (gerenciar planos, etc)
"""
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import List

from app.db.session import get_db
from app.db.models import Plan, User, Tenant, Subscription
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
                        started_at=sub.started_at.isoformat() if sub.started_at else None,
                        trial_ends_at=sub.trial_ends_at.isoformat() if sub.trial_ends_at else None,
                        current_period_start=sub.current_period_start.isoformat() if sub.current_period_start else None,
                        current_period_end=sub.current_period_end.isoformat() if sub.current_period_end else None,
                        canceled_at=sub.canceled_at.isoformat() if sub.canceled_at else None,
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


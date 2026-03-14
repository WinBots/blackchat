from __future__ import annotations

from typing import List, Optional

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.auth import get_current_tenant
from app.config import get_settings
from app.db.session import get_db
from app.db.models.plan import Plan
from app.db.models import Tenant

router = APIRouter()


class PlanOut(BaseModel):
    id: int
    name: str
    display_name: str
    description: Optional[str] = None

    # Preço
    price_monthly: float
    price_yearly: Optional[float] = None
    vpm_price: Optional[float] = None    # R$/1.000 contatos ativos (None = plano fixo)
    min_monthly: Optional[float] = None  # Mínimo mensal para planos VPM

    # Limites (None = ilimitado)
    max_bots: Optional[int] = None
    max_contacts: Optional[int] = None
    max_messages_per_month: Optional[int] = None
    max_flows: Optional[int] = None
    max_tags: Optional[int] = None
    max_sequences: Optional[int] = None

    # Features
    has_advanced_flows: bool = True
    has_api_access: bool = False
    has_webhooks: bool = False
    has_priority_support: bool = False
    has_whitelabel: bool = False
    has_early_access: bool = False

    is_active: bool
    stripe_price_id_monthly: Optional[str] = None
    stripe_price_id_yearly: Optional[str] = None

    model_config = {"from_attributes": True}


def _seed_plans(db: Session) -> None:
    """Cria ou atualiza os 3 planos canônicos (Free / Pro / Enterprise) conforme PLANOS.md."""

    settings = get_settings()

    # Pro (fixo): em produção, configure via .env com IDs do modo LIVE.
    # Em ambiente local, mantém fallback para o price_id de teste legado (facilita dev).
    pro_monthly_price_id = (getattr(settings, "STRIPE_PRO_PRICE_ID_MONTHLY", "") or "").strip() or None
    pro_yearly_price_id = (getattr(settings, "STRIPE_PRO_PRICE_ID_YEARLY", "") or "").strip() or None
    if settings.ENVIRONMENT in {"local", "dev", "development"} and not pro_monthly_price_id:
        pro_monthly_price_id = "price_1T5g14H2dYCb5KgDXFXPwDtI"

    canonical = [
        # ── Free ─────────────────────────────────────────────────────
        dict(
            name="free",
            display_name="Free",
            description="Para testar a ferramenta",
            price_monthly=0.00,
            price_yearly=None,
            vpm_price=None,
            min_monthly=None,
            max_bots=1,
            max_contacts=100,   # Hard limit conforme PLANOS.md §4.1
            max_messages_per_month=None,
            max_flows=1,
            max_tags=1,
            max_sequences=1,
            has_advanced_flows=False,
            has_api_access=False,
            has_webhooks=False,
            has_priority_support=False,
            has_whitelabel=False,
            has_early_access=False,
            is_active=True,
            stripe_price_id_monthly=None,
            stripe_price_id_yearly=None,
        ),
        # ── Pro ──────────────────────────────────────────────────────
        dict(
            name="pro",
            display_name="Pro",
            description="Plano fixo para até 2.500 contatos ativos",
            price_monthly=99.00,   # Preço fixo mensal
            price_yearly=None,
            vpm_price=None,        # Sem VPM — preço fixo
            min_monthly=None,
            max_bots=3,
            max_contacts=2500,     # Limite fixo do plano Pro
            max_messages_per_month=None,
            max_flows=None,        # Fluxos ilimitados
            max_tags=None,         # Tags ilimitadas
            max_sequences=None,    # Sequências ilimitadas
            has_advanced_flows=True,
            has_api_access=False,
            has_webhooks=False,
            has_priority_support=False,
            has_whitelabel=False,
            has_early_access=False,
            is_active=True,
            stripe_price_id_monthly=pro_monthly_price_id,
            stripe_price_id_yearly=pro_yearly_price_id,
        ),
        # ── Enterprise ───────────────────────────────────────────────
        dict(
            name="unlimited",
            display_name="Enterprise",
            description="Plano personalizado cobrado pelo volume de contatos",
            price_monthly=0.00,    # 0 = dinâmico; valor real calculado no checkout
            price_yearly=None,
            vpm_price=49.00,       # Taxa base (referência para exibição)
            min_monthly=999.00,    # Mínimo cobrado
            max_bots=None,         # Ilimitado
            max_contacts=None,     # Ilimitado — cobrado por VPM
            max_messages_per_month=None,
            max_flows=None,
            max_tags=None,
            max_sequences=None,
            has_advanced_flows=True,
            has_api_access=True,
            has_webhooks=True,
            has_priority_support=True,
            has_whitelabel=False,
            has_early_access=True,
            is_active=True,
            stripe_price_id_monthly=None,  # Preço dinâmico via price_data no checkout
            stripe_price_id_yearly=None,
        ),
    ]

    for data in canonical:
        existing = db.query(Plan).filter(Plan.name == data["name"]).first()
        if existing:
            # Atualiza todos os campos de preços, VPM, IDs do Stripe e limites
            for k, v in data.items():
                # Não sobrescreve IDs Stripe existentes quando o seed não tem valor.
                if k in {"stripe_price_id_monthly", "stripe_price_id_yearly"} and v is None:
                    continue
                setattr(existing, k, v)
        else:
            db.add(Plan(**data))

    # Desativa planos legados que não são mais canônicos
    legacy_names = {"basic", "professional", "enterprise"}
    db.query(Plan).filter(Plan.name.in_(legacy_names)).update(
        {"is_active": False}, synchronize_session=False
    )

    db.commit()


@router.get("/", response_model=List[PlanOut])
def list_plans(
    tenant: Tenant = Depends(get_current_tenant),
    db: Session = Depends(get_db),
):
    """Lista planos ativos (Free / Pro / Enterprise) com campos VPM."""
    _seed_plans(db)

    from sqlalchemy import case
    order = case(
        (Plan.name == "free", 0),
        (Plan.name == "pro", 1),
        (Plan.name == "unlimited", 2),
        else_=9,
    )
    plans = (
        db.query(Plan)
        .filter(Plan.is_active == True)  # noqa: E712
        .order_by(order)
        .all()
    )

    out: List[PlanOut] = []
    for p in plans:
        out.append(
            PlanOut(
                id=p.id,
                name=p.name,
                display_name=p.display_name,
                description=p.description,
                price_monthly=float(p.price_monthly or 0),
                price_yearly=float(p.price_yearly) if p.price_yearly else None,
                vpm_price=float(p.vpm_price) if p.vpm_price else None,
                min_monthly=float(p.min_monthly) if p.min_monthly else None,
                max_bots=p.max_bots,
                max_contacts=p.max_contacts,
                max_messages_per_month=p.max_messages_per_month,
                max_flows=p.max_flows,
                max_tags=p.max_tags,
                max_sequences=p.max_sequences,
                has_advanced_flows=bool(p.has_advanced_flows),
                has_api_access=bool(p.has_api_access),
                has_webhooks=bool(p.has_webhooks),
                has_priority_support=bool(p.has_priority_support),
                has_whitelabel=bool(p.has_whitelabel),
                has_early_access=bool(getattr(p, "has_early_access", False)),
                is_active=bool(p.is_active),
                stripe_price_id_monthly=getattr(p, "stripe_price_id_monthly", None),
                stripe_price_id_yearly=getattr(p, "stripe_price_id_yearly", None),
            )
        )
    return out

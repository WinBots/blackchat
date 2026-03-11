"""
Router público (endpoints sem autenticação)
"""
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import List, Optional

from app.db.session import get_db
from app.db.models import Plan
from app.api.v1.routers.plans import _seed_plans

router = APIRouter()


class PlanPublicOut(BaseModel):
    """Schema público de plano para Landing Page — inclui campos VPM"""
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
    has_advanced_flows: bool
    has_api_access: bool
    has_webhooks: bool
    has_priority_support: bool
    has_whitelabel: bool
    has_early_access: Optional[bool] = False

    stripe_price_id_monthly: Optional[str] = None
    stripe_price_id_yearly: Optional[str] = None

    model_config = {"from_attributes": True}


@router.get("/plans", response_model=List[PlanPublicOut])
def list_public_plans(db: Session = Depends(get_db)):
    """Lista planos ativos (público - sem autenticação). Faz seed dos planos se necessário."""
    _seed_plans(db)
    plans = db.query(Plan).filter(Plan.is_active == True).order_by(Plan.price_monthly).all()  # noqa: E712
    out = []
    for p in plans:
        out.append(PlanPublicOut(
            id=p.id,
            name=p.name,
            display_name=p.display_name,
            description=p.description,
            price_monthly=float(p.price_monthly or 0),
            price_yearly=float(p.price_yearly) if getattr(p, "price_yearly", None) else None,
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
            stripe_price_id_monthly=getattr(p, "stripe_price_id_monthly", None),
            stripe_price_id_yearly=getattr(p, "stripe_price_id_yearly", None),
        ))
    return out


@router.get("/health")
def health_check():
    """Health check"""
    return {"status": "ok", "service": "Blackchat Pro SaaS"}

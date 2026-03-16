"""
Serviço de cache de alto nível.
Cada função faz: cache_get → se None → busca no banco → cache_set → retorna.
Todas são seguras: se o Redis estiver fora, vai direto ao banco.
"""
import json
import logging
from typing import Optional

from sqlalchemy.orm import Session

from app.cache.redis_client import cache_get, cache_set, cache_delete, cache_delete_pattern
from app.cache.keys import CacheKeys

logger = logging.getLogger("blackchat.cache")


# ═══════════════════════════════════════════
#  PLANOS
# ═══════════════════════════════════════════

def get_all_plans_cached(db: Session) -> list:
    """Retorna todos os planos ativos (cache ou banco)."""
    cached = cache_get(CacheKeys.PLANS_ALL)
    if cached is not None:
        return cached

    from app.db.models.plan import Plan
    from sqlalchemy import case

    order = case(
        (Plan.name == "free", 0),
        (Plan.name == "pro", 1),
        (Plan.name == "unlimited", 2),
        else_=9,
    )
    plans = db.query(Plan).filter(Plan.is_active == True).order_by(order).all()  # noqa: E712
    result = []
    for p in plans:
        result.append({
            "id": p.id,
            "name": p.name,
            "display_name": p.display_name,
            "description": p.description,
            "price_monthly": float(p.price_monthly or 0),
            "price_yearly": float(p.price_yearly) if p.price_yearly else None,
            "vpm_price": float(p.vpm_price) if p.vpm_price else None,
            "min_monthly": float(p.min_monthly) if p.min_monthly else None,
            "max_bots": p.max_bots,
            "max_contacts": p.max_contacts,
            "max_messages_per_month": p.max_messages_per_month,
            "max_flows": p.max_flows,
            "max_tags": p.max_tags,
            "max_sequences": p.max_sequences,
            "has_advanced_flows": bool(p.has_advanced_flows),
            "has_api_access": bool(p.has_api_access),
            "has_webhooks": bool(p.has_webhooks),
            "has_priority_support": bool(p.has_priority_support),
            "has_whitelabel": bool(p.has_whitelabel),
            "has_early_access": bool(getattr(p, "has_early_access", False)),
            "is_active": bool(p.is_active),
            "stripe_price_id_monthly": getattr(p, "stripe_price_id_monthly", None),
            "stripe_price_id_yearly": getattr(p, "stripe_price_id_yearly", None),
        })

    cache_set(CacheKeys.PLANS_ALL, result, CacheKeys.PLANS_TTL)
    return result


def get_plan_cached(db: Session, plan_id: int) -> Optional[dict]:
    """Retorna um plano específico (cache ou banco)."""
    key = CacheKeys.plan(plan_id)
    cached = cache_get(key)
    if cached is not None:
        return cached

    from app.db.models.plan import Plan
    p = db.query(Plan).filter(Plan.id == plan_id).first()
    if not p:
        return None

    result = {
        "id": p.id,
        "name": p.name,
        "display_name": p.display_name,
        "price_monthly": float(p.price_monthly) if p.price_monthly else 0,
        "max_bots": p.max_bots,
        "max_contacts": p.max_contacts,
        "max_flows": p.max_flows,
        "max_tags": p.max_tags,
        "max_sequences": p.max_sequences,
        "stripe_price_id_monthly": getattr(p, "stripe_price_id_monthly", None),
    }
    cache_set(key, result, CacheKeys.PLAN_TTL)
    return result


def invalidate_plans():
    """Limpa cache de planos (após editar no superadmin)."""
    cache_delete(CacheKeys.PLANS_ALL)
    cache_delete_pattern("plan:*")


# ═══════════════════════════════════════════
#  SUBSCRIPTION
# ═══════════════════════════════════════════

def get_subscription_cached(db: Session, tenant_id: int) -> Optional[dict]:
    """Retorna dados da assinatura do tenant (cache ou banco)."""
    key = CacheKeys.subscription(tenant_id)
    cached = cache_get(key)
    if cached is not None:
        return cached

    from app.db.models.subscription import Subscription
    sub = (
        db.query(Subscription)
        .filter(Subscription.tenant_id == tenant_id)
        .order_by(Subscription.id.desc())
        .first()
    )
    if not sub:
        return None

    result = {
        "id": sub.id,
        "tenant_id": sub.tenant_id,
        "plan_id": sub.plan_id,
        "status": sub.status.value if hasattr(sub.status, "value") else str(sub.status),
        "stripe_subscription_id": sub.stripe_subscription_id,
        "stripe_customer_id": sub.stripe_customer_id,
        "current_period_start": str(sub.current_period_start) if sub.current_period_start else None,
        "current_period_end": str(sub.current_period_end) if sub.current_period_end else None,
        "contracted_contacts": getattr(sub, 'contracted_contacts', None),
        "monthly_amount_cents": getattr(sub, 'monthly_amount_cents', None),
    }
    cache_set(key, result, CacheKeys.SUBSCRIPTION_TTL)
    return result


def invalidate_subscription(tenant_id: int):
    """Limpa cache de assinatura (após mudar plano, pagamento, etc)."""
    cache_delete(CacheKeys.subscription(tenant_id))


# ═══════════════════════════════════════════
#  FLUXOS E STEPS
# ═══════════════════════════════════════════

def get_flow_steps_cached(db: Session, flow_id: int) -> Optional[list]:
    """Retorna steps de um fluxo (cache ou banco)."""
    key = CacheKeys.flow_steps(flow_id)
    cached = cache_get(key)
    if cached is not None:
        return cached

    from app.db.models.flow_step import FlowStep
    steps = (
        db.query(FlowStep)
        .filter(FlowStep.flow_id == flow_id)
        .order_by(FlowStep.order_index)
        .all()
    )
    if not steps:
        return None

    result = []
    for s in steps:
        result.append({
            "id": s.id,
            "flow_id": s.flow_id,
            "type": s.type,
            "order_index": s.order_index,
            "config": s.config,  # JSON string — será parseado no consumer
        })

    cache_set(key, result, CacheKeys.FLOW_STEPS_TTL)
    return result


def invalidate_flow(flow_id: int):
    """Limpa cache de um fluxo (após editar steps/conexões)."""
    cache_delete(CacheKeys.flow(flow_id))
    cache_delete(CacheKeys.flow_steps(flow_id))


def invalidate_tenant_flows(tenant_id: int):
    """Limpa cache de todos os fluxos do tenant."""
    cache_delete_pattern("flow:*")


# ═══════════════════════════════════════════
#  STRIPE CONFIG
# ═══════════════════════════════════════════

def get_stripe_config_cached(db: Session) -> Optional[dict]:
    """Retorna config Stripe (cache ou banco)."""
    cached = cache_get(CacheKeys.STRIPE_CONFIG)
    if cached is not None:
        return cached

    from app.db.models.stripe_config import StripeConfig
    cfg = db.query(StripeConfig).filter(StripeConfig.id == 1).first()
    if not cfg:
        return None

    result = {
        "id": cfg.id,
        "mode_active": cfg.mode_active,
        "test_secret_key": cfg.test_secret_key,
        "test_publishable_key": cfg.test_publishable_key,
        "test_webhook_secret": cfg.test_webhook_secret,
        "test_pro_price_id": cfg.test_pro_price_id,
        "test_enterprise_product_id": cfg.test_enterprise_product_id,
        "live_secret_key": cfg.live_secret_key,
        "live_publishable_key": cfg.live_publishable_key,
        "live_webhook_secret": cfg.live_webhook_secret,
        "live_pro_price_id": cfg.live_pro_price_id,
        "live_enterprise_product_id": cfg.live_enterprise_product_id,
    }
    cache_set(CacheKeys.STRIPE_CONFIG, result, CacheKeys.STRIPE_CONFIG_TTL)
    return result


def invalidate_stripe_config():
    """Limpa cache de config Stripe (após salvar no superadmin)."""
    cache_delete(CacheKeys.STRIPE_CONFIG)


# ═══════════════════════════════════════════
#  CHANNEL CONFIG
# ═══════════════════════════════════════════

def invalidate_channel(channel_id: int):
    """Limpa cache de canal (após editar config/activate/deactivate)."""
    cache_delete(CacheKeys.channel(channel_id))

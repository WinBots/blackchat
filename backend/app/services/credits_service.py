"""
Serviço central de créditos IA.
Toda lógica de consumo, alocação e compra passa por aqui.
"""
from __future__ import annotations

import logging
from datetime import date, timedelta
from typing import Optional

from sqlalchemy.orm import Session

from app.db.models.tenant_credits import TenantCredits, CreditTransaction
from app.db.models.subscription import Subscription, SubscriptionStatus

logger = logging.getLogger(__name__)

# Alocação de créditos por plano (plan.name)
PLAN_CREDITS = {
    "free":       1,
    "pro":        10,
    "unlimited":  25,  # Enterprise
}


def _get_or_create_credits(tenant_id: int, db: Session) -> TenantCredits:
    """Retorna ou cria o registro de créditos do tenant."""
    credits = db.query(TenantCredits).filter(
        TenantCredits.tenant_id == tenant_id
    ).with_for_update().first()

    if not credits:
        credits = TenantCredits(
            tenant_id=tenant_id,
            plan_balance=0,
            plan_monthly_allocation=0,
            purchased_balance=0,
        )
        db.add(credits)
        db.flush()

    return credits


def get_balance(tenant_id: int, db: Session) -> dict:
    """Retorna saldo atual do tenant."""
    credits = db.query(TenantCredits).filter(
        TenantCredits.tenant_id == tenant_id
    ).first()

    if not credits:
        return {
            "plan_balance": 0,
            "plan_monthly_allocation": 0,
            "plan_reset_date": None,
            "purchased_balance": 0,
            "total": 0,
        }

    return {
        "plan_balance": credits.plan_balance,
        "plan_monthly_allocation": credits.plan_monthly_allocation,
        "plan_reset_date": credits.plan_reset_date.isoformat() if credits.plan_reset_date else None,
        "purchased_balance": credits.purchased_balance,
        "total": credits.plan_balance + credits.purchased_balance,
    }


def consume_credit(tenant_id: int, operation: str, db: Session) -> dict:
    """
    Deduz 1 crédito do tenant com prioridade: plano → comprado.
    Retorna dict com resultado ou lança ValueError se sem saldo.
    """
    credits = _get_or_create_credits(tenant_id, db)

    plan_before = credits.plan_balance
    purchased_before = credits.purchased_balance
    total = plan_before + purchased_before

    if total <= 0:
        raise ValueError("out_of_credits")

    # Prioridade: plano primeiro
    if credits.plan_balance > 0:
        credits.plan_balance -= 1
        source = "plan"
    else:
        credits.purchased_balance -= 1
        source = "purchased"

    db.add(credits)

    tx = CreditTransaction(
        tenant_id=tenant_id,
        type="consumed",
        source=source,
        amount=1,
        reason=operation,
        plan_balance_before=plan_before,
        plan_balance_after=credits.plan_balance,
        purchased_balance_before=purchased_before,
        purchased_balance_after=credits.purchased_balance,
        created_by="system",
    )
    db.add(tx)
    db.commit()

    logger.info("Crédito consumido: tenant=%d source=%s op=%s saldo=%d+%d",
                tenant_id, source, operation, credits.plan_balance, credits.purchased_balance)

    return {
        "success": True,
        "consumed": 1,
        "source": source,
        "balance": {
            "plan": credits.plan_balance,
            "purchased": credits.purchased_balance,
            "total": credits.plan_balance + credits.purchased_balance,
        },
    }


def add_purchased_credits(tenant_id: int, amount: int, stripe_event_id: str, db: Session) -> dict:
    """Adiciona créditos comprados após pagamento Stripe confirmado."""
    credits = _get_or_create_credits(tenant_id, db)

    plan_before = credits.plan_balance
    purchased_before = credits.purchased_balance

    credits.purchased_balance += amount
    db.add(credits)

    tx = CreditTransaction(
        tenant_id=tenant_id,
        type="purchased",
        source="purchased",
        amount=amount,
        reason="stripe_payment",
        plan_balance_before=plan_before,
        plan_balance_after=plan_before,
        purchased_balance_before=purchased_before,
        purchased_balance_after=credits.purchased_balance,
        created_by="stripe",
        stripe_event_id=stripe_event_id,
    )
    db.add(tx)
    db.commit()

    logger.info("Créditos comprados adicionados: tenant=%d amount=%d total_comprados=%d",
                tenant_id, amount, credits.purchased_balance)

    return {
        "plan": credits.plan_balance,
        "purchased": credits.purchased_balance,
        "total": credits.plan_balance + credits.purchased_balance,
    }


def allocate_plan_credits(tenant_id: int, amount: int, reset_date: date, db: Session) -> None:
    """
    Aloca créditos do plano (reset mensal ou upgrade).
    Créditos do plano não acumulam — substituem o saldo anterior.
    """
    credits = _get_or_create_credits(tenant_id, db)

    plan_before = credits.plan_balance
    purchased_before = credits.purchased_balance

    credits.plan_balance = amount
    credits.plan_monthly_allocation = amount
    credits.plan_reset_date = reset_date
    db.add(credits)

    tx = CreditTransaction(
        tenant_id=tenant_id,
        type="plan_allocation",
        source="plan",
        amount=amount,
        reason="monthly_reset",
        plan_balance_before=plan_before,
        plan_balance_after=amount,
        purchased_balance_before=purchased_before,
        purchased_balance_after=purchased_before,
        created_by="system",
    )
    db.add(tx)
    db.commit()

    logger.info("Créditos do plano alocados: tenant=%d amount=%d reset=%s",
                tenant_id, amount, reset_date)


def _next_reset_date(from_date: date) -> date:
    """Retorna a mesma data do mês seguinte (data de vencimento + 1 mês)."""
    month = from_date.month + 1
    year = from_date.year
    if month > 12:
        month = 1
        year += 1
    # Ajusta para último dia do mês se necessário
    import calendar
    last_day = calendar.monthrange(year, month)[1]
    day = min(from_date.day, last_day)
    return date(year, month, day)


def reset_credits_for_tenant(tenant_id: int, db: Session) -> bool:
    """
    Executa o reset mensal de créditos para um tenant.
    Chamado pelo ARQ job. Retorna True se resetou.
    """
    from app.db.models.subscription import Subscription, SubscriptionStatus
    from app.db.models.plan import Plan

    sub = db.query(Subscription).filter(
        Subscription.tenant_id == tenant_id,
        Subscription.status.in_([SubscriptionStatus.ACTIVE, SubscriptionStatus.PAST_DUE]),
    ).first()

    if not sub:
        return False

    plan = sub.plan
    allocation = PLAN_CREDITS.get(plan.name if plan else "", 0)
    if allocation <= 0:
        return False

    # Próxima data de reset = current_period_end + 1 mês
    reset_date = None
    if sub.current_period_end:
        reset_date = _next_reset_date(sub.current_period_end.date())
    else:
        reset_date = _next_reset_date(date.today())

    allocate_plan_credits(tenant_id, allocation, reset_date, db)
    return True

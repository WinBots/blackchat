"""
Router de Créditos IA — Blackchat

Endpoints:
  GET  /api/v1/credits/balance         → saldo atual do tenant
  POST /api/v1/credits/purchase        → cria checkout Stripe para compra de créditos
"""
import logging

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.core.auth import get_current_tenant, get_current_user
from app.db.session import get_db
from app.db.models.tenant import Tenant
from app.db.models.user import User
from app.services import credits_service

logger = logging.getLogger(__name__)
router = APIRouter()

PRICE_PER_CREDIT_CENTS = 125  # R$ 1,25
MIN_CREDITS = 10
MAX_CREDITS = 100


# ─── Schemas ──────────────────────────────────────────────────────────────────

class BalanceOut(BaseModel):
    plan_balance: int
    plan_monthly_allocation: int
    plan_reset_date: str | None
    purchased_balance: int
    total: int


class PurchaseIn(BaseModel):
    amount: int = Field(..., ge=MIN_CREDITS, le=MAX_CREDITS,
                        description="Quantidade de créditos (10-100)")


class PurchaseOut(BaseModel):
    checkout_url: str
    amount: int
    price_brl: float


# ─── Endpoints ────────────────────────────────────────────────────────────────

@router.get("/balance", response_model=BalanceOut)
def get_balance(
    tenant: Tenant = Depends(get_current_tenant),
    db: Session = Depends(get_db),
):
    """Retorna saldo de créditos IA do tenant."""
    data = credits_service.get_balance(tenant.id, db)
    return BalanceOut(**data)


@router.post("/purchase", response_model=PurchaseOut)
def purchase_credits(
    body: PurchaseIn,
    user: User = Depends(get_current_user),
    tenant: Tenant = Depends(get_current_tenant),
    db: Session = Depends(get_db),
):
    """
    Cria uma sessão de checkout Stripe para compra de créditos avulsos.
    Mínimo: 10 créditos (R$ 12,50) | Máximo: 100 créditos (R$ 125,00)
    """
    # Valida múltiplo de 10
    if body.amount % 10 != 0:
        raise HTTPException(status_code=422, detail="Quantidade deve ser múltiplo de 10")

    try:
        import stripe as stripe_lib  # type: ignore
    except ImportError:
        raise HTTPException(status_code=500, detail="Stripe SDK não instalado")

    from app.services import stripe_service
    from app.config import get_settings
    from app.api.v1.routers.billing import _ensure_customer

    creds = stripe_service.require_credits_credentials(db)
    settings = get_settings()

    stripe_lib.api_key = creds.secret_key

    unit_amount = body.amount * PRICE_PER_CREDIT_CENTS  # total em centavos
    price_brl = unit_amount / 100

    frontend_url = getattr(settings, "FRONTEND_URL", settings.PUBLIC_BASE_URL).rstrip("/")
    success_url = f"{frontend_url}/settings?tab=Cobran%C3%A7a&credits=success&amount={body.amount}"
    cancel_url  = f"{frontend_url}/settings?tab=Cobran%C3%A7a"

    billing_email = user.email
    customer_id = _ensure_customer(stripe_lib, tenant, billing_email, db)

    try:
        session = stripe_lib.checkout.Session.create(
            mode="payment",
            customer=customer_id,
            line_items=[{
                "price_data": {
                    "currency": "brl",
                    "product_data": {
                        "name": f"Créditos IA Blackchat ({body.amount} créditos)",
                    },
                    "unit_amount": unit_amount,
                },
                "quantity": 1,
            }],
            success_url=success_url,
            cancel_url=cancel_url,
            metadata={
                "app": "blackchatpro",
                "tenant_id": str(tenant.id),
                "credits_amount": str(body.amount),
                "stripe_mode": creds.mode,
                "type": "credits_purchase",
            },
        )
    except Exception as exc:
        logger.error("Stripe checkout credits falhou: %s", exc)
        raise HTTPException(status_code=502, detail="Erro ao criar sessão de pagamento")

    logger.info("Checkout de créditos criado: tenant=%d amount=%d price=R$%.2f",
                tenant.id, body.amount, price_brl)

    return PurchaseOut(
        checkout_url=session.url,
        amount=body.amount,
        price_brl=price_brl,
    )

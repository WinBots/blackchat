from __future__ import annotations

import json
import logging
import math
from datetime import datetime, timezone
from typing import Optional

logger = logging.getLogger(__name__)

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Request
from starlette.requests import ClientDisconnect
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.config import get_settings
from app.core.auth import get_current_tenant, get_current_user
from app.db.session import get_db
from app.db.models import Tenant
from app.db.models.user import User
from app.db.models.tenant_user import TenantUser
from app.db.models.plan import Plan
from app.db.models.subscription import Subscription, SubscriptionStatus
from app.db.models.stripe_webhook_event import StripeWebhookEvent
from app.db.models.stripe_config import StripeConfig
from app.db.models.subscription_history import SubscriptionHistory
from app.services.billing_service import estimate_billing
from app.services import stripe_service
from app.services.email_sender import (
    send_plan_activated_email,
    send_plan_upgraded_email,
    send_subscription_canceled_email,
)
from app.cache.service import invalidate_subscription, invalidate_stripe_config

router = APIRouter()


# ─── Tabela de preços Enterprise ──────────────────────────────────────────────
# (contacts, preco_mensal_brl)
_PRICE_TABLE = [
    (500,       24.50),
    (2_500,    106.31),
    (5_000,    206.27),
    (10_000,   401.65),
    (15_000,   593.80),
    (20_000,   783.93),
    (30_000,  1_160.15),
    (40_000,  1_532.60),
    (50_000,  1_902.32),
    (60_000,  2_269.90),
    (70_000,  2_635.70),
    (80_000,  2_999.97),
    (90_000,  3_362.90),
    (100_000, 3_724.64),
    (120_000, 4_444.35),
    (140_000, 5_160.26),
    (160_000, 5_872.92),
    (180_000, 6_582.79),
    (200_000, 7_290.17),
    (300_000, 10_790.40),
    (400_000, 14_266.69),
    (500_000, 17_726.88),
    (600_000, 21_174.36),
    (700_000, 24_611.56),
    (800_000, 28_040.28),
    (900_000, 31_461.87),
    (1_000_000, 34_877.31),
    (1_200_000, 41_711.85),
    (1_400_000, 48_467.37),
    (1_600_000, 55_198.55),
    (1_800_000, 61_908.60),
    (2_000_000, 68_600.00),
]
_EXCESS_RATE = 34.30      # R$/1K para além de 2M
_ENT_MIN     = 999.00     # Mínimo Enterprise


def calculate_enterprise_price(contacts: int) -> float:
    """Interpola o preço mensal para o volume de contatos informado."""
    if contacts <= 0:
        return _ENT_MIN
    last_c, last_p = _PRICE_TABLE[-1]
    if contacts >= last_c:
        excess = math.ceil((contacts - last_c) / 1000) * _EXCESS_RATE
        return max(last_p + excess, _ENT_MIN)
    first_c, first_p = _PRICE_TABLE[0]
    if contacts <= first_c:
        return max(first_p * (contacts / first_c), _ENT_MIN)
    for i in range(1, len(_PRICE_TABLE)):
        hi_c, hi_p = _PRICE_TABLE[i]
        if contacts <= hi_c:
            lo_c, lo_p = _PRICE_TABLE[i - 1]
            t = (contacts - lo_c) / (hi_c - lo_c)
            price = lo_p + t * (hi_p - lo_p)
            return max(price, _ENT_MIN)
    return max(last_p, _ENT_MIN)


def _get_stripe():
    try:
        import stripe  # type: ignore
        return stripe
    except Exception:
        return None


def _resolve_billing_email(tenant: Tenant, user: User, db: Session) -> str:
    """
    Retorna o melhor email para usar no Stripe Customer.
    Prioridade:
      1. Email do usuário logado (quem está fazendo checkout)
      2. Email do owner do workspace (via tenant_users)
      3. tenant.email (fallback)
    Corrige tenant.email se ainda for @workspace.internal.
    """
    # Preferir email do usuário logado
    email = (user.email or "").strip()
    if email and "@workspace.internal" not in email:
        # Corrigir tenant.email se estiver com placeholder
        if tenant.email and "@workspace.internal" in tenant.email:
            tenant.email = email
            try:
                db.commit()
            except Exception:
                db.rollback()
        return email

    # Fallback: email do owner do workspace
    owner_link = (
        db.query(TenantUser)
        .filter(TenantUser.tenant_id == tenant.id, TenantUser.role == "owner")
        .first()
    )
    if owner_link:
        owner = db.query(User).filter(User.id == owner_link.user_id).first()
        if owner and owner.email and "@workspace.internal" not in owner.email:
            if tenant.email and "@workspace.internal" in tenant.email:
                tenant.email = owner.email
                try:
                    db.commit()
                except Exception:
                    db.rollback()
            return owner.email.strip()

    # Último fallback
    return (tenant.email or "").strip() or None


# ─── Schemas ──────────────────────────────────────────────────────────────────

class CheckoutSessionIn(BaseModel):
    plan_id: int
    interval: str = "monthly"  # "monthly" ou "yearly"


class EnterpriseCheckoutIn(BaseModel):
    contact_count: int   # volume de contatos escolhido pelo usuário


class BillingUrlOut(BaseModel):
    url: str


class BillingStatusOut(BaseModel):
    stripe_configured: bool
    has_customer: bool


class VpmEstimateOut(BaseModel):
    plan_name: str
    active_contacts: int
    thousand_blocks: int
    vpm_price: Optional[float]
    min_monthly: Optional[float]
    calculated_amount: Optional[float]
    minimum_applied: Optional[bool]
    final_amount: Optional[float]
    is_vpm_plan: bool


# ─── Endpoints ────────────────────────────────────────────────────────────────

@router.get("/status", response_model=BillingStatusOut)
def billing_status(
    tenant: Tenant = Depends(get_current_tenant),
    db: Session = Depends(get_db),
):
    stripe = _get_stripe()
    return BillingStatusOut(
        stripe_configured=bool(stripe and stripe_service.is_configured(db)),
        has_customer=bool(getattr(tenant, "stripe_customer_id", None)),
    )


@router.get("/vpm-estimate", response_model=VpmEstimateOut)
def vpm_estimate(
    tenant: Tenant = Depends(get_current_tenant),
    db: Session = Depends(get_db),
):
    """
    Retorna estimativa de billing VPM para o tenant (baseado nos contatos ativos dos últimos 30 dias).
    Útil para exibir no painel de cobrança.
    """
    sub = (
        db.query(Subscription)
        .filter(Subscription.tenant_id == tenant.id)
        .order_by(Subscription.id.desc())
        .first()
    )
    plan = db.query(Plan).filter(Plan.id == sub.plan_id).first() if sub else None

    if not plan:
        raise HTTPException(status_code=404, detail="Plano não encontrado.")

    estimate = estimate_billing(db, tenant.id, plan)

    if estimate is None:
        # Plano Free ou sem VPM
        from app.services.billing_service import count_active_contacts
        return VpmEstimateOut(
            plan_name=plan.name,
            active_contacts=count_active_contacts(db, tenant.id),
            thousand_blocks=0,
            vpm_price=None,
            min_monthly=None,
            calculated_amount=None,
            minimum_applied=None,
            final_amount=None,
            is_vpm_plan=False,
        )

    return VpmEstimateOut(
        plan_name=plan.name,
        active_contacts=estimate["active_contacts"],
        thousand_blocks=estimate["thousand_blocks"],
        vpm_price=estimate["vpm_price"],
        min_monthly=estimate["min_monthly"],
        calculated_amount=estimate["calculated_amount"],
        minimum_applied=estimate["minimum_applied"],
        final_amount=estimate["final_amount"],
        is_vpm_plan=True,
    )


@router.post("/checkout-session", response_model=BillingUrlOut)
def create_checkout_session(
    body: CheckoutSessionIn,
    user: User = Depends(get_current_user),
    tenant: Tenant = Depends(get_current_tenant),
    db: Session = Depends(get_db),
):
    """
    Checkout Pro — utiliza o price_id fixo recorrente mensal configurado pelo superadmin.
    O ambiente (test/live) e as credenciais são resolvidos pelo stripe_service.
    """
    settings = get_settings()
    stripe = _get_stripe()
    if not stripe:
        raise HTTPException(status_code=500, detail="Stripe SDK não está instalado.")

    creds = stripe_service.require_pro_credentials(db)

    plan = db.query(Plan).filter(Plan.id == body.plan_id, Plan.is_active == True).first()  # noqa: E712
    if not plan:
        raise HTTPException(status_code=404, detail="Plano não encontrado.")
    if plan.name == "free":
        raise HTTPException(status_code=400, detail="Plano Free não precisa de checkout.")
    if plan.name == "unlimited":
        raise HTTPException(status_code=400, detail="Use /enterprise-checkout para o plano Enterprise.")

    price_id = creds.pro_price_id  # vem do stripe_config (test ou live)

    stripe.api_key = creds.secret_key

    billing_email = _resolve_billing_email(tenant, user, db)

    customer_id = getattr(tenant, "stripe_customer_id", None)
    if not customer_id:
        try:
            customer = stripe.Customer.create(
                name=tenant.name,
                email=billing_email,
                metadata={"tenant_id": str(tenant.id)},
            )
            customer_id = customer["id"]
            tenant.stripe_customer_id = customer_id
            db.commit()
        except Exception as exc:
            logger.error("Stripe Customer.create falhou: %s", exc)
            raise HTTPException(status_code=502, detail=f"Erro ao criar cliente no Stripe: {exc}")

    frontend_url = getattr(settings, "FRONTEND_URL", settings.PUBLIC_BASE_URL).rstrip("/")
    success_url = f"{frontend_url}/thank-you?plan={plan.display_name}&checkout=success"
    cancel_url  = f"{frontend_url}/settings?tab=Cobran%C3%A7a&billing=cancel"

    try:
        session = stripe.checkout.Session.create(
            mode="subscription",
            customer=customer_id,
            line_items=[{"price": price_id, "quantity": 1}],
            allow_promotion_codes=True,
            success_url=success_url,
            cancel_url=cancel_url,
            metadata={
                "app": "blackchatpro",
                "tenant_id": str(tenant.id),
                "plan_id": str(plan.id),
                "interval": "monthly",
                "stripe_mode": creds.mode,
            },
            subscription_data={
                "metadata": {
                    "app": "blackchatpro",
                    "tenant_id": str(tenant.id),
                    "plan_id": str(plan.id),
                    "stripe_mode": creds.mode,
                }
            },
        )
    except Exception as exc:
        logger.error("Stripe checkout.Session.create (Pro) falhou [mode=%s]: %s", creds.mode, exc)
        raise HTTPException(
            status_code=502,
            detail=f"Erro ao criar sessão de checkout no Stripe ({creds.mode}): {exc}",
        )

    return BillingUrlOut(url=session["url"])


@router.post("/enterprise-checkout", response_model=BillingUrlOut)
def create_enterprise_checkout(
    body: EnterpriseCheckoutIn,
    user: User = Depends(get_current_user),
    tenant: Tenant = Depends(get_current_tenant),
    db: Session = Depends(get_db),
):
    """
    Checkout Enterprise — preço recorrente mensal inline calculado pelo backend.
    Usa o product_id do produto 'BlackChat Enterprise' configurado pelo superadmin.
    O frontend envia apenas a quantidade de contatos; o backend calcula o valor.
    """
    settings = get_settings()
    stripe = _get_stripe()
    if not stripe:
        raise HTTPException(status_code=500, detail="Stripe SDK não está instalado.")

    creds = stripe_service.require_enterprise_credentials(db)

    contact_count = max(body.contact_count, 1)
    monthly_price = calculate_enterprise_price(contact_count)
    unit_amount_cents = int(round(monthly_price * 100))

    stripe.api_key = creds.secret_key

    billing_email = _resolve_billing_email(tenant, user, db)
    logger.info(
        "Enterprise checkout: tenant=%s, mode=%s, contacts=%s, price=R$%.2f, product_id=%s, email=%s",
        tenant.id, creds.mode, contact_count, monthly_price,
        creds.enterprise_product_id, billing_email,
    )

    customer_id = getattr(tenant, "stripe_customer_id", None)
    if not customer_id:
        try:
            customer = stripe.Customer.create(
                name=tenant.name,
                email=billing_email,
                metadata={"tenant_id": str(tenant.id)},
            )
            customer_id = customer["id"]
            tenant.stripe_customer_id = customer_id
            db.commit()
        except Exception as exc:
            logger.error("Stripe Customer.create falhou: %s", exc)
            raise HTTPException(status_code=502, detail=f"Erro ao criar cliente no Stripe: {exc}")

    # Busca o plano Enterprise no banco para gravar plan_id nos metadados
    ent_plan = db.query(Plan).filter(Plan.name == "unlimited", Plan.is_active == True).first()  # noqa: E712
    plan_id_meta = str(ent_plan.id) if ent_plan else "enterprise"

    frontend_url = getattr(settings, "FRONTEND_URL", settings.PUBLIC_BASE_URL).rstrip("/")
    ent_display = ent_plan.display_name if ent_plan else "Enterprise"
    success_url = f"{frontend_url}/thank-you?plan={ent_display}&checkout=success"
    cancel_url  = f"{frontend_url}/settings?tab=Cobran%C3%A7a&billing=cancel"

    # Enterprise: inline/custom recurring monthly usando o product_id configurado.
    # O 'product' garante que a Stripe associa ao produto correto (sem criar novos produtos a cada checkout).
    try:
        session = stripe.checkout.Session.create(
            mode="subscription",
            customer=customer_id,
            line_items=[{
                "price_data": {
                    "currency": "brl",
                    "product": creds.enterprise_product_id,
                    "unit_amount": unit_amount_cents,
                    "recurring": {"interval": "month"},
                },
                "quantity": 1,
            }],
            allow_promotion_codes=True,
            success_url=success_url,
            cancel_url=cancel_url,
            metadata={
                "app": "blackchatpro",
                "tenant_id": str(tenant.id),
                "plan_id": plan_id_meta,
                "interval": "monthly",
                "stripe_mode": creds.mode,
                "enterprise_contacts": str(contact_count),
                "enterprise_price": str(monthly_price),
                "enterprise_product_id": creds.enterprise_product_id,
            },
            subscription_data={
                "metadata": {
                    "app": "blackchatpro",
                    "tenant_id": str(tenant.id),
                    "plan_id": plan_id_meta,
                    "stripe_mode": creds.mode,
                    "enterprise_contacts": str(contact_count),
                    "enterprise_price": str(monthly_price),
                }
            },
        )
    except Exception as exc:
        logger.error("Stripe checkout.Session.create (Enterprise) falhou [mode=%s]: %s", creds.mode, exc)
        raise HTTPException(
            status_code=502,
            detail=f"Erro ao criar sessão de checkout no Stripe ({creds.mode}): {exc}",
        )

    return BillingUrlOut(url=session["url"])


@router.post("/portal-session", response_model=BillingUrlOut)
def create_portal_session(
    tenant: Tenant = Depends(get_current_tenant),
    db: Session = Depends(get_db),
):
    settings = get_settings()
    stripe = _get_stripe()
    if not stripe:
        raise HTTPException(status_code=500, detail="Stripe SDK não está instalado.")

    creds = stripe_service._safe_get_creds(db)
    stripe.api_key = creds.secret_key

    customer_id = getattr(tenant, "stripe_customer_id", None)
    if not customer_id:
        raise HTTPException(status_code=400, detail="Nenhum customer Stripe associado ao tenant.")

    frontend_url = getattr(settings, "FRONTEND_URL", settings.PUBLIC_BASE_URL).rstrip("/")
    return_url = f"{frontend_url}/settings?tab=Cobran%C3%A7a"
    session = stripe.billing_portal.Session.create(customer=customer_id, return_url=return_url)
    return BillingUrlOut(url=session["url"])


# ─── Webhook Stripe (com idempotência) ────────────────────────────────────────

@router.post("/webhook")
async def stripe_webhook(request: Request, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    """
    Webhook Stripe — processa eventos e sincroniza assinatura.

    - Valida assinatura (STRIPE_WEBHOOK_SECRET)
    - Garante idempotência via StripeWebhookEvent
    - Eventos tratados:
        · checkout.session.completed
        · customer.subscription.created/updated/deleted
        · invoice.payment_succeeded
        · invoice.payment_failed
    """
    settings = get_settings()
    stripe = _get_stripe()
    if not stripe:
        raise HTTPException(status_code=500, detail="Stripe SDK não instalado.")

    try:
        payload = await request.body()
    except ClientDisconnect:
        # Stripe fechou a conexão antes do corpo ser lido; retorna 200 para
        # evitar loop de reenvio — o evento será reenviado se necessário.
        logger.warning("[webhook] ClientDisconnect ao ler body — ignorando")
        return {"received": True, "skipped": "client_disconnect"}

    sig_header = request.headers.get("stripe-signature")

    # ── Detecta o modo do evento (test/live) pelo campo livemode no payload ───
    # Isso permite aceitar eventos de ambos os ambientes no mesmo endpoint.
    try:
        raw_event = json.loads(payload.decode("utf-8"))
    except Exception:
        raise HTTPException(status_code=400, detail="Payload inválido.")

    event_livemode = raw_event.get("livemode", False)
    event_mode = "live" if event_livemode else "test"

    # Resolve webhook_secret do ambiente correspondente ao evento
    try:
        cfg = db.query(StripeConfig).filter(StripeConfig.id == 1).first()
        if cfg is None:
            cfg = StripeConfig(id=1, mode_active="test")
        if event_mode == "live":
            webhook_secret = (cfg.live_webhook_secret or "").strip() or None
        else:
            webhook_secret = (cfg.test_webhook_secret or "").strip() or None
    except Exception:
        webhook_secret = None

    # Valida assinatura do webhook
    event = None
    if webhook_secret and sig_header:
        try:
            event = stripe.Webhook.construct_event(payload, sig_header, webhook_secret)
        except Exception:
            raise HTTPException(status_code=400, detail="Webhook signature inválida.")
    else:
        if event_mode == "live":
            raise HTTPException(
                status_code=400,
                detail="Webhook secret LIVE não configurado. Configure em Super Admin → Stripe antes de ativar o modo produção.",
            )
        # Mode test sem secret: aceita sem validação (apenas desenvolvimento)
        logger.warning("[webhook] webhook_secret TEST não configurado — aceitando sem validação (somente em teste)")
        event = raw_event

    stripe_event_id = event.get("id", "")
    event_type = event.get("type", "")

    # ── Idempotência ─────────────────────────────────────────────────────────
    if stripe_event_id:
        existing = db.query(StripeWebhookEvent).filter(
            StripeWebhookEvent.stripe_event_id == stripe_event_id
        ).first()
        if existing and existing.status == "processed":
            return {"received": True, "skipped": True}

        # Registra o evento (ou atualiza se recebido mas não processado)
        if not existing:
            wh_event = StripeWebhookEvent(
                stripe_event_id=stripe_event_id,
                event_type=event_type,
                payload_json=json.dumps(event)[:10000],
                status="received",
                stripe_mode=event_mode,
            )
            db.add(wh_event)
            db.flush()
        else:
            wh_event = existing
    else:
        wh_event = None

    data_object = (event.get("data") or {}).get("object") or {}

    try:
        _process_event(event_type, data_object, db, background_tasks, event_mode)

        if wh_event:
            wh_event.status = "processed"
            wh_event.processed_at = datetime.now(timezone.utc)

    except Exception as e:
        if wh_event:
            wh_event.status = "error"
            wh_event.error_message = str(e)[:500]
        db.commit()
        # Retorna 200 para não fazer Stripe reenviar indefinidamente (logar e monitorar)
        return {"received": True, "error": str(e)}

    db.commit()
    return {"received": True}


def _get_tenant_owner(db: Session, tenant_id: int):
    """Retorna (email, full_name) do primeiro usuário admin do tenant."""
    user = (
        db.query(User)
        .filter(User.tenant_id == tenant_id, User.is_active == True)  # noqa: E712
        .order_by(User.id.asc())
        .first()
    )
    if user:
        return user.email, user.full_name
    return None, None


def _process_event(event_type: str, data_object: dict, db: Session, bg: BackgroundTasks, event_mode: str = "test") -> None:
    """Processa o evento Stripe e atualiza a assinatura local."""

    # ── checkout.session.completed ────────────────────────────────────────────
    if event_type == "checkout.session.completed":
        metadata = data_object.get("metadata") or {}
        # Ignora eventos de outros produtos Stripe na mesma conta
        if metadata.get("app") != "blackchatpro":
            logger.info("[webhook] checkout.session.completed ignorado (app=%s)", metadata.get("app"))
            return
        tenant_id = _safe_int(metadata.get("tenant_id"))
        plan_id   = _safe_int(metadata.get("plan_id"))
        interval  = metadata.get("interval", "monthly")
        sub_id    = data_object.get("subscription")
        logger.info("[webhook] checkout.session.completed tenant_id=%s plan_id=%s sub_id=%s", tenant_id, plan_id, sub_id)
        if tenant_id and sub_id:
            sub = _get_latest_sub(db, tenant_id)
            if sub:
                sub.stripe_subscription_id = str(sub_id)
                plan = None
                if plan_id:
                    plan = db.query(Plan).filter(Plan.id == plan_id).first()
                    if plan:
                        sub.plan_id = plan.id
                        logger.info("[webhook] plan updated to %s", plan.name)
                    else:
                        logger.warning("[webhook] plan_id=%s not found in DB", plan_id)
                else:
                    logger.warning("[webhook] plan_id ausente no metadata")
                # Contatos contratados (Enterprise: salva o volume escolhido no checkout)
                enterprise_contacts = _safe_int(metadata.get("enterprise_contacts"))
                if enterprise_contacts:
                    sub.contracted_contacts = enterprise_contacts
                # Persiste modo Stripe e valor mensal contratado
                stripe_mode_meta = metadata.get("stripe_mode") or data_object.get("livemode_str")
                if stripe_mode_meta:
                    sub.stripe_mode = stripe_mode_meta
                enterprise_price_str = metadata.get("enterprise_price")
                if enterprise_price_str:
                    try:
                        sub.monthly_amount_cents = int(round(float(enterprise_price_str) * 100))
                    except Exception:
                        pass
                # Persiste product_id do Enterprise
                ent_product_id = metadata.get("enterprise_product_id")
                if ent_product_id:
                    sub.stripe_product_id = ent_product_id
                # Ativa a assinatura independente do status anterior
                sub.status = SubscriptionStatus.ACTIVE
                # Invalida cache da subscription deste tenant
                invalidate_subscription(tenant_id)
                # E-mail de plano ativado
                email, full_name = _get_tenant_owner(db, tenant_id)
                logger.info("[webhook] notificando owner: email=%s plan=%s", email, plan.name if plan else None)
                if email and plan:
                    bg.add_task(
                        send_plan_activated_email,
                        to_email=email,
                        full_name=full_name,
                        plan_name=getattr(plan, "display_name", plan.name),
                        interval=interval,
                    )
            else:
                logger.warning("[webhook] nenhuma subscription encontrada para tenant_id=%s", tenant_id)
        else:
            logger.warning("[webhook] checkout.session.completed sem tenant_id ou sub_id")

    # ── customer.subscription.created / updated ───────────────────────────────
    elif event_type in ("customer.subscription.created", "customer.subscription.updated"):
        _sync_subscription_status(data_object, db, bg, event_mode)
        # Invalidar cache após sync
        customer_id_sync = data_object.get("customer")
        if customer_id_sync:
            t = db.query(Tenant).filter(Tenant.stripe_customer_id == str(customer_id_sync)).first()
            if t:
                invalidate_subscription(t.id)

    # ── customer.subscription.deleted ────────────────────────────────────────
    elif event_type == "customer.subscription.deleted":
        stripe_sub_id = data_object.get("id")
        customer_id   = data_object.get("customer")
        if stripe_sub_id:
            sub = db.query(Subscription).filter(
                Subscription.stripe_subscription_id == str(stripe_sub_id)
            ).first()
            if sub:
                # Capturar nome do plano antes de fazer downgrade
                old_plan = db.query(Plan).filter(Plan.id == sub.plan_id).first()
                old_plan_name = getattr(old_plan, "display_name", old_plan.name) if old_plan else ""
                old_status = sub.status.value if hasattr(sub.status, "value") else str(sub.status)

                sub.status     = SubscriptionStatus.CANCELED
                sub.canceled_at = datetime.now(timezone.utc)
                # Downgrade para Free ao cancelar
                free_plan = db.query(Plan).filter(Plan.name == "free").first()
                if free_plan:
                    sub.plan_id = free_plan.id

                # Invalida cache da subscription
                invalidate_subscription(sub.tenant_id)

                # Histórico de cancelamento
                db.add(SubscriptionHistory(
                    subscription_id=sub.id,
                    tenant_id=sub.tenant_id,
                    event_type="cancellation",
                    old_plan_name=old_plan_name,
                    new_plan_name="free",
                    old_status=old_status,
                    new_status="canceled",
                    stripe_mode=event_mode,
                    note=f"Assinatura cancelada pela Stripe ({stripe_sub_id})",
                ))

                # E-mail de cancelamento
                tenant = db.query(Tenant).filter(Tenant.stripe_customer_id == str(customer_id)).first() if customer_id else None
                if tenant:
                    email, full_name = _get_tenant_owner(db, tenant.id)
                    if email:
                        bg.add_task(
                            send_subscription_canceled_email,
                            to_email=email,
                            full_name=full_name,
                            plan_name=old_plan_name,
                        )

    # ── invoice.paid / invoice.payment_succeeded ─────────────────────────────
    elif event_type in ("invoice.paid", "invoice.payment_succeeded"):
        customer_id = data_object.get("customer")
        if customer_id:
            tenant = db.query(Tenant).filter(
                Tenant.stripe_customer_id == str(customer_id)
            ).first()
            if tenant:
                sub = _get_latest_sub(db, tenant.id)
                if sub and sub.status in (SubscriptionStatus.PAST_DUE, SubscriptionStatus.UNPAID):
                    sub.status = SubscriptionStatus.ACTIVE
                    invalidate_subscription(tenant.id)

    # ── invoice.payment_failed ────────────────────────────────────────────────
    elif event_type == "invoice.payment_failed":
        customer_id = data_object.get("customer")
        # Verifica quantas tentativas já foram feitas
        attempt_count = data_object.get("attempt_count", 1)
        if customer_id:
            tenant = db.query(Tenant).filter(
                Tenant.stripe_customer_id == str(customer_id)
            ).first()
            if tenant:
                sub = _get_latest_sub(db, tenant.id)
                if sub:
                    # 1ª falha → past_due (acesso mantido + avisos)
                    # 3+ falhas → unpaid (restringe ações sensíveis)
                    if attempt_count >= 3:
                        sub.status = SubscriptionStatus.UNPAID
                    else:
                        sub.status = SubscriptionStatus.PAST_DUE


def _resolve_plan_from_price(price_id: str, db: Session) -> Optional[Plan]:
    """Resolve o plano local pelo price_id da Stripe (mensal ou anual)."""
    if not price_id:
        return None
    plan = db.query(Plan).filter(Plan.stripe_price_id_monthly == price_id).first()
    if not plan:
        plan = db.query(Plan).filter(Plan.stripe_price_id_yearly == price_id).first()
    return plan


def _sync_subscription_status(data_object: dict, db: Session, bg: BackgroundTasks, event_mode: str = "test") -> None:
    """Sincroniza status e plano da assinatura baseado nos dados do objeto Stripe subscription."""
    stripe_sub_id = data_object.get("id")
    customer_id = data_object.get("customer")
    status = data_object.get("status")

    if not (stripe_sub_id and customer_id):
        return

    # Ignora assinaturas de outros produtos na mesma conta Stripe
    sub_meta = data_object.get("metadata") or {}
    if sub_meta and sub_meta.get("app") not in (None, "", "blackchatpro"):
        logger.info("[webhook] subscription event ignorado (app=%s)", sub_meta.get("app"))
        return

    tenant = db.query(Tenant).filter(Tenant.stripe_customer_id == str(customer_id)).first()
    if not tenant:
        return

    sub = _get_latest_sub(db, tenant.id)
    if not sub:
        return

    sub.stripe_subscription_id = str(stripe_sub_id)

    # Atualiza stripe_mode com o ambiente do evento
    sub.stripe_mode = event_mode

    # Resolver plano + price_id pelo itens da assinatura (cobre upgrade/downgrade via portal)
    try:
        items = ((data_object.get("items") or {}).get("data") or [])
        if items:
            price_id = (items[0].get("price") or {}).get("id")
            if price_id:
                sub.stripe_price_id = price_id  # ← Item 1: persiste price_id usado (PRO)
            resolved_plan = _resolve_plan_from_price(price_id, db)
            if resolved_plan and resolved_plan.id != sub.plan_id:
                # Plano mudou — e-mail de upgrade/downgrade + histórico
                old_plan = db.query(Plan).filter(Plan.id == sub.plan_id).first()
                old_plan_name = getattr(old_plan, "display_name", old_plan.name) if old_plan else ""
                new_plan_name = getattr(resolved_plan, "display_name", resolved_plan.name)

                # Grava histórico de mudança de plano
                db.add(SubscriptionHistory(
                    subscription_id=sub.id,
                    tenant_id=tenant.id,
                    event_type="plan_change",
                    old_plan_name=old_plan_name,
                    new_plan_name=new_plan_name,
                    stripe_mode=event_mode,
                    note=f"Plano alterado via webhook {data_object.get('id', '')}",
                ))

                email, full_name = _get_tenant_owner(db, tenant.id)
                if email:
                    bg.add_task(
                        send_plan_upgraded_email,
                        to_email=email,
                        full_name=full_name,
                        old_plan=old_plan_name,
                        new_plan=new_plan_name,
                    )
                sub.plan_id = resolved_plan.id
    except Exception:
        pass  # Falha silenciosa — plano fica como está

    status_map = {
        "active": SubscriptionStatus.ACTIVE,
        "trialing": SubscriptionStatus.TRIAL,
        "past_due": SubscriptionStatus.PAST_DUE,
        "unpaid": SubscriptionStatus.UNPAID,
        "canceled": SubscriptionStatus.CANCELED,
        "incomplete_expired": SubscriptionStatus.EXPIRED,
    }
    if status in status_map:
        sub.status = status_map[status]

    # Atualiza período corrente
    period_start = data_object.get("current_period_start")
    period_end = data_object.get("current_period_end")
    if period_start:
        sub.current_period_start = datetime.fromtimestamp(period_start, tz=timezone.utc)
    if period_end:
        sub.current_period_end = datetime.fromtimestamp(period_end, tz=timezone.utc)


def _get_latest_sub(db: Session, tenant_id: int) -> Optional[Subscription]:
    return (
        db.query(Subscription)
        .filter(Subscription.tenant_id == tenant_id)
        .order_by(Subscription.id.desc())
        .first()
    )


def _safe_int(val) -> Optional[int]:
    try:
        return int(val) if val is not None else None
    except (ValueError, TypeError):
        return None

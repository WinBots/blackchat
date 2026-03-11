"""
Reseta a assinatura do tenant "Admin Demo" para Free + Trial,
como se o usuário acabasse de ser criado.

O que faz:
  - Assinatura → plano Free, status=trial, 14 dias a partir de agora
  - Zera stripe_subscription_id, stripe_price_id, contracted_contacts, canceled_at
  - Remove stripe_customer_id do Tenant
  - Apaga todos os stripe_webhook_events do sistema (para testes limpos)
  - Apaga billing_snapshots do tenant

Uso:
  python reset_to_free.py
  python reset_to_free.py --email outro@exemplo.com
"""
from __future__ import annotations

import argparse
import sys
from datetime import datetime, timezone, timedelta

from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.db.models.user import User
from app.db.models.tenant import Tenant
from app.db.models.subscription import Subscription, SubscriptionStatus
from app.db.models.plan import Plan
from app.db.models.stripe_webhook_event import StripeWebhookEvent

try:
    from app.db.models.billing_snapshot import BillingSnapshot
    HAS_SNAPSHOT = True
except ImportError:
    HAS_SNAPSHOT = False


def reset(email: str, db: Session) -> None:
    # ── 1. Localizar usuário ──────────────────────────────────────────────────
    user = db.query(User).filter(User.email == email).first()
    if not user:
        print(f"ERRO: usuário com e-mail '{email}' não encontrado.")
        sys.exit(1)

    tenant: Tenant = db.query(Tenant).filter(Tenant.id == user.tenant_id).first()
    if not tenant:
        print(f"ERRO: tenant não encontrado para o usuário.")
        sys.exit(1)

    print(f"Tenant : {tenant.name} (id={tenant.id})")
    print(f"Usuário: {user.full_name} <{user.email}>")

    # ── 2. Plano Free ─────────────────────────────────────────────────────────
    free_plan: Plan = db.query(Plan).filter(Plan.name == "free").first()
    if not free_plan:
        print("ERRO: plano 'free' não encontrado no banco.")
        sys.exit(1)

    # ── 3. Subscription ───────────────────────────────────────────────────────
    subs = (
        db.query(Subscription)
        .filter(Subscription.tenant_id == tenant.id)
        .order_by(Subscription.id.asc())
        .all()
    )

    now = datetime.now(timezone.utc)
    trial_end = now + timedelta(days=14)

    if subs:
        # Mantém a primeira, apaga extras
        sub = subs[0]
        for extra in subs[1:]:
            print(f"  Removendo assinatura extra id={extra.id}")
            db.delete(extra)

        old_plan_id = sub.plan_id
        old_status  = sub.status
        old_stripe  = sub.stripe_subscription_id

        sub.plan_id                = free_plan.id
        sub.status                 = SubscriptionStatus.TRIAL
        sub.started_at             = now
        sub.trial_ends_at          = trial_end
        sub.current_period_start   = now
        sub.current_period_end     = trial_end
        sub.canceled_at            = None
        sub.stripe_subscription_id = None
        sub.stripe_price_id        = None
        sub.contracted_contacts    = None
        sub.current_bots_count     = 0
        sub.current_contacts_count = 0
        sub.active_contacts_count  = 0
        sub.current_messages_count = 0

        print(f"  Assinatura id={sub.id}: {old_status}/{old_plan_id} → trial/free")
        print(f"    stripe_subscription_id apagado: {old_stripe or '(vazio)'}")
    else:
        # Cria uma nova assinatura do zero
        sub = Subscription(
            tenant_id=tenant.id,
            plan_id=free_plan.id,
            status=SubscriptionStatus.TRIAL,
            started_at=now,
            trial_ends_at=trial_end,
            current_period_start=now,
            current_period_end=trial_end,
        )
        db.add(sub)
        print("  Assinatura criada do zero (trial/free).")

    # ── 4. Tenant: limpar Stripe customer ─────────────────────────────────────
    old_cid = tenant.stripe_customer_id
    if old_cid:
        tenant.stripe_customer_id = None
        print(f"  stripe_customer_id removido: {old_cid}")
    else:
        print("  stripe_customer_id já estava vazio.")

    # ── 5. Limpar stripe_webhook_events (todos — ambiente de teste) ───────────
    wh_count = db.query(StripeWebhookEvent).count()
    db.query(StripeWebhookEvent).delete(synchronize_session=False)
    print(f"  stripe_webhook_events apagados: {wh_count}")

    # ── 6. Limpar billing_snapshots do tenant ─────────────────────────────────
    if HAS_SNAPSHOT:
        snap_count = db.query(BillingSnapshot).filter(BillingSnapshot.tenant_id == tenant.id).count()
        db.query(BillingSnapshot).filter(BillingSnapshot.tenant_id == tenant.id).delete(synchronize_session=False)
        print(f"  billing_snapshots apagados: {snap_count}")

    db.commit()

    print()
    print("✓ Reset concluído com sucesso.")
    print(f"  Plano  : Free (trial até {trial_end.strftime('%Y-%m-%d')})")
    print(f"  Status : trial")
    print(f"  Stripe : sem customer, sem subscription")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--email",
        default="admin@blackchatpro.com",
        help="E-mail do usuário a resetar (padrão: admin@blackchatpro.com)",
    )
    args = parser.parse_args()

    db: Session = SessionLocal()
    try:
        reset(args.email, db)
    except SystemExit:
        raise
    except Exception as exc:
        db.rollback()
        print(f"ERRO inesperado: {exc}")
        raise
    finally:
        db.close()

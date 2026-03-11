"""
Backfill contracted_contacts from Stripe checkout session metadata.

Finds all Enterprise subscriptions in the DB where contracted_contacts is NULL,
looks up the Stripe checkout session that created each subscription, reads
enterprise_contacts from its metadata and saves it to the DB.

Usage:
    python backfill_contracted_contacts.py [--dry-run]
"""
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

import argparse

from sqlalchemy.orm import Session

from app.config import get_settings
from app.db.session import SessionLocal
from app.db.models.subscription import Subscription
from app.db.models.plan import Plan
from app.db.models.tenant import Tenant


def _get_stripe():
    try:
        import stripe as _stripe
        return _stripe
    except ImportError:
        print("ERROR: stripe package not installed.")
        sys.exit(1)


def run(dry_run: bool = False):
    settings = get_settings()
    stripe = _get_stripe()
    stripe.api_key = settings.STRIPE_SECRET_KEY

    db: Session = SessionLocal()
    try:
        # All Enterprise subs with stripe_subscription_id but no contracted_contacts yet
        rows = (
            db.query(Subscription, Plan, Tenant)
            .join(Plan, Plan.id == Subscription.plan_id)
            .join(Tenant, Tenant.id == Subscription.tenant_id)
            .filter(
                Plan.name == "unlimited",
                Subscription.stripe_subscription_id.isnot(None),
                Subscription.contracted_contacts.is_(None),
            )
            .all()
        )

        print(f"Found {len(rows)} Enterprise subscription(s) to backfill.")

        for sub, plan, tenant in rows:
            customer_id = getattr(tenant, "stripe_customer_id", None)
            if not customer_id:
                print(f"  SKIP sub_id={sub.id} tenant_id={tenant.id} — no stripe_customer_id")
                continue

            enterprise_contacts = None

            # 1) Try subscription metadata first (populated for new checkouts)
            try:
                stripe_sub = stripe.Subscription.retrieve(sub.stripe_subscription_id)
                meta = stripe_sub.get("metadata") or {}
                if meta.get("enterprise_contacts"):
                    enterprise_contacts = int(meta["enterprise_contacts"])
                    print(f"  sub_id={sub.id}: found {enterprise_contacts} contacts in Stripe subscription metadata")
            except Exception as e:
                print(f"  sub_id={sub.id}: could not retrieve Stripe subscription — {e}")

            # 2) Fallback: scan checkout sessions for this customer
            if not enterprise_contacts:
                try:
                    sessions = stripe.checkout.Session.list(customer=customer_id, limit=100)
                    for session in sessions.auto_paging_iter():
                        if session.get("subscription") == sub.stripe_subscription_id:
                            meta = session.get("metadata") or {}
                            if meta.get("enterprise_contacts"):
                                enterprise_contacts = int(meta["enterprise_contacts"])
                                print(f"  sub_id={sub.id}: found {enterprise_contacts} contacts in checkout session {session['id']}")
                                break
                except Exception as e:
                    print(f"  sub_id={sub.id}: could not list checkout sessions — {e}")

            if enterprise_contacts:
                if dry_run:
                    print(f"  DRY-RUN: would set contracted_contacts={enterprise_contacts} for sub_id={sub.id} tenant={tenant.id}")
                else:
                    sub.contracted_contacts = enterprise_contacts
                    db.commit()
                    print(f"  UPDATED sub_id={sub.id} tenant={tenant.id} -> contracted_contacts={enterprise_contacts}")
            else:
                print(f"  WARNING: sub_id={sub.id} tenant={tenant.id} — could not find enterprise_contacts in Stripe, skipping.")

    finally:
        db.close()

    print("Done.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true", help="Preview without writing to DB")
    args = parser.parse_args()
    run(dry_run=args.dry_run)

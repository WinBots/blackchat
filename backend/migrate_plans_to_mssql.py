"""
Migra plans, subscriptions, billing_snapshots e stripe_webhook_events
do SQLite para SQL Server, preservando IDs (IDENTITY_INSERT).

Uso:
    python migrate_plans_to_mssql.py
"""
import sqlite3
import sys
from pathlib import Path

SQLITE_PATH = Path(__file__).parent / "data" / "app.db"
if not SQLITE_PATH.exists():
    print(f"[ERRO] SQLite não encontrado em: {SQLITE_PATH}")
    sys.exit(1)

sys.path.insert(0, str(Path(__file__).parent))
from app.config import get_settings
from sqlalchemy import create_engine, text

settings = get_settings()
mssql_engine = create_engine(settings.DATABASE_URL)

sqlite_conn = sqlite3.connect(str(SQLITE_PATH))
sqlite_conn.row_factory = sqlite3.Row


def fetch(query):
    return [dict(r) for r in sqlite_conn.execute(query).fetchall()]


def val(v):
    return v if v is not None else None


plans               = fetch("SELECT * FROM plans")
subscriptions       = fetch("SELECT * FROM subscriptions")
billing_snapshots   = fetch("SELECT * FROM billing_snapshots")
stripe_events       = fetch("SELECT * FROM stripe_webhook_events")

print(f"SQLite:")
print(f"  plans:                {len(plans)}")
print(f"  subscriptions:        {len(subscriptions)}")
print(f"  billing_snapshots:    {len(billing_snapshots)}")
print(f"  stripe_webhook_events:{len(stripe_events)}")

with mssql_engine.begin() as conn:

    # ─── PLANS ────────────────────────────────────────────────────────────────
    conn.execute(text("SET IDENTITY_INSERT plans ON"))
    mig, skip = 0, 0
    for p in plans:
        if conn.execute(text("SELECT id FROM plans WHERE id=:id"), {"id": p["id"]}).fetchone():
            skip += 1
            continue
        conn.execute(text("""
            INSERT INTO plans (
                id, name, display_name, description,
                price_monthly, price_yearly,
                vpm_price, min_monthly,
                max_bots, max_contacts, max_messages_per_month,
                max_flows, max_tags, max_sequences,
                has_advanced_flows, has_api_access, has_webhooks,
                has_priority_support, has_whitelabel, has_early_access,
                is_active,
                stripe_price_id_monthly, stripe_price_id_yearly
            ) VALUES (
                :id, :name, :display_name, :description,
                :price_monthly, :price_yearly,
                :vpm_price, :min_monthly,
                :max_bots, :max_contacts, :max_messages_per_month,
                :max_flows, :max_tags, :max_sequences,
                :has_advanced_flows, :has_api_access, :has_webhooks,
                :has_priority_support, :has_whitelabel, :has_early_access,
                :is_active,
                :stripe_price_id_monthly, :stripe_price_id_yearly
            )
        """), {
            "id":                      p["id"],
            "name":                    p["name"],
            "display_name":            p["display_name"],
            "description":             val(p.get("description")),
            "price_monthly":           val(p.get("price_monthly")) or 0,
            "price_yearly":            val(p.get("price_yearly")),
            "vpm_price":               val(p.get("vpm_price")),
            "min_monthly":             val(p.get("min_monthly")),
            "max_bots":                val(p.get("max_bots")),
            "max_contacts":            val(p.get("max_contacts")),
            "max_messages_per_month":  val(p.get("max_messages_per_month")),
            "max_flows":               val(p.get("max_flows")),
            "max_tags":                val(p.get("max_tags")),
            "max_sequences":           val(p.get("max_sequences")),
            "has_advanced_flows":      1 if p.get("has_advanced_flows") else 0,
            "has_api_access":          1 if p.get("has_api_access") else 0,
            "has_webhooks":            1 if p.get("has_webhooks") else 0,
            "has_priority_support":    1 if p.get("has_priority_support") else 0,
            "has_whitelabel":          1 if p.get("has_whitelabel") else 0,
            "has_early_access":        1 if p.get("has_early_access") else 0,
            "is_active":               1 if p.get("is_active") else 0,
            "stripe_price_id_monthly": val(p.get("stripe_price_id_monthly")),
            "stripe_price_id_yearly":  val(p.get("stripe_price_id_yearly")),
        })
        mig += 1
    conn.execute(text("SET IDENTITY_INSERT plans OFF"))
    print(f"\nPlans             → migrados: {mig}, já existiam: {skip}")

    # ─── SUBSCRIPTIONS ────────────────────────────────────────────────────────
    conn.execute(text("SET IDENTITY_INSERT subscriptions ON"))
    mig, skip = 0, 0
    for s in subscriptions:
        if conn.execute(text("SELECT id FROM subscriptions WHERE id=:id"), {"id": s["id"]}).fetchone():
            skip += 1
            continue
        # Verifica FKs
        if not conn.execute(text("SELECT id FROM tenants WHERE id=:id"), {"id": s["tenant_id"]}).fetchone():
            print(f"  [SKIP] subscription id={s['id']} — tenant_id={s['tenant_id']} não existe")
            skip += 1
            continue
        if not conn.execute(text("SELECT id FROM plans WHERE id=:id"), {"id": s["plan_id"]}).fetchone():
            print(f"  [SKIP] subscription id={s['id']} — plan_id={s['plan_id']} não existe")
            skip += 1
            continue

        conn.execute(text("""
            INSERT INTO subscriptions (
                id, tenant_id, plan_id, status,
                started_at, trial_ends_at,
                current_period_start, current_period_end, canceled_at,
                current_bots_count, current_contacts_count,
                active_contacts_count, current_messages_count,
                contracted_contacts,
                stripe_subscription_id, stripe_price_id,
                created_at, updated_at
            ) VALUES (
                :id, :tenant_id, :plan_id, :status,
                :started_at, :trial_ends_at,
                :current_period_start, :current_period_end, :canceled_at,
                :current_bots_count, :current_contacts_count,
                :active_contacts_count, :current_messages_count,
                :contracted_contacts,
                :stripe_subscription_id, :stripe_price_id,
                :created_at, :updated_at
            )
        """), {
            "id":                     s["id"],
            "tenant_id":              s["tenant_id"],
            "plan_id":                s["plan_id"],
            "status":                 s.get("status") or "trial",
            "started_at":             val(s.get("started_at")),
            "trial_ends_at":          val(s.get("trial_ends_at")),
            "current_period_start":   val(s.get("current_period_start")),
            "current_period_end":     val(s.get("current_period_end")),
            "canceled_at":            val(s.get("canceled_at")),
            "current_bots_count":     s.get("current_bots_count") or 0,
            "current_contacts_count": s.get("current_contacts_count") or 0,
            "active_contacts_count":  s.get("active_contacts_count") or 0,
            "current_messages_count": s.get("current_messages_count") or 0,
            "contracted_contacts":    val(s.get("contracted_contacts")),
            "stripe_subscription_id": val(s.get("stripe_subscription_id")),
            "stripe_price_id":        val(s.get("stripe_price_id")),
            "created_at":             val(s.get("created_at")),
            "updated_at":             val(s.get("updated_at")),
        })
        mig += 1
    conn.execute(text("SET IDENTITY_INSERT subscriptions OFF"))
    print(f"Subscriptions     → migrados: {mig}, já existiam: {skip}")

    # ─── BILLING_SNAPSHOTS ────────────────────────────────────────────────────
    if billing_snapshots:
        conn.execute(text("SET IDENTITY_INSERT billing_snapshots ON"))
        mig, skip = 0, 0
        for b in billing_snapshots:
            if conn.execute(text("SELECT id FROM billing_snapshots WHERE id=:id"), {"id": b["id"]}).fetchone():
                skip += 1
                continue
            conn.execute(text("""
                INSERT INTO billing_snapshots (
                    id, tenant_id, plan_id, period_start, period_end,
                    active_contacts_count, thousand_blocks, vpm_value,
                    minimum_applied, final_amount, plan_name, created_at
                ) VALUES (
                    :id, :tenant_id, :plan_id, :period_start, :period_end,
                    :active_contacts_count, :thousand_blocks, :vpm_value,
                    :minimum_applied, :final_amount, :plan_name, :created_at
                )
            """), {
                "id":                    b["id"],
                "tenant_id":             b["tenant_id"],
                "plan_id":               val(b.get("plan_id")),
                "period_start":          val(b.get("period_start")),
                "period_end":            val(b.get("period_end")),
                "active_contacts_count": b.get("active_contacts_count") or 0,
                "thousand_blocks":       b.get("thousand_blocks") or 0,
                "vpm_value":             val(b.get("vpm_value")),
                "minimum_applied":       1 if b.get("minimum_applied") else 0,
                "final_amount":          val(b.get("final_amount")),
                "plan_name":             val(b.get("plan_name")),
                "created_at":            val(b.get("created_at")),
            })
            mig += 1
        conn.execute(text("SET IDENTITY_INSERT billing_snapshots OFF"))
        print(f"BillingSnapshots  → migrados: {mig}, já existiam: {skip}")
    else:
        print("BillingSnapshots  → vazio, nada a migrar")

    # ─── STRIPE_WEBHOOK_EVENTS ────────────────────────────────────────────────
    if stripe_events:
        conn.execute(text("SET IDENTITY_INSERT stripe_webhook_events ON"))
        mig, skip = 0, 0
        for e in stripe_events:
            if conn.execute(text("SELECT id FROM stripe_webhook_events WHERE id=:id"), {"id": e["id"]}).fetchone():
                skip += 1
                continue
            conn.execute(text("""
                INSERT INTO stripe_webhook_events (
                    id, stripe_event_id, event_type,
                    received_at, processed_at, status,
                    payload_json, error_message
                ) VALUES (
                    :id, :stripe_event_id, :event_type,
                    :received_at, :processed_at, :status,
                    :payload_json, :error_message
                )
            """), {
                "id":             e["id"],
                "stripe_event_id": val(e.get("stripe_event_id")),
                "event_type":     val(e.get("event_type")),
                "received_at":    val(e.get("received_at")),
                "processed_at":   val(e.get("processed_at")),
                "status":         val(e.get("status")),
                "payload_json":   val(e.get("payload_json")),
                "error_message":  val(e.get("error_message")),
            })
            mig += 1
        conn.execute(text("SET IDENTITY_INSERT stripe_webhook_events OFF"))
        print(f"StripeWebhookEvts → migrados: {mig}, já existiam: {skip}")
    else:
        print("StripeWebhookEvts → vazio, nada a migrar")

sqlite_conn.close()
print("\n✓ Migração de planos concluída com sucesso!")

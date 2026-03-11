"""
Script de migração direta — aplica novas colunas e reinicia planos.
Execute com: python migrate_plans.py (dentro do diretório backend/)
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import create_engine, text

DB_PATH = "data/app.db"
DATABASE_URL = f"sqlite:///{DB_PATH}"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

def has_column(conn, table, col):
    rows = conn.execute(text(f"PRAGMA table_info({table})")).fetchall()
    return any(r[1] == col for r in rows)

print("=== Aplicando migrações ===")
with engine.begin() as conn:
    # plans — VPM
    for col, ddl in [
        ("vpm_price", "NUMERIC(10,2)"),
        ("min_monthly", "NUMERIC(10,2)"),
        ("max_tags", "INTEGER"),
        ("max_sequences", "INTEGER"),
        ("has_early_access", "BOOLEAN DEFAULT 0"),
    ]:
        if not has_column(conn, "plans", col):
            conn.execute(text(f"ALTER TABLE plans ADD COLUMN {col} {ddl}"))
            print(f"  + plans.{col}")
        else:
            print(f"  = plans.{col} (já existe)")

    # subscriptions
    if not has_column(conn, "subscriptions", "active_contacts_count"):
        conn.execute(text("ALTER TABLE subscriptions ADD COLUMN active_contacts_count INTEGER DEFAULT 0"))
        print("  + subscriptions.active_contacts_count")

    # contacts
    if not has_column(conn, "contacts", "last_interaction_at"):
        conn.execute(text("ALTER TABLE contacts ADD COLUMN last_interaction_at DATETIME"))
        print("  + contacts.last_interaction_at")

    # Cria novas tabelas
    conn.execute(text("""
        CREATE TABLE IF NOT EXISTS billing_snapshots (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tenant_id INTEGER NOT NULL,
            plan_id INTEGER,
            period_start DATETIME NOT NULL,
            period_end DATETIME NOT NULL,
            active_contacts_count INTEGER NOT NULL DEFAULT 0,
            thousand_blocks INTEGER NOT NULL DEFAULT 0,
            vpm_value NUMERIC(10,2),
            minimum_applied BOOLEAN DEFAULT 0,
            final_amount NUMERIC(10,2) NOT NULL DEFAULT 0,
            plan_name VARCHAR(100),
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """))
    print("  ✓ billing_snapshots table OK")

    conn.execute(text("""
        CREATE TABLE IF NOT EXISTS stripe_webhook_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            stripe_event_id VARCHAR(255) NOT NULL UNIQUE,
            event_type VARCHAR(100) NOT NULL,
            received_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            processed_at DATETIME,
            status VARCHAR(50) DEFAULT 'received',
            payload_json TEXT,
            error_message TEXT
        )
    """))
    print("  ✓ stripe_webhook_events table OK")

    conn.execute(text("""
        CREATE TABLE IF NOT EXISTS limit_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tenant_id INTEGER NOT NULL,
            limit_type VARCHAR(50) NOT NULL,
            limit_value INTEGER NOT NULL,
            current_value INTEGER NOT NULL,
            detected_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            status VARCHAR(50) DEFAULT 'warning',
            resolved_at DATETIME
        )
    """))
    print("  ✓ limit_events table OK")

print("\n=== Atualizando planos ===")
with engine.begin() as conn:
    # Desativa planos legados
    conn.execute(text("UPDATE plans SET is_active = 0 WHERE name IN ('basic','professional','enterprise')"))
    print("  - Desativados: basic, professional, enterprise")

    # Free
    row = conn.execute(text("SELECT id FROM plans WHERE name='free'")).fetchone()
    if row:
        conn.execute(text("""
            UPDATE plans SET
                display_name='Free',
                description='Para testar a ferramenta',
                price_monthly=0,
                vpm_price=NULL,
                min_monthly=NULL,
                max_bots=1,
                max_contacts=100,
                max_messages_per_month=NULL,
                max_flows=1,
                max_tags=1,
                max_sequences=1,
                has_advanced_flows=0,
                has_api_access=0,
                has_webhooks=0,
                has_priority_support=0,
                has_whitelabel=0,
                has_early_access=0,
                is_active=1
            WHERE name='free'
        """))
        print("  ~ Free atualizado")
    else:
        conn.execute(text("""
            INSERT INTO plans (name,display_name,description,price_monthly,vpm_price,min_monthly,
                max_bots,max_contacts,max_messages_per_month,max_flows,max_tags,max_sequences,
                has_advanced_flows,has_api_access,has_webhooks,has_priority_support,has_whitelabel,has_early_access,is_active)
            VALUES ('free','Free','Para testar a ferramenta',0,NULL,NULL,1,100,NULL,1,1,1,0,0,0,0,0,0,1)
        """))
        print("  + Free criado")

    # Pro
    row = conn.execute(text("SELECT id FROM plans WHERE name='pro'")).fetchone()
    if row:
        conn.execute(text("""
            UPDATE plans SET
                display_name='Pro',
                description='Para operações em crescimento',
                price_monthly=99,
                vpm_price=49,
                min_monthly=99,
                max_bots=NULL,
                max_contacts=NULL,
                max_messages_per_month=NULL,
                max_flows=NULL,
                max_tags=NULL,
                max_sequences=NULL,
                has_advanced_flows=1,
                has_api_access=0,
                has_webhooks=0,
                has_priority_support=0,
                has_whitelabel=0,
                has_early_access=0,
                is_active=1
            WHERE name='pro'
        """))
        print("  ~ Pro atualizado")
    else:
        conn.execute(text("""
            INSERT INTO plans (name,display_name,description,price_monthly,vpm_price,min_monthly,
                max_bots,max_contacts,max_messages_per_month,max_flows,max_tags,max_sequences,
                has_advanced_flows,has_api_access,has_webhooks,has_priority_support,has_whitelabel,has_early_access,is_active)
            VALUES ('pro','Pro','Para operações em crescimento',99,49,99,NULL,NULL,NULL,NULL,NULL,NULL,1,0,0,0,0,0,1)
        """))
        print("  + Pro criado")

    # Enterprise (antigo Unlimited)
    row = conn.execute(text("SELECT id FROM plans WHERE name='unlimited'")).fetchone()
    if row:
        conn.execute(text("""
            UPDATE plans SET
                display_name='Enterprise',
                description='Para grandes volumes',
                price_monthly=999,
                vpm_price=29,
                min_monthly=999,
                max_bots=NULL,
                max_contacts=NULL,
                max_messages_per_month=NULL,
                max_flows=NULL,
                max_tags=NULL,
                max_sequences=NULL,
                has_advanced_flows=1,
                has_api_access=0,
                has_webhooks=0,
                has_priority_support=1,
                has_whitelabel=0,
                has_early_access=1,
                is_active=1
            WHERE name='unlimited'
        """))
        print("  ~ Enterprise atualizado")
    else:
        conn.execute(text("""
            INSERT INTO plans (name,display_name,description,price_monthly,vpm_price,min_monthly,
                max_bots,max_contacts,max_messages_per_month,max_flows,max_tags,max_sequences,
                has_advanced_flows,has_api_access,has_webhooks,has_priority_support,has_whitelabel,has_early_access,is_active)
            VALUES ('unlimited','Enterprise','Para grandes volumes',999,29,999,NULL,NULL,NULL,NULL,NULL,NULL,1,0,0,1,0,1,1)
        """))
        print("  + Enterprise criado")

print("\n=== Resultado final ===")
with engine.connect() as conn:
    rows = conn.execute(text("SELECT id, name, display_name, price_monthly, vpm_price, min_monthly, is_active FROM plans ORDER BY price_monthly")).fetchall()
    for r in rows:
        status = "✅ ativo" if r[6] else "❌ inativo"
        print(f"  [{r[0]}] {r[2]} ({r[1]}) — R${r[3]} | VPM: R${r[4]}/1k | min: R${r[5]} | {status}")

print("\nMigração concluída!")

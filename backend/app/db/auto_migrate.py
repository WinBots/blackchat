from __future__ import annotations

from sqlalchemy import text


# ─────────────────────────────────────────────────────────────────────────────
# Helpers SQL Server (INFORMATION_SCHEMA — funciona em qualquer schema)
# ─────────────────────────────────────────────────────────────────────────────

def _mssql_has_column(conn, table: str, column: str) -> bool:
    result = conn.execute(
        text(
            "SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS "
            "WHERE TABLE_NAME = :t AND COLUMN_NAME = :c"
        ),
        {"t": table, "c": column},
    ).scalar()
    return int(result or 0) > 0


def _mssql_has_table(conn, table: str) -> bool:
    result = conn.execute(
        text(
            "SELECT COUNT(*) FROM INFORMATION_SCHEMA.TABLES "
            "WHERE TABLE_NAME = :t"
        ),
        {"t": table},
    ).scalar()
    return int(result or 0) > 0


def _mssql_add_column(conn, table: str, column_ddl: str) -> None:
    """ALTER TABLE — sintaxe SQL Server (sem a palavra COLUMN)."""
    conn.execute(text(f"ALTER TABLE {table} ADD {column_ddl}"))


# ─────────────────────────────────────────────────────────────────────────────
# Mapa de colunas a garantir  (table, column, ddl_mssql)
# ─────────────────────────────────────────────────────────────────────────────
# Tipos SQL Server usados:
#   BOOLEAN  → BIT
#   DATETIME → DATETIME2      (maior precisão, timezone-aware)
#   NUMERIC  → NUMERIC        (igual)
#   VARCHAR  → NVARCHAR       (suporte a Unicode)
# ─────────────────────────────────────────────────────────────────────────────

_COLUMNS = [
    # table, column, ddl_mssql
    # ── users ──────────────────────────────────────────────────────────
    ("users", "is_super_admin",
        "is_super_admin BIT"),

    # ── tenants ────────────────────────────────────────────────────────
    ("tenants", "timezone",
        "timezone NVARCHAR(64)"),
    ("tenants", "stripe_customer_id",
        "stripe_customer_id NVARCHAR(255)"),

    # ── plans — campos legados ─────────────────────────────────────────
    ("plans", "stripe_price_id_monthly",
        "stripe_price_id_monthly NVARCHAR(255)"),

    # ── plans — campos VPM ────────────────────────────────────────────
    ("plans", "vpm_price",
        "vpm_price NUMERIC(10,2)"),
    ("plans", "min_monthly",
        "min_monthly NUMERIC(10,2)"),
    ("plans", "max_tags",
        "max_tags INT"),
    ("plans", "max_sequences",
        "max_sequences INT"),
    ("plans", "has_early_access",
        "has_early_access BIT DEFAULT 0"),

    # ── subscriptions ──────────────────────────────────────────────────
    ("subscriptions", "stripe_subscription_id",
        "stripe_subscription_id NVARCHAR(255)"),
    ("subscriptions", "stripe_price_id",
        "stripe_price_id NVARCHAR(255)"),
    ("subscriptions", "active_contacts_count",
        "active_contacts_count INT DEFAULT 0"),

    # ── contacts ───────────────────────────────────────────────────────
    ("contacts", "last_interaction_at",
        "last_interaction_at DATETIME2"),

    # ── subscriptions — campos Stripe estendidos ───────────────────────
    ("subscriptions", "stripe_product_id",
        "stripe_product_id NVARCHAR(255)"),
    ("subscriptions", "stripe_mode",
        "stripe_mode NVARCHAR(10)"),
    ("subscriptions", "monthly_amount_cents",
        "monthly_amount_cents INT"),

    # ── stripe_webhook_events — modo do evento ─────────────────────────
    ("stripe_webhook_events", "stripe_mode",
        "stripe_mode NVARCHAR(10)"),
]

# Tabelas que o auto_migrate garante existem (criadas via SQLAlchemy create_all, mas
# verificamos pois deployments antigos podem não tê-las).
_ENSURE_TABLES_SQL = {
    "stripe_config": """
        IF NOT EXISTS (SELECT 1 FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = 'stripe_config')
        CREATE TABLE stripe_config (
            id INT PRIMARY KEY DEFAULT 1,
            mode_active NVARCHAR(10) NOT NULL DEFAULT 'test',
            test_secret_key NVARCHAR(MAX),
            test_publishable_key NVARCHAR(MAX),
            test_webhook_secret NVARCHAR(MAX),
            test_pro_price_id NVARCHAR(255),
            test_enterprise_product_id NVARCHAR(255),
            live_secret_key NVARCHAR(MAX),
            live_publishable_key NVARCHAR(MAX),
            live_webhook_secret NVARCHAR(MAX),
            live_pro_price_id NVARCHAR(255),
            live_enterprise_product_id NVARCHAR(255),
            updated_at DATETIME2
        );
    """,
    "subscription_history": """
        IF NOT EXISTS (SELECT 1 FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = 'subscription_history')
        CREATE TABLE subscription_history (
            id INT IDENTITY(1,1) PRIMARY KEY,
            subscription_id INT,
            tenant_id INT,
            event_type NVARCHAR(50) NOT NULL,
            old_plan_name NVARCHAR(100),
            new_plan_name NVARCHAR(100),
            old_status NVARCHAR(50),
            new_status NVARCHAR(50),
            stripe_mode NVARCHAR(10),
            note NVARCHAR(500),
            created_at DATETIME2 DEFAULT GETUTCDATE()
        );
    """,
}


# ─────────────────────────────────────────────────────────────────────────────
# Entry point
# ─────────────────────────────────────────────────────────────────────────────

def run_auto_migrations(engine) -> None:
    """Aplica migrações incrementais (ADD COLUMN idempotente) para SQL Server."""

    url = str(getattr(engine, "url", ""))
    is_mssql = "mssql" in url or "sqlserver" in url.lower()

    if not is_mssql:
        return

    with engine.begin() as conn:
        # Garante tabelas extras que podem não ter sido criadas em deploys antigos
        for _tname, _sql in _ENSURE_TABLES_SQL.items():
            try:
                conn.execute(text(_sql))
            except Exception as _exc:
                pass  # já existe ou erro de sintaxe — ignorar silenciosamente

        for table, column, ddl_mssql in _COLUMNS:
            if _mssql_has_table(conn, table) and not _mssql_has_column(conn, table, column):
                _mssql_add_column(conn, table, ddl_mssql)


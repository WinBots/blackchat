from __future__ import annotations

from sqlalchemy import text


# ─────────────────────────────────────────────────────────────────────────────
# Helpers SQLite
# ─────────────────────────────────────────────────────────────────────────────

def _sqlite_has_column(conn, table: str, column: str) -> bool:
    rows = conn.execute(text(f"PRAGMA table_info({table})")).fetchall()
    return any(r[1] == column for r in rows)


def _sqlite_add_column(conn, table: str, column_ddl: str) -> None:
    conn.execute(text(f"ALTER TABLE {table} ADD COLUMN {column_ddl}"))


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
# Mapa de colunas a garantir  (table, column, ddl_sqlite, ddl_mssql)
# ─────────────────────────────────────────────────────────────────────────────
# Tipos SQL Server usados:
#   BOOLEAN  → BIT
#   DATETIME → DATETIME2      (maior precisão, timezone-aware)
#   NUMERIC  → NUMERIC        (igual)
#   VARCHAR  → NVARCHAR       (suporte a Unicode)
# ─────────────────────────────────────────────────────────────────────────────

_COLUMNS = [
    # table, column, ddl_sqlite, ddl_mssql
    # ── users ──────────────────────────────────────────────────────────
    ("users", "is_super_admin",
        "is_super_admin BOOLEAN",
        "is_super_admin BIT"),

    # ── tenants ────────────────────────────────────────────────────────
    ("tenants", "timezone",
        "timezone VARCHAR(64)",
        "timezone NVARCHAR(64)"),
    ("tenants", "stripe_customer_id",
        "stripe_customer_id VARCHAR(255)",
        "stripe_customer_id NVARCHAR(255)"),

    # ── plans — campos legados ─────────────────────────────────────────
    ("plans", "stripe_price_id_monthly",
        "stripe_price_id_monthly VARCHAR(255)",
        "stripe_price_id_monthly NVARCHAR(255)"),

    # ── plans — campos VPM ────────────────────────────────────────────
    ("plans", "vpm_price",
        "vpm_price NUMERIC(10,2)",
        "vpm_price NUMERIC(10,2)"),
    ("plans", "min_monthly",
        "min_monthly NUMERIC(10,2)",
        "min_monthly NUMERIC(10,2)"),
    ("plans", "max_tags",
        "max_tags INTEGER",
        "max_tags INT"),
    ("plans", "max_sequences",
        "max_sequences INTEGER",
        "max_sequences INT"),
    ("plans", "has_early_access",
        "has_early_access BOOLEAN DEFAULT 0",
        "has_early_access BIT DEFAULT 0"),

    # ── subscriptions ──────────────────────────────────────────────────
    ("subscriptions", "stripe_subscription_id",
        "stripe_subscription_id VARCHAR(255)",
        "stripe_subscription_id NVARCHAR(255)"),
    ("subscriptions", "stripe_price_id",
        "stripe_price_id VARCHAR(255)",
        "stripe_price_id NVARCHAR(255)"),
    ("subscriptions", "active_contacts_count",
        "active_contacts_count INTEGER DEFAULT 0",
        "active_contacts_count INT DEFAULT 0"),

    # ── contacts ───────────────────────────────────────────────────────
    ("contacts", "last_interaction_at",
        "last_interaction_at DATETIME",
        "last_interaction_at DATETIME2"),
]


# ─────────────────────────────────────────────────────────────────────────────
# Entry point
# ─────────────────────────────────────────────────────────────────────────────

def run_auto_migrations(engine) -> None:
    """Aplica migrações incrementais (ADD COLUMN idempotente) para SQLite e SQL Server."""

    url = str(getattr(engine, "url", ""))
    is_sqlite = url.startswith("sqlite")
    is_mssql = "mssql" in url or "sqlserver" in url.lower()

    if not (is_sqlite or is_mssql):
        # Para outros bancos (ex.: PostgreSQL), use Alembic.
        return

    with engine.begin() as conn:
        for table, column, ddl_sqlite, ddl_mssql in _COLUMNS:
            if is_sqlite:
                if not _sqlite_has_column(conn, table, column):
                    _sqlite_add_column(conn, table, ddl_sqlite)
            else:  # mssql
                if _mssql_has_table(conn, table) and not _mssql_has_column(conn, table, column):
                    _mssql_add_column(conn, table, ddl_mssql)


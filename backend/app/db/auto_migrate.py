from __future__ import annotations

import logging
from sqlalchemy import text

logger = logging.getLogger(__name__)


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

    # ── tenant_users — multi-workspace ─────────────────────────────────
    ("tenant_users", "is_default",
        "is_default BIT DEFAULT 0"),
    ("tenant_users", "created_at",
        "created_at DATETIME2 DEFAULT GETUTCDATE()"),
    ("tenant_users", "permissions",
        "permissions NVARCHAR(MAX)"),
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

        # ── Multi-workspace: remover UNIQUE constraint de tenants.email ──
        # Permite que múltiplos workspaces usem o mesmo email do owner.
        if _mssql_has_table(conn, "tenants"):
            try:
                # Encontra o nome da constraint UNIQUE no email
                row = conn.execute(text("""
                    SELECT tc.CONSTRAINT_NAME
                    FROM INFORMATION_SCHEMA.TABLE_CONSTRAINTS tc
                    JOIN INFORMATION_SCHEMA.CONSTRAINT_COLUMN_USAGE ccu
                      ON tc.CONSTRAINT_NAME = ccu.CONSTRAINT_NAME
                    WHERE tc.TABLE_NAME = 'tenants'
                      AND ccu.COLUMN_NAME = 'email'
                      AND tc.CONSTRAINT_TYPE = 'UNIQUE'
                """)).fetchone()
                if row:
                    conn.execute(text(f"ALTER TABLE tenants DROP CONSTRAINT {row[0]}"))
            except Exception:
                pass  # já foi removida ou não existia

        # ── Multi-workspace: backfill tenant_users ─────────────────────
        # Para cada user existente que ainda NÃO tem registro em tenant_users,
        # cria um vínculo como "owner" + is_default=1.
        # Isto garante compatibilidade total: usuários existentes continuam
        # acessando seu workspace normalmente.
        if _mssql_has_table(conn, "tenant_users") and _mssql_has_table(conn, "users"):
            try:
                conn.execute(text("""
                    INSERT INTO tenant_users (tenant_id, user_id, role, is_default)
                    SELECT u.tenant_id, u.id, 'owner', 1
                    FROM users u
                    WHERE NOT EXISTS (
                        SELECT 1 FROM tenant_users tu
                        WHERE tu.user_id = u.id AND tu.tenant_id = u.tenant_id
                    )
                """))
            except Exception:
                pass  # constraint violation ou duplicata — seguro ignorar

        # ── Corrigir emails @workspace.internal → email do owner ───────
        if _mssql_has_table(conn, "tenants") and _mssql_has_table(conn, "tenant_users") and _mssql_has_table(conn, "users"):
            try:
                conn.execute(text("""
                    UPDATE t
                    SET t.email = u.email
                    FROM tenants t
                    JOIN tenant_users tu ON tu.tenant_id = t.id AND tu.role = 'owner'
                    JOIN users u ON u.id = tu.user_id
                    WHERE t.email LIKE '%@workspace.internal'
                """))
            except Exception:
                pass

    # ── Performance: criar índices (transação separada por índice) ─────
    _create_performance_indexes(engine)


# ─────────────────────────────────────────────────────────────────────────────
# Índices de performance (idempotente — só cria se não existir)
# ─────────────────────────────────────────────────────────────────────────────

# (index_name, table, columns)
_PERF_INDEXES = [
    # ── Contatos (tabela mais consultada) ──────────────────────────────
    ("ix_contacts_tenant_id",           "contacts",          "tenant_id"),
    ("ix_contacts_tenant_channel",      "contacts",          "tenant_id, default_channel_id"),
    ("ix_contacts_last_interaction",    "contacts",          "tenant_id, last_interaction_at"),

    # ── Mensagens ──────────────────────────────────────────────────────
    ("ix_messages_tenant_id",           "messages",          "tenant_id"),
    ("ix_messages_contact_id",          "messages",          "contact_id"),
    ("ix_messages_tenant_created",      "messages",          "tenant_id, created_at"),
    ("ix_messages_contact_created",     "messages",          "contact_id, created_at"),

    # ── Canais ─────────────────────────────────────────────────────────
    ("ix_channels_tenant_id",           "channels",          "tenant_id"),

    # ── Fluxos ─────────────────────────────────────────────────────────
    ("ix_flows_tenant_id",              "flows",             "tenant_id"),
    ("ix_flow_steps_flow_id",           "flow_steps",        "flow_id"),

    # ── Execuções de fluxo ─────────────────────────────────────────────
    ("ix_flow_exec_tenant_id",          "flow_executions",   "tenant_id"),
    ("ix_flow_exec_contact_id",         "flow_executions",   "contact_id"),
    ("ix_flow_exec_flow_id",            "flow_executions",   "flow_id"),
    ("ix_flow_exec_tenant_status",      "flow_executions",   "tenant_id, status"),

    # ── Logs de execução ───────────────────────────────────────────────
    ("ix_flow_exec_logs_exec_id",       "flow_execution_logs", "flow_execution_id"),

    # ── Contact Tags ───────────────────────────────────────────────────
    ("ix_contact_tags_tenant_id",       "contact_tags",      "tenant_id"),
    ("ix_contact_tags_contact_id",      "contact_tags",      "contact_id"),
    ("ix_contact_tags_tenant_tag",      "contact_tags",      "tenant_id, tag_name"),

    # ── Sequences ──────────────────────────────────────────────────────
    ("ix_sequences_tenant_id",          "sequences",         "tenant_id"),
    ("ix_contact_seq_tenant_id",        "contact_sequences", "tenant_id"),
    ("ix_contact_seq_contact_id",       "contact_sequences", "contact_id"),
    ("ix_contact_seq_sequence_id",      "contact_sequences", "sequence_id"),

    # ── Subscriptions ──────────────────────────────────────────────────
    ("ix_subscriptions_tenant_id",      "subscriptions",     "tenant_id"),

    # ── Subscription History ───────────────────────────────────────────
    ("ix_sub_history_tenant_id",        "subscription_history", "tenant_id"),
    ("ix_sub_history_created",          "subscription_history", "created_at"),

    # ── Billing Snapshots ──────────────────────────────────────────────
    ("ix_billing_snap_tenant_id",       "billing_snapshots", "tenant_id"),

    # ── Limit Events ──────────────────────────────────────────────────
    ("ix_limit_events_tenant_id",       "limit_events",      "tenant_id"),
    ("ix_limit_events_detected",        "limit_events",      "detected_at"),

    # ── Stripe Webhook Events ──────────────────────────────────────────
    ("ix_stripe_wh_events_received",    "stripe_webhook_events", "received_at"),

    # ── Tenant Users (multi-workspace) ─────────────────────────────────
    ("ix_tenant_users_user_id",         "tenant_users",      "user_id"),
    ("ix_tenant_users_tenant_id",       "tenant_users",      "tenant_id"),

    # ── Password Reset Tokens ──────────────────────────────────────────
    ("ix_pw_reset_user_id",             "password_reset_tokens", "user_id"),
]


def _mssql_has_index(conn, index_name: str) -> bool:
    """Verifica se um índice já existe no SQL Server."""
    result = conn.execute(
        text("SELECT COUNT(*) FROM sys.indexes WHERE name = :n"),
        {"n": index_name},
    ).scalar()
    return int(result or 0) > 0


def _create_performance_indexes(engine) -> None:
    """Cria índices de performance. Cada índice em sua própria transação para
    evitar que uma falha cancele todos os outros."""
    created = 0
    skipped = 0
    errors = 0

    for idx_name, table, columns in _PERF_INDEXES:
        try:
            with engine.begin() as conn:
                if not _mssql_has_table(conn, table):
                    skipped += 1
                    continue
                if _mssql_has_index(conn, idx_name):
                    skipped += 1
                    continue
                conn.execute(text(
                    f"CREATE NONCLUSTERED INDEX {idx_name} ON {table} ({columns})"
                ))
                created += 1
                logger.info("Índice criado: %s ON %s(%s)", idx_name, table, columns)
        except Exception as exc:
            errors += 1
            logger.warning("Falha ao criar índice %s: %s", idx_name, exc)

    if created or errors:
        logger.info(
            "Performance indexes: %d criados, %d já existiam, %d erros",
            created, skipped, errors,
        )

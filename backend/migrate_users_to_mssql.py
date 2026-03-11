"""
Migra tenants + users + tenant_users do SQLite para SQL Server.
Mantém os mesmos IDs para preservar a integridade das FKs.

Uso:
    python migrate_users_to_mssql.py
"""
import sqlite3
import sys
from pathlib import Path

# ── Caminho do SQLite ─────────────────────────────────────────────────────────
SQLITE_PATH = Path(__file__).parent / "data" / "app.db"

if not SQLITE_PATH.exists():
    print(f"[ERRO] SQLite não encontrado em: {SQLITE_PATH}")
    sys.exit(1)

# ── Conexão SQL Server via SQLAlchemy (usa .env) ──────────────────────────────
import os, sys
sys.path.insert(0, str(Path(__file__).parent))

from app.config import get_settings
from sqlalchemy import create_engine, text

settings = get_settings()
mssql_engine = create_engine(settings.DATABASE_URL)

# ── Lê dados do SQLite ────────────────────────────────────────────────────────
sqlite_conn = sqlite3.connect(str(SQLITE_PATH))
sqlite_conn.row_factory = sqlite3.Row

def fetch_sqlite(query):
    cur = sqlite_conn.execute(query)
    return [dict(r) for r in cur.fetchall()]

tenants      = fetch_sqlite("SELECT * FROM tenants")
users        = fetch_sqlite("SELECT * FROM users")
tenant_users = fetch_sqlite("SELECT * FROM tenant_users")

print(f"SQLite: {len(tenants)} tenant(s), {len(users)} usuário(s), {len(tenant_users)} tenant_user(s)")

if not tenants and not users:
    print("[AVISO] Nenhum dado encontrado no SQLite. Nada a migrar.")
    sys.exit(0)

# ── Insere no SQL Server ──────────────────────────────────────────────────────
def val(v):
    """Converte None e garante tipos compatíveis."""
    return v if v is not None else None

with mssql_engine.begin() as conn:

    # ── tenants ───────────────────────────────────────────────────────────────
    conn.execute(text("SET IDENTITY_INSERT tenants ON"))
    migrated_tenants = 0
    skipped_tenants  = 0
    for t in tenants:
        existing = conn.execute(
            text("SELECT id FROM tenants WHERE id = :id"), {"id": t["id"]}
        ).fetchone()
        if existing:
            skipped_tenants += 1
            continue
        conn.execute(text("""
            INSERT INTO tenants (id, name, email, is_active, timezone, stripe_customer_id, created_at, updated_at)
            VALUES (:id, :name, :email, :is_active, :timezone, :stripe_customer_id, :created_at, :updated_at)
        """), {
            "id":                 t["id"],
            "name":               t["name"],
            "email":              t["email"],
            "is_active":          1 if t.get("is_active") else 0,
            "timezone":           val(t.get("timezone")),
            "stripe_customer_id": val(t.get("stripe_customer_id")),
            "created_at":         val(t.get("created_at")),
            "updated_at":         val(t.get("updated_at")),
        })
        migrated_tenants += 1
    conn.execute(text("SET IDENTITY_INSERT tenants OFF"))
    print(f"Tenants  → migrados: {migrated_tenants}, já existiam: {skipped_tenants}")

    # ── users ─────────────────────────────────────────────────────────────────
    conn.execute(text("SET IDENTITY_INSERT users ON"))
    migrated_users = 0
    skipped_users  = 0
    for u in users:
        existing = conn.execute(
            text("SELECT id FROM users WHERE id = :id"), {"id": u["id"]}
        ).fetchone()
        if existing:
            skipped_users += 1
            continue

        # Verifica se o tenant existe antes de inserir (FK)
        tenant_ok = conn.execute(
            text("SELECT id FROM tenants WHERE id = :id"), {"id": u["tenant_id"]}
        ).fetchone()
        if not tenant_ok:
            print(f"  [SKIP] user id={u['id']} email={u['email']} — tenant_id={u['tenant_id']} não existe no destino")
            skipped_users += 1
            continue

        conn.execute(text("""
            INSERT INTO users
              (id, tenant_id, email, password_hash, full_name, is_active, is_admin, is_super_admin,
               created_at, updated_at, last_login)
            VALUES
              (:id, :tenant_id, :email, :password_hash, :full_name, :is_active, :is_admin,
               :is_super_admin, :created_at, :updated_at, :last_login)
        """), {
            "id":             u["id"],
            "tenant_id":      u["tenant_id"],
            "email":          u["email"],
            "password_hash":  u["password_hash"],
            "full_name":      u["full_name"],
            "is_active":      1 if u.get("is_active") else 0,
            "is_admin":       1 if u.get("is_admin") else 0,
            "is_super_admin": 1 if u.get("is_super_admin") else 0,
            "created_at":     val(u.get("created_at")),
            "updated_at":     val(u.get("updated_at")),
            "last_login":     val(u.get("last_login")),
        })
        migrated_users += 1
    conn.execute(text("SET IDENTITY_INSERT users OFF"))
    print(f"Users    → migrados: {migrated_users}, já existiam: {skipped_users}")

    # ── tenant_users ──────────────────────────────────────────────────────────
    conn.execute(text("SET IDENTITY_INSERT tenant_users ON"))
    migrated_tu = 0
    skipped_tu  = 0
    for tu in tenant_users:
        existing = conn.execute(
            text("SELECT id FROM tenant_users WHERE id = :id"), {"id": tu["id"]}
        ).fetchone()
        if existing:
            skipped_tu += 1
            continue
        conn.execute(text("""
            INSERT INTO tenant_users (id, tenant_id, user_id, role)
            VALUES (:id, :tenant_id, :user_id, :role)
        """), {
            "id":        tu["id"],
            "tenant_id": tu["tenant_id"],
            "user_id":   tu["user_id"],
            "role":      tu.get("role") or "owner",
        })
        migrated_tu += 1
    conn.execute(text("SET IDENTITY_INSERT tenant_users OFF"))
    print(f"TenantUsers → migrados: {migrated_tu}, já existiam: {skipped_tu}")

sqlite_conn.close()
print("\n✓ Migração concluída com sucesso!")

"""Verifica se o auto_migrate aplicou as migrações multi-workspace."""
from app.db.session import engine
from sqlalchemy import text

with engine.connect() as conn:
    # 1. Colunas em tenant_users
    cols = conn.execute(text(
        "SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS "
        "WHERE TABLE_NAME = 'tenant_users' ORDER BY ORDINAL_POSITION"
    )).fetchall()
    print("=== Colunas em tenant_users ===")
    for c in cols:
        print(f"  - {c[0]}")

    # 2. Total registros
    rows = conn.execute(text("SELECT COUNT(*) FROM tenant_users")).scalar()
    print(f"\n=== Total registros tenant_users: {rows} ===")

    # 3. Total users
    users = conn.execute(text("SELECT COUNT(*) FROM users")).scalar()
    print(f"=== Total users: {users} ===")

    # 4. Users sem registro
    orphans = conn.execute(text(
        "SELECT COUNT(*) FROM users u "
        "WHERE NOT EXISTS ("
        "  SELECT 1 FROM tenant_users tu "
        "  WHERE tu.user_id = u.id AND tu.tenant_id = u.tenant_id"
        ")"
    )).scalar()
    print(f"=== Users sem tenant_users (orfaos): {orphans} ===")

    # 5. Amostra
    sample = conn.execute(text(
        "SELECT TOP 5 id, tenant_id, user_id, role, is_default, created_at FROM tenant_users"
    )).fetchall()
    print("\n=== Amostra tenant_users ===")
    for r in sample:
        print(f"  id={r[0]} tenant={r[1]} user={r[2]} role={r[3]} default={r[4]} created={r[5]}")

    print("\n OK - Migrate verificado!")

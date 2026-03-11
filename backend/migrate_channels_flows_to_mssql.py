"""
Migra channels, flows e flow_steps do SQLite para SQL Server.
Preserva IDs originais (IDENTITY_INSERT).

Uso:
    python migrate_channels_flows_to_mssql.py
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

channels   = fetch("SELECT * FROM channels")
flows      = fetch("SELECT * FROM flows")
flow_steps = fetch("SELECT * FROM flow_steps")

print(f"SQLite: {len(channels)} channel(s), {len(flows)} flow(s), {len(flow_steps)} flow_step(s)\n")

with mssql_engine.begin() as conn:

    # ─── CHANNELS ─────────────────────────────────────────────────────────────
    conn.execute(text("SET IDENTITY_INSERT channels ON"))
    mig, skip = 0, 0
    for c in channels:
        if conn.execute(text("SELECT id FROM channels WHERE id=:id"), {"id": c["id"]}).fetchone():
            skip += 1
            continue
        if not conn.execute(text("SELECT id FROM tenants WHERE id=:id"), {"id": c["tenant_id"]}).fetchone():
            print(f"  [SKIP] channel id={c['id']} — tenant_id={c['tenant_id']} não existe")
            skip += 1
            continue
        conn.execute(text("""
            INSERT INTO channels (id, tenant_id, type, name, config, is_active, created_at)
            VALUES (:id, :tenant_id, :type, :name, :config, :is_active, :created_at)
        """), {
            "id":        c["id"],
            "tenant_id": c["tenant_id"],
            "type":      c["type"],
            "name":      c["name"],
            "config":    val(c.get("config")),
            "is_active": 1 if c.get("is_active") else 0,
            "created_at": val(c.get("created_at")),
        })
        mig += 1
    conn.execute(text("SET IDENTITY_INSERT channels OFF"))
    print(f"Channels   → migrados: {mig}, já existiam: {skip}")

    # ─── FLOWS ────────────────────────────────────────────────────────────────
    conn.execute(text("SET IDENTITY_INSERT flows ON"))
    mig, skip = 0, 0
    for f in flows:
        if conn.execute(text("SELECT id FROM flows WHERE id=:id"), {"id": f["id"]}).fetchone():
            skip += 1
            continue
        if not conn.execute(text("SELECT id FROM tenants WHERE id=:id"), {"id": f["tenant_id"]}).fetchone():
            print(f"  [SKIP] flow id={f['id']} — tenant_id={f['tenant_id']} não existe")
            skip += 1
            continue
        conn.execute(text("""
            INSERT INTO flows
              (id, tenant_id, channel_id, name, description, is_active,
               trigger_type, trigger_config, config, created_at, updated_at)
            VALUES
              (:id, :tenant_id, :channel_id, :name, :description, :is_active,
               :trigger_type, :trigger_config, :config, :created_at, :updated_at)
        """), {
            "id":             f["id"],
            "tenant_id":      f["tenant_id"],
            "channel_id":     val(f.get("channel_id")),
            "name":           f["name"],
            "description":    val(f.get("description")),
            "is_active":      1 if f.get("is_active") else 0,
            "trigger_type":   f.get("trigger_type") or "manual",
            "trigger_config": val(f.get("trigger_config")),
            "config":         val(f.get("config")),
            "created_at":     val(f.get("created_at")),
            "updated_at":     val(f.get("updated_at")),
        })
        mig += 1
    conn.execute(text("SET IDENTITY_INSERT flows OFF"))
    print(f"Flows      → migrados: {mig}, já existiam: {skip}")

    # ─── FLOW_STEPS ───────────────────────────────────────────────────────────
    conn.execute(text("SET IDENTITY_INSERT flow_steps ON"))
    mig, skip = 0, 0
    for s in flow_steps:
        if conn.execute(text("SELECT id FROM flow_steps WHERE id=:id"), {"id": s["id"]}).fetchone():
            skip += 1
            continue
        if not conn.execute(text("SELECT id FROM flows WHERE id=:id"), {"id": s["flow_id"]}).fetchone():
            print(f"  [SKIP] flow_step id={s['id']} — flow_id={s['flow_id']} não existe")
            skip += 1
            continue
        conn.execute(text("""
            INSERT INTO flow_steps (id, flow_id, order_index, type, config)
            VALUES (:id, :flow_id, :order_index, :type, :config)
        """), {
            "id":          s["id"],
            "flow_id":     s["flow_id"],
            "order_index": s["order_index"],
            "type":        s["type"],
            "config":      val(s.get("config")),
        })
        mig += 1
    conn.execute(text("SET IDENTITY_INSERT flow_steps OFF"))
    print(f"FlowSteps  → migrados: {mig}, já existiam: {skip}")

sqlite_conn.close()
print("\n✓ Migração concluída com sucesso!")

"""
Limpa todos os tenants/usuários exceto demo@blackchatpro.com
Execute uma única vez para reset de ambiente de teste.
"""
import sqlite3
import sys

DB = "data/app.db"
KEEP_EMAIL = "demo@blackchatpro.com"

con = sqlite3.connect(DB)
con.execute("PRAGMA foreign_keys = OFF")
cur = con.cursor()

# Tenant a manter
cur.execute("SELECT id FROM tenants WHERE lower(email) = ?", (KEEP_EMAIL.lower(),))
row = cur.fetchone()
if not row:
    print(f"ERRO: tenant '{KEEP_EMAIL}' nao encontrado no DB")
    sys.exit(1)

keep_tenant_id = row[0]
print(f"Mantendo tenant_id={keep_tenant_id} ({KEEP_EMAIL})\n")

# Tenants a deletar
cur.execute("SELECT id, email FROM tenants WHERE id != ?", (keep_tenant_id,))
to_delete = cur.fetchall()
if not to_delete:
    print("Nenhum tenant para deletar. DB ja esta limpo.")
    con.close()
    sys.exit(0)

print(f"Deletando {len(to_delete)} tenant(s):")
for tid, temail in to_delete:
    print(f"  - id={tid}  email={temail}")

del_ids = tuple(r[0] for r in to_delete)
ph = lambda ids: ','.join('?' * len(ids))


def query_ids(table, col, ids):
    if not ids:
        return ()
    cur.execute(f"SELECT id FROM {table} WHERE {col} IN ({ph(ids)})", ids)
    return tuple(r[0] for r in cur.fetchall())


def delete_if(table, col, ids):
    if not ids:
        print(f"  {table:<30} 0 linhas")
        return
    cur.execute(f"DELETE FROM {table} WHERE {col} IN ({ph(ids)})", ids)
    print(f"  {table:<30} {cur.rowcount} linhas removidas")


# Reunir IDs relacionados
ch_ids      = query_ids("channels",        "tenant_id", del_ids)
contact_ids = query_ids("contacts",        "channel_id", ch_ids)
flow_ids    = query_ids("flows",           "tenant_id", del_ids)
exec_ids    = query_ids("flow_executions", "flow_id",   flow_ids)

print("\nDeletando (ordem FK-safe):")
delete_if("flow_execution_logs", "flow_execution_id", exec_ids)
delete_if("flow_executions",     "flow_id",           flow_ids)
if contact_ids:
    delete_if("flow_executions", "contact_id",        contact_ids)
delete_if("messages",            "contact_id",        contact_ids)
delete_if("contact_sequences",   "contact_id",        contact_ids)
delete_if("contact_tags",        "contact_id",        contact_ids)
delete_if("contacts",            "channel_id",        ch_ids)
delete_if("flow_steps",          "flow_id",           flow_ids)
delete_if("flows",               "tenant_id",         del_ids)
delete_if("sequences",           "tenant_id",         del_ids)
delete_if("channels",            "tenant_id",         del_ids)
delete_if("limit_events",        "tenant_id",         del_ids)
delete_if("billing_snapshots",   "tenant_id",         del_ids)
delete_if("subscriptions",       "tenant_id",         del_ids)
delete_if("tenant_users",        "tenant_id",         del_ids)

user_ids = query_ids("users", "tenant_id", del_ids)
delete_if("users",    "id",          user_ids)
delete_if("tenants",  "id",          del_ids)

con.commit()
con.close()
print("\nFeito! DB limpo.")

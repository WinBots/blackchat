"""
Limpa dados de contatos e interações para iniciar testes limpos.

Tabelas APAGADAS:
  - flow_execution_logs  (logs de execução de fluxo por contato)
  - flow_executions      (execuções de fluxo por contato)
  - contact_sequences    (contatos matriculados em sequências)
  - contact_tags         (tags dos contatos)
  - messages             (mensagens trocadas)
  - contacts             (contatos)
  - billing_snapshots    (snapshots de faturamento)
  - limit_events         (eventos de limite atingido)
  - stripe_webhook_events (eventos do webhook Stripe)

Tabelas PRESERVADAS:
  - users / tenant_users
  - tenants
  - plans / subscriptions
  - channels  (configuração dos bots)
  - flows / flow_steps
  - sequences (definições de sequência)
  - password_reset_tokens

Uso:
    python clean_for_tests.py [--confirm]
"""
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

import argparse
from sqlalchemy import text
from app.db.session import engine

TABLES_TO_CLEAN = [
    "flow_execution_logs",
    "flow_executions",
    "contact_sequences",
    "contact_tags",
    "messages",
    "contacts",
    "billing_snapshots",
    "limit_events",
    "stripe_webhook_events",
]


def run(confirm: bool = False):
    if not confirm:
        print("=== PRÉVIA — nenhum dado será apagado ===")
        with engine.connect() as conn:
            for table in TABLES_TO_CLEAN:
                try:
                    count = conn.execute(text(f"SELECT COUNT(*) FROM {table}")).scalar()
                    print(f"  {table}: {count} registro(s)")
                except Exception as e:
                    print(f"  {table}: ERRO — {e}")
        print()
        print("Para confirmar e apagar, execute:")
        print("  python clean_for_tests.py --confirm")
        return

    print("=== LIMPANDO banco de dados ===")
    with engine.begin() as conn:
        # Desativa FK constraints no SQLite para permitir DELETE em qualquer ordem
        conn.execute(text("PRAGMA foreign_keys = OFF"))
        for table in TABLES_TO_CLEAN:
            try:
                result = conn.execute(text(f"DELETE FROM {table}"))
                print(f"  ✔ {table}: {result.rowcount} registro(s) removido(s)")
            except Exception as e:
                print(f"  ✘ {table}: ERRO — {e}")
        conn.execute(text("PRAGMA foreign_keys = ON"))

    print()
    print("Banco limpo. Fluxos, usuários, canais, planos e assinaturas foram preservados.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--confirm", action="store_true", help="Confirma e executa a limpeza")
    args = parser.parse_args()
    run(confirm=args.confirm)

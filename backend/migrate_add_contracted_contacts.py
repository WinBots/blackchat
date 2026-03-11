"""
Migration: add contracted_contacts column to subscriptions table.

Usage:
    python migrate_add_contracted_contacts.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

from sqlalchemy import text
from app.db.session import engine


def run():
    with engine.begin() as conn:
        # SQLite / PostgreSQL compatible check
        result = conn.execute(
            text("SELECT COUNT(*) FROM pragma_table_info('subscriptions') WHERE name='contracted_contacts'")
        ).scalar()
        if result:
            print("Column 'contracted_contacts' already exists — skipping.")
            return

        conn.execute(
            text("ALTER TABLE subscriptions ADD COLUMN contracted_contacts INTEGER")
        )
        print("Column 'contracted_contacts' added to subscriptions table.")


if __name__ == "__main__":
    run()

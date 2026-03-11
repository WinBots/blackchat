#!/usr/bin/env python3
"""
Migration: Adicionar suporte para Actions (Custom Fields, Tags, Sequences)
Executa:
    python migrate_add_actions_support.py
"""
import sys
import os

# Adicionar o diretório raiz ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.db.session import engine, SessionLocal
from app.db.models import Contact, ContactTag, Sequence, ContactSequence
from sqlalchemy import text, inspect
import json

def check_column_exists(table_name: str, column_name: str) -> bool:
    """Verifica se uma coluna existe em uma tabela"""
    inspector = inspect(engine)
    columns = [col['name'] for col in inspector.get_columns(table_name)]
    return column_name in columns

def check_table_exists(table_name: str) -> bool:
    """Verifica se uma tabela existe"""
    inspector = inspect(engine)
    return table_name in inspector.get_table_names()

def migrate():
    """Executa a migration"""
    db = SessionLocal()
    
    try:
        print("=" * 80)
        print("MIGRATION: Suporte para Actions")
        print("=" * 80)
        
        # 1. Adicionar custom_fields ao Contact
        print("\n[1] Adicionando coluna custom_fields na tabela contacts...")
        if not check_column_exists('contacts', 'custom_fields'):
            db.execute(text("""
                ALTER TABLE contacts 
                ADD COLUMN custom_fields TEXT DEFAULT '{}' NOT NULL
            """))
            db.commit()
            print("   [OK] Coluna custom_fields adicionada")
        else:
            print("   [INFO] Coluna custom_fields ja existe")
        
        # 2. Criar tabela contact_tags
        print("\n[2] Criando tabela contact_tags...")
        if not check_table_exists('contact_tags'):
            db.execute(text("""
                CREATE TABLE contact_tags (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    tenant_id INTEGER NOT NULL,
                    contact_id INTEGER NOT NULL,
                    tag_name VARCHAR(100) NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (tenant_id) REFERENCES tenants(id),
                    FOREIGN KEY (contact_id) REFERENCES contacts(id) ON DELETE CASCADE
                )
            """))
            db.execute(text("""
                CREATE UNIQUE INDEX idx_contact_tag_unique 
                ON contact_tags(contact_id, tag_name)
            """))
            db.execute(text("""
                CREATE INDEX idx_tenant_tag 
                ON contact_tags(tenant_id, tag_name)
            """))
            db.execute(text("""
                CREATE INDEX idx_contact_tags_contact_id 
                ON contact_tags(contact_id)
            """))
            db.commit()
            print("   [OK] Tabela contact_tags criada com indices")
        else:
            print("   [INFO] Tabela contact_tags ja existe")
        
        # 3. Criar tabela sequences
        print("\n[3] Criando tabela sequences...")
        if not check_table_exists('sequences'):
            db.execute(text("""
                CREATE TABLE sequences (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    tenant_id INTEGER NOT NULL,
                    name VARCHAR(100) NOT NULL,
                    description TEXT,
                    is_active BOOLEAN DEFAULT 1 NOT NULL,
                    steps TEXT DEFAULT '[]' NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (tenant_id) REFERENCES tenants(id)
                )
            """))
            db.execute(text("""
                CREATE INDEX idx_sequences_tenant_name 
                ON sequences(tenant_id, name)
            """))
            db.commit()
            print("   [OK] Tabela sequences criada")
        else:
            print("   [INFO] Tabela sequences ja existe")
        
        # 4. Criar tabela contact_sequences
        print("\n[4] Criando tabela contact_sequences...")
        if not check_table_exists('contact_sequences'):
            db.execute(text("""
                CREATE TABLE contact_sequences (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    tenant_id INTEGER NOT NULL,
                    contact_id INTEGER NOT NULL,
                    sequence_id INTEGER NOT NULL,
                    status VARCHAR(20) DEFAULT 'active' NOT NULL,
                    current_step INTEGER DEFAULT 0 NOT NULL,
                    next_execution_at TIMESTAMP,
                    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    completed_at TIMESTAMP,
                    FOREIGN KEY (tenant_id) REFERENCES tenants(id),
                    FOREIGN KEY (contact_id) REFERENCES contacts(id) ON DELETE CASCADE,
                    FOREIGN KEY (sequence_id) REFERENCES sequences(id) ON DELETE CASCADE
                )
            """))
            db.execute(text("""
                CREATE INDEX idx_contact_sequences_contact 
                ON contact_sequences(contact_id)
            """))
            db.execute(text("""
                CREATE INDEX idx_contact_sequences_status 
                ON contact_sequences(status, next_execution_at)
            """))
            db.commit()
            print("   [OK] Tabela contact_sequences criada")
        else:
            print("   [INFO] Tabela contact_sequences ja existe")
        
        print("\n" + "=" * 80)
        print("MIGRATION CONCLUIDA COM SUCESSO!")
        print("=" * 80)
        print("\nEstruturas criadas:")
        print("   - contacts.custom_fields (JSON)")
        print("   - contact_tags (tabela)")
        print("   - sequences (tabela)")
        print("   - contact_sequences (tabela)")
        print("\nAgora voce pode usar:")
        print("   - Set Custom Field")
        print("   - Add/Remove Tag")
        print("   - Start/Stop Sequence")
        print()
        
    except Exception as e:
        print(f"\n[ERRO] na migration: {str(e)}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    migrate()

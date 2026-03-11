"""
Script para limpar todas as tabelas do banco de dados, exceto usuários (tenants e tenant_users).
"""
import sys
from pathlib import Path
from sqlalchemy import create_engine, text

# Adicionar o diretório backend ao path
sys.path.insert(0, str(Path(__file__).parent))

from app.config import Settings

def clean_database():
    settings = Settings()
    engine = create_engine(settings.DATABASE_URL)
    
    print("🗑️ Limpando banco de dados...")
    print(f"📁 Database: {settings.DATABASE_URL}")
    print()
    
    # Tabelas a serem limpadas (mantendo apenas tenants e tenant_users)
    tables_to_clean = [
        'flow_executions',
        'flow_steps',
        'flows',
        'messages',
        'contacts',
        'sequences',
        'tags',
        'channels',
        'subscriptions',
        'plans',
    ]
    
    with engine.connect() as conn:
        # Desabilitar foreign keys temporariamente (SQLite)
        conn.execute(text("PRAGMA foreign_keys = OFF"))
        conn.commit()
        
        for table in tables_to_clean:
            try:
                result = conn.execute(text(f"DELETE FROM {table}"))
                deleted = result.rowcount
                conn.commit()
                print(f"✅ {table}: {deleted} registros removidos")
            except Exception as e:
                print(f"⚠️ {table}: {str(e)}")
        
        # Reabilitar foreign keys
        conn.execute(text("PRAGMA foreign_keys = ON"))
        conn.commit()
    
    print()
    print("✨ Limpeza concluída! Usuários (tenants e tenant_users) foram mantidos.")

if __name__ == "__main__":
    # Se passou --confirm como argumento, não pede confirmação
    if "--confirm" in sys.argv:
        clean_database()
    else:
        confirm = input("⚠️ Tem certeza que deseja limpar o banco de dados? (sim/não): ")
        if confirm.lower() in ['sim', 's', 'yes', 'y']:
            clean_database()
        else:
            print("❌ Operação cancelada.")

"""
Adiciona campos de estado na tabela flow_executions para suportar fluxos assíncronos
"""
import sqlite3

db_path = "data/winchat.db"

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

try:
    # Verificar colunas existentes
    cursor.execute("PRAGMA table_info(flow_executions)")
    columns = {col[1]: col for col in cursor.fetchall()}
    
    # Adicionar current_step_id
    if 'current_step_id' not in columns:
        print("Adicionando coluna current_step_id...")
        cursor.execute("ALTER TABLE flow_executions ADD COLUMN current_step_id INTEGER")
        print("✓ current_step_id adicionada")
    else:
        print("✓ current_step_id já existe")
    
    # Adicionar context
    if 'context' not in columns:
        print("Adicionando coluna context...")
        cursor.execute("ALTER TABLE flow_executions ADD COLUMN context TEXT")
        print("✓ context adicionada")
    else:
        print("✓ context já existe")
    
    # Adicionar updated_at
    if 'updated_at' not in columns:
        print("Adicionando coluna updated_at...")
        cursor.execute("ALTER TABLE flow_executions ADD COLUMN updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP")
        print("✓ updated_at adicionada")
    else:
        print("✓ updated_at já existe")
    
    conn.commit()
    print("\n✅ Migração concluída com sucesso!")
    
except Exception as e:
    print(f"\n❌ Erro na migração: {e}")
    conn.rollback()
finally:
    conn.close()

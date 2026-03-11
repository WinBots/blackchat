"""
Adiciona tabela de logs e campos de rastreamento para debugging completo de fluxos
"""
import sqlite3
import os

# Conectar ao banco
db_path = os.path.join(os.path.dirname(__file__), "data", "app.db")
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

print("🔧 Iniciando migração de rastreamento...")

try:
    # 1. Criar tabela flow_execution_logs
    print("\n1️⃣ Criando tabela flow_execution_logs...")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS flow_execution_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            flow_execution_id INTEGER NOT NULL,
            step_id INTEGER,
            log_type VARCHAR(50) NOT NULL,
            description TEXT,
            data TEXT,
            error_message TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (flow_execution_id) REFERENCES flow_executions (id) ON DELETE CASCADE,
            FOREIGN KEY (step_id) REFERENCES flow_steps (id)
        )
    """)
    
    # Criar índices para performance
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_logs_execution ON flow_execution_logs(flow_execution_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_logs_type ON flow_execution_logs(log_type)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_logs_created ON flow_execution_logs(created_at)")
    print("✅ Tabela flow_execution_logs criada")
    
    # 2. Adicionar campos à tabela messages
    print("\n2️⃣ Adicionando campos de rastreamento à tabela messages...")
    
    # Verificar se os campos já existem
    cursor.execute("PRAGMA table_info(messages)")
    columns = [col[1] for col in cursor.fetchall()]
    
    if 'flow_execution_id' not in columns:
        cursor.execute("ALTER TABLE messages ADD COLUMN flow_execution_id INTEGER")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_messages_execution ON messages(flow_execution_id)")
        print("✅ Campo flow_execution_id adicionado")
    else:
        print("⏭️ Campo flow_execution_id já existe")
    
    if 'step_id' not in columns:
        cursor.execute("ALTER TABLE messages ADD COLUMN step_id INTEGER")
        print("✅ Campo step_id adicionado")
    else:
        print("⏭️ Campo step_id já existe")
    
    # Commit das mudanças
    conn.commit()
    print("\n✅ Migração concluída com sucesso!")
    print("\n📊 Estrutura atualizada:")
    print("   • flow_execution_logs: rastreia cada passo da execução")
    print("   • messages.flow_execution_id: vincula mensagens à execução")
    print("   • messages.step_id: vincula mensagens ao step específico")
    
except Exception as e:
    conn.rollback()
    print(f"\n❌ Erro na migração: {e}")
    raise
finally:
    conn.close()

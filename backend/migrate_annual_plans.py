import sys
from pathlib import Path
from sqlalchemy import text

# Add the project root to the Python path
backend_dir = Path(__file__).parent.resolve()
sys.path.append(str(backend_dir))

from app.db.session import SessionLocal

def migrate():
    print("Iniciando migração de planos anuais...")
    db = SessionLocal()
    try:
        print("1. Adicionando novas colunas na tabela plans...")
        
        # Cria as colunas ignorando erros caso já existam (SQLite)
        statements = [
            "ALTER TABLE plans ADD COLUMN price_yearly NUMERIC(10, 2);",
            "ALTER TABLE plans ADD COLUMN stripe_price_id_yearly VARCHAR(255);"
        ]
        
        for statement in statements:
            try:
                db.execute(text(statement))
                db.commit()
                print(f"  [OK] Coluna adicionada via: {statement}")
            except Exception as e:
                db.rollback()
                if "duplicate column name" in str(e).lower():
                    print(f"  [SKIP] Coluna já existe.")
                else:
                    print(f"  [ERRO] Falha ao adicionar coluna: {e}")
                    raise e
                    
        print("2. Atualizando base de testes com os novos planos e IDs do Stripe...")
        
        # Chama a função _seed_plans que já está atualizada com os novos valores
        from app.api.v1.routers.plans import _seed_plans
        _seed_plans(db)
        
        print("  [OK] Planos canônicos atualizados (Free, Pro, Enterprise).")
        print("Migração concluída com sucesso!")
        
    except Exception as e:
        db.rollback()
        print(f"Erro durante a migração: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    migrate()

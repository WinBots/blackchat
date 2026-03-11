"""
Script para reativar canais inativos
"""
import sys
import os
from pathlib import Path

# Adicionar o diretório raiz ao path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))
os.chdir(backend_dir)

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.config import get_settings
from app.db.models.channel import Channel

def reactivate_channels():
    """Reativa todos os canais inativos"""
    settings = get_settings()
    engine = create_engine(settings.DATABASE_URL)
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()
    
    try:
        print("\n" + "="*80)
        print("REATIVANDO CANAIS INATIVOS")
        print("="*80 + "\n")
        
        # Buscar canais inativos
        inactive_channels = db.query(Channel).filter(Channel.is_active == False).all()
        
        if not inactive_channels:
            print("Nenhum canal inativo encontrado!")
            return
        
        print(f"Encontrados {len(inactive_channels)} canais inativos:\n")
        
        # Reativar cada um
        for channel in inactive_channels:
            print(f"[--] Reativando: {channel.name} (ID: {channel.id})")
            channel.is_active = True
        
        # Salvar no banco
        db.commit()
        
        print("\n" + "="*80)
        print(f"[OK] {len(inactive_channels)} canais reativados com sucesso!")
        print("="*80 + "\n")
        
        # Verificar resultado
        all_channels = db.query(Channel).all()
        ativos = len([c for c in all_channels if c.is_active])
        print(f"Status atual: {ativos}/{len(all_channels)} canais ativos\n")
        
    except Exception as e:
        print(f"\nERRO: {e}")
        db.rollback()
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    reactivate_channels()

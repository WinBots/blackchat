"""
Script para verificar status dos canais no banco de dados
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
import json

def check_channels():
    """Verifica todos os canais no banco de dados"""
    settings = get_settings()
    engine = create_engine(settings.DATABASE_URL)
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()
    
    try:
        print("\n" + "="*80)
        print("VERIFICACAO DE CANAIS NO BANCO DE DADOS")
        print("="*80 + "\n")
        
        # Buscar todos os canais
        channels = db.query(Channel).all()
        
        if not channels:
            print("NENHUM CANAL ENCONTRADO no banco de dados!")
            print("\nSugestao: Conecte um bot do Telegram nas configuracoes")
            return
        
        print(f"Total de canais: {len(channels)}\n")
        
        # Estatísticas
        total = len(channels)
        ativos = len([c for c in channels if c.is_active])
        inativos = total - ativos
        telegram = len([c for c in channels if c.type == 'telegram'])
        
        print("ESTATISTICAS:")
        print(f"   Total: {total}")
        print(f"   [OK] Ativos: {ativos}")
        print(f"   [--] Inativos: {inativos}")
        print(f"   Telegram: {telegram}")
        print(f"   Outros: {total - telegram}")
        print("\n" + "-"*80 + "\n")
        
        # Listar cada canal
        for idx, channel in enumerate(channels, 1):
            status = "[OK]" if channel.is_active else "[--]"
            tipo = "Telegram" if channel.type == 'telegram' else channel.type.upper()
            
            print(f"{status} Canal #{idx} ({tipo})")
            print(f"   ID: {channel.id}")
            print(f"   Nome: {channel.name}")
            print(f"   Tipo: {channel.type}")
            print(f"   Status: {'ATIVO' if channel.is_active else 'INATIVO'}")
            print(f"   Tenant ID: {channel.tenant_id}")
            
            # Mostrar config se for Telegram
            if channel.type == 'telegram' and channel.config:
                try:
                    config = json.loads(channel.config)
                    username = config.get('bot_username', 'nao configurado')
                    token = config.get('bot_token', '')
                    webhook = config.get('webhook_url', 'nao configurado')
                    
                    print(f"   Bot Username: @{username}")
                    print(f"   Bot Token: {token[:20]}...") if token else print("   Bot Token: [vazio]")
                    print(f"   Webhook URL: {webhook[:60]}...")
                except Exception as e:
                    print(f"   Config: [Erro ao parsear: {e}]")
            
            print()
        
        print("="*80)
        print("Verificacao concluida!")
        print("="*80 + "\n")
        
    except Exception as e:
        print(f"\nERRO: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    check_channels()

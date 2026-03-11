#!/usr/bin/env python3
"""
Script para atualizar a URL do webhook no banco e re-registrar no Telegram
Útil quando o ngrok muda de URL
"""
import sys
import os
from pathlib import Path
import requests
import json

# Adicionar o diretório raiz ao path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))
os.chdir(backend_dir)

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.config import get_settings
from app.db.models.channel import Channel

def print_status(status, message):
    """Imprime status com ícone"""
    icons = {'ok': '✅', 'warning': '⚠️', 'error': '❌', 'info': 'ℹ️'}
    print(f"{icons.get(status, '')} {message}")

def register_webhook(bot_token, webhook_url, secret_token=None):
    """Registra o webhook no Telegram"""
    try:
        api_url = f"https://api.telegram.org/bot{bot_token}/setWebhook"
        payload = {
            "url": webhook_url,
            "allowed_updates": ["message", "callback_query"],
            "drop_pending_updates": True
        }
        if secret_token:
            payload["secret_token"] = secret_token
        
        response = requests.post(api_url, json=payload, timeout=10)
        data = response.json()
        
        return data.get('ok'), data.get('description', 'Erro desconhecido')
    except Exception as e:
        return False, str(e)

def main():
    if len(sys.argv) != 2:
        print("="*80)
        print(" 🔄 ATUALIZAR URL DO WEBHOOK")
        print("="*80)
        print("\nUso: python update_webhook_url.py <NOVA_URL_NGROK>")
        print("\nExemplo:")
        print('  python update_webhook_url.py https://abc123.ngrok-free.app')
        print("\nO script irá:")
        print("  1. Atualizar a URL do webhook no banco de dados")
        print("  2. Re-registrar o webhook no Telegram")
        print("  3. Limpar mensagens pendentes")
        print("\n💡 Dica: Execute 'ngrok http 8061' e copie a URL HTTPS")
        return
    
    new_ngrok_url = sys.argv[1].rstrip('/')
    
    print("="*80)
    print(" 🔄 ATUALIZAR URL DO WEBHOOK")
    print("="*80)
    print(f"\nNova URL base: {new_ngrok_url}\n")
    
    settings = get_settings()
    engine = create_engine(settings.DATABASE_URL)
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()
    
    try:
        # Buscar canais Telegram ativos
        channels = db.query(Channel).filter(
            Channel.type == 'telegram',
            Channel.is_active == True
        ).all()
        
        if not channels:
            print_status('error', "Nenhum canal Telegram ativo encontrado!")
            return
        
        for idx, channel in enumerate(channels, 1):
            print(f"\n{'='*80}")
            print(f" 📱 Canal #{idx}: {channel.name}")
            print(f"{'='*80}\n")
            
            try:
                config = json.loads(channel.config) if channel.config else {}
            except:
                print_status('error', "Erro ao ler configuração")
                continue
            
            bot_token = config.get('bot_token')
            webhook_secret = config.get('webhook_secret')
            old_webhook_url = config.get('webhook_url', '')
            
            if not bot_token:
                print_status('error', "Bot token não encontrado")
                continue
            
            if not webhook_secret:
                print_status('error', "Webhook secret não encontrado")
                continue
            
            # Construir nova URL do webhook
            new_webhook_url = f"{new_ngrok_url}/api/v1/webhooks/telegram/{webhook_secret}"
            
            print(f"URL antiga: {old_webhook_url[:60]}...")
            print(f"URL nova:   {new_webhook_url[:60]}...\n")
            
            # Atualizar no banco de dados
            print("1️⃣ Atualizando no banco de dados...")
            config['webhook_url'] = new_webhook_url
            channel.config = json.dumps(config)
            db.commit()
            print_status('ok', "Banco de dados atualizado")
            
            # Re-registrar webhook no Telegram
            print("\n2️⃣ Re-registrando webhook no Telegram...")
            success, message = register_webhook(bot_token, new_webhook_url, webhook_secret)
            
            if success:
                print_status('ok', f"Webhook registrado com sucesso!")
                print(f"   {message}")
                
                print("\n✨ Tudo pronto! Teste enviando uma mensagem:")
                print(f"   👉 https://t.me/{config.get('bot_username', 'seu_bot')}")
                print(f"   Digite: /start")
                print("\n🔍 Verifique os logs do backend para ver as mensagens chegando")
            else:
                print_status('error', f"Falha ao registrar webhook: {message}")
                print("\n💡 Possíveis causas:")
                print("   - Backend não está rodando na porta 8061")
                print("   - ngrok não está rodando")
                print("   - URL incorreta")
                
                # Reverter mudança no banco
                config['webhook_url'] = old_webhook_url
                channel.config = json.dumps(config)
                db.commit()
                print_status('warning', "URL revertida no banco de dados")
    
    except Exception as e:
        print_status('error', f"Erro inesperado: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    main()

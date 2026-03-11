#!/usr/bin/env python3
"""
Script para re-registrar webhook automaticamente
Usa informações do banco de dados e atualiza o webhook no Telegram
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
    icons = {
        'ok': '✅',
        'warning': '⚠️',
        'error': '❌',
        'info': 'ℹ️'
    }
    print(f"{icons.get(status, '')} {message}")

def register_webhook(bot_token, webhook_url, secret_token=None):
    """Registra o webhook no Telegram"""
    try:
        api_url = f"https://api.telegram.org/bot{bot_token}/setWebhook"
        
        payload = {
            "url": webhook_url,
            "allowed_updates": ["message", "callback_query"],
            "drop_pending_updates": True  # Limpa mensagens pendentes antigas
        }
        
        if secret_token:
            payload["secret_token"] = secret_token
        
        response = requests.post(api_url, json=payload, timeout=10)
        data = response.json()
        
        if data.get('ok'):
            return True, data.get('description', 'Webhook registrado')
        else:
            return False, data.get('description', 'Erro desconhecido')
    
    except Exception as e:
        return False, str(e)

def get_webhook_info(bot_token):
    """Obtém informações do webhook atual"""
    try:
        url = f"https://api.telegram.org/bot{bot_token}/getWebhookInfo"
        response = requests.get(url, timeout=10)
        data = response.json()
        
        if data.get('ok'):
            return data['result'], None
        return None, data.get('description', 'Erro desconhecido')
    
    except Exception as e:
        return None, str(e)

def main():
    print("="*80)
    print(" 🔄 RE-REGISTRAR WEBHOOK DO TELEGRAM")
    print("="*80)
    
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
        
        print(f"\n{len(channels)} canal(is) encontrado(s)\n")
        
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
            webhook_url = config.get('webhook_url')
            webhook_secret = config.get('webhook_secret')
            bot_username = config.get('bot_username')
            
            if not bot_token:
                print_status('error', "Bot token não encontrado")
                continue
            
            if not webhook_url:
                print_status('error', "Webhook URL não configurada")
                continue
            
            print(f"Bot: @{bot_username}")
            print(f"Webhook: {webhook_url[:60]}...")
            
            # Verificar status atual
            print("\n1️⃣ Verificando status atual do webhook...")
            info, error = get_webhook_info(bot_token)
            
            if error:
                print_status('error', f"Erro ao verificar: {error}")
                continue
            
            current_url = info.get('url', '')
            pending = info.get('pending_update_count', 0)
            last_error = info.get('last_error_message', '')
            
            print(f"   URL atual: {current_url or 'Não configurado'}")
            print(f"   Pendentes: {pending}")
            if last_error:
                print(f"   Último erro: {last_error}")
            
            # Re-registrar webhook
            print("\n2️⃣ Re-registrando webhook...")
            success, message = register_webhook(bot_token, webhook_url, webhook_secret)
            
            if success:
                print_status('ok', f"Webhook registrado com sucesso!")
                print(f"   {message}")
                
                # Verificar novamente
                print("\n3️⃣ Verificando novo status...")
                new_info, error = get_webhook_info(bot_token)
                
                if not error:
                    new_pending = new_info.get('pending_update_count', 0)
                    print(f"   URL: {new_info.get('url', '')[:60]}...")
                    print(f"   Pendentes: {new_pending}")
                    
                    if new_pending == 0:
                        print_status('ok', "Mensagens pendentes limpas!")
                    
                print("\n✨ Tudo pronto! Teste enviando uma mensagem:")
                print(f"   👉 https://t.me/{bot_username}")
                print(f"   Digite: /start")
            else:
                print_status('error', f"Falha ao registrar webhook: {message}")
                print("\n💡 Possíveis causas:")
                print("   - Backend não está rodando")
                print("   - URL não é acessível publicamente")
                print("   - Problema com ngrok/túnel")
    
    except Exception as e:
        print_status('error', f"Erro inesperado: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    main()

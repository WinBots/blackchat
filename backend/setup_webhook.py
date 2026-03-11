#!/usr/bin/env python3
"""Script para registrar o webhook do bot no Telegram"""

import httpx
import sys

def setup_webhook(bot_token: str, webhook_url: str):
    """Registra o webhook no Telegram"""
    
    telegram_api = f"https://api.telegram.org/bot{bot_token}/setWebhook"
    
    print(f"🔧 Registrando webhook no Telegram...")
    print(f"   Bot Token: {bot_token[:10]}...{bot_token[-5:]}")
    print(f"   Webhook URL: {webhook_url}")
    
    try:
        response = httpx.post(
            telegram_api,
            json={"url": webhook_url},
            timeout=10.0
        )
        
        result = response.json()
        
        if result.get("ok"):
            print(f"\n✅ Webhook registrado com sucesso!")
            print(f"   Descrição: {result.get('description', 'OK')}")
        else:
            print(f"\n❌ Erro ao registrar webhook:")
            print(f"   {result.get('description', 'Erro desconhecido')}")
            
    except Exception as e:
        print(f"\n❌ Erro na requisição: {e}")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Uso: python setup_webhook.py <BOT_TOKEN> <WEBHOOK_URL>")
        print("\nExemplo:")
        print('  python setup_webhook.py "123456:ABC-DEF..." "https://abc123.ngrok.io/api/v1/webhooks/telegram/430b..."')
        sys.exit(1)
    
    bot_token = sys.argv[1]
    webhook_url = sys.argv[2]
    
    setup_webhook(bot_token, webhook_url)


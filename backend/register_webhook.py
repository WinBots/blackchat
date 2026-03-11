#!/usr/bin/env python3
"""Script para registrar webhook no Telegram"""
import httpx
import sys

def register_webhook(bot_token, webhook_url):
    """Registra o webhook no Telegram"""
    
    api_url = f"https://api.telegram.org/bot{bot_token}/setWebhook"
    
    print("=" * 60)
    print("🔧 Registrando Webhook no Telegram")
    print("=" * 60)
    print(f"\n📍 Bot Token: {bot_token[:15]}...{bot_token[-5:]}")
    print(f"🔗 Webhook URL: {webhook_url}")
    
    try:
        response = httpx.post(
            api_url,
            json={"url": webhook_url},
            timeout=10.0
        )
        
        result = response.json()
        
        print(f"\n📊 Resposta do Telegram:")
        print(f"   Status: {'✅ OK' if result.get('ok') else '❌ ERRO'}")
        print(f"   Descrição: {result.get('description', 'N/A')}")
        
        if result.get('ok'):
            print(f"\n✅ Webhook registrado com sucesso!")
            print(f"\n💡 Agora envie uma mensagem no Telegram e veja os logs do backend!")
        else:
            print(f"\n❌ Erro ao registrar webhook!")
            print(f"   Verifique se a URL está acessível publicamente")
    
    except Exception as e:
        print(f"\n❌ Erro na requisição: {e}")
    
    print("=" * 60)

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Uso: python register_webhook.py <BOT_TOKEN> <WEBHOOK_URL>")
        print("\nExemplo:")
        print('python register_webhook.py "123456:ABC-DEF..." "https://abc.ngrok-free.app/api/v1/webhooks/telegram/430b..."')
        sys.exit(1)
    
    bot_token = sys.argv[1]
    webhook_url = sys.argv[2]
    
    register_webhook(bot_token, webhook_url)


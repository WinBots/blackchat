"""
Atualiza o PUBLIC_BASE_URL no .env E registra o webhook no Telegram.

Uso:
  python update_webhook.py https://NOVA-URL.ngrok-free.app
"""
import sys
import json
import re
import sqlite3
import httpx

def main():
    if len(sys.argv) < 2:
        print("Uso: python update_webhook.py https://NOVA-URL.ngrok-free.app")
        sys.exit(1)

    new_url = sys.argv[1].rstrip("/")

    # 1. Atualizar .env
    env_path = ".env"
    with open(env_path, "r", encoding="utf-8") as f:
        content = f.read()

    content = re.sub(
        r"^PUBLIC_BASE_URL=.*$",
        f"PUBLIC_BASE_URL={new_url}",
        content,
        flags=re.MULTILINE
    )

    with open(env_path, "w", encoding="utf-8") as f:
        f.write(content)

    print(f"✅ .env atualizado: PUBLIC_BASE_URL={new_url}")

    # 2. Buscar bot_token e webhook_secret do banco
    db_path = "data/app.db"
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute("SELECT config FROM channels WHERE type='telegram' LIMIT 1")
    row = c.fetchone()
    conn.close()

    if not row:
        print("❌ Nenhum canal Telegram encontrado no banco.")
        sys.exit(1)

    cfg = json.loads(row[0])
    bot_token = cfg.get("bot_token", "")
    webhook_secret = cfg.get("webhook_secret", "")

    if not bot_token or not webhook_secret:
        print("❌ bot_token ou webhook_secret não encontrados no canal.")
        sys.exit(1)

    # 3. Registrar webhook no Telegram
    webhook_url = f"{new_url}/api/v1/webhooks/telegram/{webhook_secret}"
    r = httpx.post(
        f"https://api.telegram.org/bot{bot_token}/setWebhook",
        json={
            "url": webhook_url,
            "allowed_updates": ["message", "callback_query"],
            "drop_pending_updates": True
        },
        timeout=10
    )
    result = r.json()

    if result.get("ok"):
        print(f"✅ Webhook registrado no Telegram: {webhook_url}")
    else:
        print(f"❌ Erro ao registrar webhook: {result}")
        sys.exit(1)

    # 4. Confirmar
    r2 = httpx.get(f"https://api.telegram.org/bot{bot_token}/getWebhookInfo", timeout=10)
    info = r2.json().get("result", {})
    print(f"\n📡 Status final:")
    print(f"   URL      : {info.get('url')}")
    print(f"   Pendentes: {info.get('pending_update_count', 0)}")
    print(f"   Erro     : {info.get('last_error_message', 'nenhum')}")

if __name__ == "__main__":
    main()

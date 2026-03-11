import sys, json, urllib.request, urllib.parse
sys.path.insert(0, '.')
from app.db.session import SessionLocal
from app.db.models.channel import Channel
from app.config import get_settings

db = SessionLocal()
settings = get_settings()
base_url = settings.PUBLIC_BASE_URL.rstrip('/')

channels = db.query(Channel).filter(Channel.type == 'telegram', Channel.is_active == True).all()
print(f'Registrando webhook para {len(channels)} canal(is) com base_url={base_url}')

for ch in channels:
    cfg = json.loads(ch.config) if ch.config else {}
    token = cfg.get('bot_token', '')
    secret = cfg.get('webhook_secret', '')
    if not token or not secret:
        print(f'  SKIP canal_id={ch.id} — sem token ou secret')
        continue

    webhook_url = f'{base_url}/api/v1/webhooks/telegram/{secret}'
    payload = json.dumps({'url': webhook_url}).encode()
    req = urllib.request.Request(
        f'https://api.telegram.org/bot{token}/setWebhook',
        data=payload,
        headers={'Content-Type': 'application/json'},
        method='POST'
    )
    resp = json.loads(urllib.request.urlopen(req, timeout=10).read())
    ok = resp.get('result') or resp.get('ok')
    print(f'  canal_id={ch.id} ({ch.name}): {"OK" if ok else "ERRO"} → {webhook_url}')
    print(f'    response: {resp}')

db.close()

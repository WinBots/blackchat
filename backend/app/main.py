from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import get_settings

from app.api.v1.routers import (
    auth, tenants, channels, flows, contacts, events, 
    telegram, instagram, instagram_connect, media, admin, public, debug, dev_tools, dashboard,
    plans, subscription, billing
)
from app.db.session import Base, engine
from app.db.auto_migrate import run_auto_migrations

run_auto_migrations(engine)

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Blackchat Pro SaaS API", version="0.2.0")

_settings = get_settings()
_ALLOWED_ORIGINS = [
    # Produção
    "https://blackchatpro.com",
    "https://www.blackchatpro.com",
    # Dev local
    "http://localhost:3061",
    "http://127.0.0.1:3061",
]
# Em ambiente local também aceita a FRONTEND_URL configurada no .env (ex.: ngrok do frontend)
if _settings.FRONTEND_URL and _settings.FRONTEND_URL not in _ALLOWED_ORIGINS:
    _ALLOWED_ORIGINS.append(_settings.FRONTEND_URL.rstrip("/"))

app.add_middleware(
    CORSMiddleware,
    allow_origins=_ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(public.router, prefix="/api/v1/public", tags=["public"])
app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(admin.router, prefix="/api/v1/admin", tags=["admin"])
app.include_router(tenants.router, prefix="/api/v1/tenants", tags=["tenants"])
app.include_router(channels.router, prefix="/api/v1/channels", tags=["channels"])
app.include_router(flows.router, prefix="/api/v1/flows", tags=["flows"])
app.include_router(contacts.router, prefix="/api/v1/contacts", tags=["contacts"])
app.include_router(plans.router, prefix="/api/v1/plans", tags=["plans"])
app.include_router(subscription.router, prefix="/api/v1/subscription", tags=["subscription"])
app.include_router(billing.router, prefix="/api/v1/billing", tags=["billing"])
app.include_router(dashboard.router, prefix="/api/v1/dashboard", tags=["dashboard"])
app.include_router(events.router, prefix="/api/v1/events", tags=["events"])
app.include_router(media.router, prefix="/api/v1/media", tags=["media"])
app.include_router(telegram.router, prefix="/api/v1/webhooks/telegram", tags=["telegram-webhooks"])
app.include_router(instagram.router, prefix="/api/v1/webhooks/instagram", tags=["instagram-webhooks"])
app.include_router(instagram_connect.router, prefix="/api/v1/instagram", tags=["instagram-connect"])
app.include_router(debug.router, prefix="/api/v1/debug", tags=["debug"])
app.include_router(dev_tools.router, prefix="/api/v1", tags=["dev-tools"])


@app.get("/")
def read_root():
    return {"message": "API Blackchat Pro rodando v0.2.0"}

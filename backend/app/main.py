import threading
import time

from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from uvicorn.middleware.proxy_headers import ProxyHeadersMiddleware
from app.config import get_settings

from app.api.v1.routers import (
    auth, tenants, channels, flows, contacts, events,
    telegram, instagram, instagram_connect, media, admin, public, debug, dev_tools, dashboard,
    plans, subscription, billing, workspaces, integrations, credits
)
from app.api.v1.routers.stripe_config import router as stripe_config_router
from app.core.auth import require_permission
from app.db.session import Base, engine
from app.db.auto_migrate import run_auto_migrations

run_auto_migrations(engine)

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Blackchat Pro SaaS API", version="0.2.0")

# Trusted proxy headers — faz o uvicorn respeitar X-Forwarded-Proto (https)
# enviado pelo Nginx, evitando redirects com http:// em produção
app.add_middleware(ProxyHeadersMiddleware, trusted_hosts="*")

_settings = get_settings()
_ALLOWED_ORIGINS = [
    # Produção
    "https://app.blackchatpro.com",
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
app.include_router(stripe_config_router, prefix="/api/v1/admin", tags=["admin-stripe"])
app.include_router(tenants.router, prefix="/api/v1/tenants", tags=["tenants"],
                   dependencies=[Depends(require_permission("settings"))])
app.include_router(channels.router, prefix="/api/v1/channels", tags=["channels"],
                   dependencies=[Depends(require_permission("channels"))])
app.include_router(flows.router, prefix="/api/v1/flows", tags=["flows"],
                   dependencies=[Depends(require_permission("flows"))])
app.include_router(contacts.router, prefix="/api/v1/contacts", tags=["contacts"],
                   dependencies=[Depends(require_permission("contacts"))])
app.include_router(plans.router, prefix="/api/v1/plans", tags=["plans"])
app.include_router(subscription.router, prefix="/api/v1/subscription", tags=["subscription"])
app.include_router(billing.router, prefix="/api/v1/billing", tags=["billing"])
app.include_router(workspaces.router, prefix="/api/v1/workspaces", tags=["workspaces"])
app.include_router(dashboard.router, prefix="/api/v1/dashboard", tags=["dashboard"],
                   dependencies=[Depends(require_permission("dashboard"))])
app.include_router(events.router, prefix="/api/v1/events", tags=["events"])
app.include_router(media.router, prefix="/api/v1/media", tags=["media"])
app.include_router(telegram.router, prefix="/api/v1/webhooks/telegram", tags=["telegram-webhooks"])
app.include_router(instagram.router, prefix="/api/v1/webhooks/instagram", tags=["instagram-webhooks"])
app.include_router(instagram_connect.router, prefix="/api/v1/instagram", tags=["instagram-connect"],
                   dependencies=[Depends(require_permission("channels"))])
app.include_router(debug.router, prefix="/api/v1/debug", tags=["debug"])
app.include_router(dev_tools.router, prefix="/api/v1", tags=["dev-tools"])
app.include_router(integrations.router, prefix="/api/v1/integrations", tags=["integrations"])
app.include_router(credits.router, prefix="/api/v1/credits", tags=["credits"])


@app.on_event("startup")
async def startup_arq_pool():
    """Inicializa o pool ARQ para enfileirar jobs. Falha graciosamente se Redis offline."""
    from app.workers.arq_pool import create_arq_pool
    await create_arq_pool()


@app.on_event("shutdown")
async def shutdown_arq_pool():
    """Fecha o pool ARQ no shutdown da API."""
    from app.workers.arq_pool import close_arq_pool
    await close_arq_pool()


def _timeout_checker_loop():
    """Thread daemon que verifica execuções com timeout a cada 60 segundos."""
    time.sleep(10)  # aguarda o servidor inicializar completamente
    while True:
        try:
            from app.api.v1.routers.telegram import check_timed_out_executions
            check_timed_out_executions()
        except Exception as e:
            pass  # nunca deixa a thread morrer
        time.sleep(60)


@app.on_event("startup")
def startup_event():
    t = threading.Thread(target=_timeout_checker_loop, daemon=True, name="timeout-checker")
    t.start()


@app.get("/")
def read_root():
    return {"message": "API Blackchat Pro rodando v0.2.0"}


@app.get("/api/health")
def health_check():
    """Healthcheck geral — útil para monitoramento externo (UptimeRobot, etc)."""
    from app.cache.redis_client import cache_health
    redis_status = cache_health()
    return {
        "status": "ok",
        "version": "0.2.0",
        "redis": redis_status,
    }

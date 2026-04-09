from functools import lru_cache
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


_BACKEND_ROOT = Path(__file__).resolve().parents[1]
_ENV_FILE = _BACKEND_ROOT / ".env"


class Settings(BaseSettings):
    ENVIRONMENT: str = "local"
    DEBUG: bool = True

    APP_NAME: str = "Blackchat Pro"
    APP_HOST: str = "127.0.0.1"
    APP_PORT: int = 8061

    # SQL Server (obrigatório):
    # mssql+pyodbc://USER:PASSWORD@HOST:1433/DBNAME?driver=ODBC+Driver+17+for+SQL+Server
    DATABASE_URL: str = ""

    # Autenticação
    JWT_SECRET_KEY: str = "9f4c2e7a1b8d6f3c0a5e9b7d1c4f8a2e6b3d0c7f1a9e5d2c8b4f6a0e3d7c1b5"
    SECRET_KEY: str = "4b7e1c9f3a6d2e8b0f5c1a7d9e3b6f2c8a4d0e7f1b5c9a3d6e2f8b1c7a4d9e0"  # Alias para compatibilidade
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    # APIs Externas
    TELEGRAM_API_BASE: str = "https://api.telegram.org"
    PUBLIC_BASE_URL: str = "http://localhost:8061"   # URL pública do backend (ngrok em dev)
    FRONTEND_URL: str = "http://localhost:3061"       # URL do frontend Vue
            
    # Uploads
    UPLOAD_DIR: Path = Path("uploads")

    # Stripe
    STRIPE_SECRET_KEY: str = ""
    STRIPE_WEBHOOK_SECRET: str = ""

    # Stripe — Price IDs (produção/live e dev/test)
    # Para planos de preço fixo (ex.: Pro). Em produção, *sempre* use IDs do modo Live.
    STRIPE_PRO_PRICE_ID_MONTHLY: str = ""
    STRIPE_PRO_PRICE_ID_YEARLY: str = ""

    # IA (Claude / Anthropic)
    ANTHROPIC_API_KEY: str = ""

    # Redis (cache — opcional; se indisponível o sistema continua via banco)
    REDIS_URL: str = "redis://127.0.0.1:6379/0"

    # Email (SMTP) - ex: Titan/HostGator
    SMTP_HOST: str = ""
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    SMTP_FROM_EMAIL: str = ""
    SMTP_FROM_NAME: str = "Blackchat Pro"
    SMTP_USE_TLS: bool = True  # STARTTLS (geralmente porta 587)
    SMTP_USE_SSL: bool = False  # SSL direto (geralmente porta 465)
    SMTP_ENABLED: bool = True

    # Use caminho absoluto do .env do backend para evitar depender do cwd
    model_config = SettingsConfigDict(env_file=str(_ENV_FILE), env_file_encoding="utf-8", extra="allow")
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        db_url = str(self.DATABASE_URL or "").strip()
        if not db_url:
            raise ValueError("DATABASE_URL é obrigatório e deve apontar para SQL Server (mssql+pyodbc://...).")

        db_url_l = db_url.lower()
        if not (db_url_l.startswith("mssql+pyodbc://") or db_url_l.startswith("mssql://") or "mssql" in db_url_l):
            raise ValueError("Somente SQL Server é suportado. Configure DATABASE_URL com 'mssql+pyodbc://...'.")
        # Sincronizar JWT_SECRET_KEY e SECRET_KEY
        if self.JWT_SECRET_KEY != "changeme":
            self.SECRET_KEY = self.JWT_SECRET_KEY


@lru_cache()
def get_settings() -> Settings:
    return Settings()

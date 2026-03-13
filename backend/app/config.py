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

    # SQLite (dev local): sqlite:///./data/app.db
    # SQL Server (produção): mssql+pyodbc://user:pass@host/dbname?driver=ODBC+Driver+17+for+SQL+Server
    DATABASE_URL: str = "sqlite:///./data/app.db"

    # Segurança: evitar cair silenciosamente em SQLite por falta de .env/variáveis
    # Para permitir SQLite em dev, defina ALLOW_SQLITE=true no ambiente.
    ALLOW_SQLITE: bool = False

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

        if not self.ALLOW_SQLITE and str(self.DATABASE_URL).strip().lower().startswith("sqlite"):
            raise ValueError(
                "SQLite não é permitido (ALLOW_SQLITE=false). Defina DATABASE_URL para SQL Server "
                "ou configure ALLOW_SQLITE=true para uso local."
            )
        # Sincronizar JWT_SECRET_KEY e SECRET_KEY
        if self.JWT_SECRET_KEY != "changeme":
            self.SECRET_KEY = self.JWT_SECRET_KEY


@lru_cache()
def get_settings() -> Settings:
    return Settings()

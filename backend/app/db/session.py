from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, declarative_base
from app.config import get_settings

settings = get_settings()

_url = settings.DATABASE_URL
_is_mssql = "mssql" in _url

# SQL Server — pool otimizado + fast_executemany
_engine_kwargs: dict = {"connect_args": {}}
if _is_mssql:
    _engine_kwargs["fast_executemany"] = True
    _engine_kwargs["pool_size"] = 10          # conexões permanentes no pool
    _engine_kwargs["max_overflow"] = 20       # conexões extras sob carga
    _engine_kwargs["pool_timeout"] = 30       # segundos para esperar conexão livre
    _engine_kwargs["pool_recycle"] = 1800     # recicla conexões a cada 30min (evita timeout do SQL Server)
    _engine_kwargs["pool_pre_ping"] = True    # testa conexão antes de usar (evita "Connection is closed")

engine = create_engine(_url, **_engine_kwargs)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

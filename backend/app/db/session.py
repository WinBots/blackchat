from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.config import get_settings

settings = get_settings()

_url = settings.DATABASE_URL
_is_sqlite = _url.startswith("sqlite")
_is_mssql = "mssql" in _url

_connect_args: dict = {}
if _is_sqlite:
    _connect_args = {"check_same_thread": False}

# SQL Server: desativa fast_executemany para maior compatibilidade; ativa autocommit
# apenas quando necessário via flag do pyodbc.
_engine_kwargs: dict = {"connect_args": _connect_args}
if _is_mssql:
    _engine_kwargs["fast_executemany"] = True

engine = create_engine(_url, **_engine_kwargs)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

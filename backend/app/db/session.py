from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.config import get_settings

settings = get_settings()

_url = settings.DATABASE_URL
_is_mssql = "mssql" in _url

# SQL Server
_engine_kwargs: dict = {"connect_args": {}}
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

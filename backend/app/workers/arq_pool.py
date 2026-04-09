"""
ARQ Redis pool — singleton async para enfileirar jobs a partir da API.

Design:
- Falha graciosamente se o Redis estiver offline (sem lançar exceção)
- Mesmo padrão do redis_client.py existente: _pool = False significa "tentou e falhou"
- A API continua funcionando normalmente sem o pool (jobs são ignorados com log de warning)
"""
from __future__ import annotations

import logging
import os
from typing import Optional

logger = logging.getLogger("blackchat.arq")

# Singleton global do pool ARQ
# None  = ainda não inicializado
# False = tentou e falhou (não tenta de novo)
# obj   = pool ArqRedis conectado
_arq_pool = None


async def create_arq_pool() -> None:
    """Inicializa o pool ARQ. Chamado no startup do FastAPI."""
    global _arq_pool
    try:
        from arq import create_pool
        from arq.connections import RedisSettings

        try:
            from app.config import get_settings
            redis_url = get_settings().REDIS_URL
        except Exception:
            redis_url = os.getenv("REDIS_URL", "redis://127.0.0.1:6379/0")
        settings = RedisSettings.from_dsn(redis_url)
        _arq_pool = await create_pool(settings)
        logger.info(f"✅ ARQ pool conectado: {redis_url}")
    except Exception as e:
        _arq_pool = False
        logger.warning(f"⚠️ ARQ pool indisponível ({e}) — jobs serão ignorados silenciosamente")


async def close_arq_pool() -> None:
    """Fecha o pool ARQ. Chamado no shutdown do FastAPI."""
    global _arq_pool
    if _arq_pool and _arq_pool is not False:
        try:
            await _arq_pool.aclose()
        except Exception:
            pass
    _arq_pool = None


def get_arq_pool():
    """Retorna o pool ARQ ou None se indisponível."""
    if _arq_pool is False or _arq_pool is None:
        return None
    return _arq_pool


async def enqueue(job_name: str, *args, _job_id: str = None, _defer_by: int = None, **kwargs) -> Optional[str]:
    """
    Enfileira um job de forma segura.

    Retorna o job_id (str) se enfileirou com sucesso, ou None se falhou.
    Nunca lança exceção — a API sempre retorna mesmo sem Redis disponível.

    Args:
        job_name: Nome da função registrada no WorkerSettings
        *args: Argumentos posicionais para o job
        _job_id: ID de idempotência (mesmo job_id = não duplica)
        _defer_by: Atraso em segundos antes de executar
        **kwargs: Argumentos nomeados para o job
    """
    pool = get_arq_pool()
    if pool is None:
        logger.warning(f"ARQ indisponível — job {job_name!r} não enfileirado")
        return None
    try:
        enqueue_kwargs = {}
        if _job_id:
            enqueue_kwargs["_job_id"] = _job_id
        if _defer_by:
            from datetime import timedelta
            enqueue_kwargs["_defer_by"] = timedelta(seconds=_defer_by)

        job = await pool.enqueue_job(job_name, *args, **enqueue_kwargs, **kwargs)
        if job:
            logger.debug(f"Job enfileirado: {job_name!r} id={job.job_id}")
            return job.job_id
        # job=None significa que já existe um job com o mesmo _job_id (idempotência)
        logger.debug(f"Job {job_name!r} ignorado (já enfileirado com mesmo id)")
        return None
    except Exception as e:
        logger.error(f"Erro ao enfileirar job {job_name!r}: {e}")
        return None

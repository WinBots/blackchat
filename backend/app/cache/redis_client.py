"""
Conexão Redis centralizada com fallback gracioso.
Se o Redis não estiver acessível, todas as operações retornam None/False
sem levantar exceção — o sistema continua funcionando via banco.
"""
import os
import json
import logging
from typing import Optional, Any

logger = logging.getLogger("blackchat.cache")

# Instância global do Redis (lazy init)
# _redis_client = None     → ainda não tentou conectar
# _redis_client = False    → tentou e falhou (sentinela para não tentar de novo)
# _redis_client = <obj>    → conectado com sucesso
_redis_client = None
_redis_available = False


def get_redis():
    """Retorna a conexão Redis ou None se indisponível."""
    global _redis_client, _redis_available

    # Já inicializado (sucesso ou falha): retorno imediato sem re-tentar
    if _redis_client is not None:
        return _redis_client if _redis_available else None

    try:
        import redis
        url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
        client = redis.Redis.from_url(
            url,
            decode_responses=True,
            socket_connect_timeout=3,
            socket_timeout=2,
            retry_on_timeout=True,
        )
        client.ping()
        _redis_client = client
        _redis_available = True
        logger.info(f"✅ Redis conectado: {url}")
        return _redis_client
    except Exception as e:
        _redis_client = False  # sentinela: não tenta de novo
        _redis_available = False
        logger.warning(f"⚠️ Redis indisponível ({e}) — sistema continua sem cache")
        return None


def cache_get(key: str) -> Optional[Any]:
    """Lê do cache. Retorna None se não existir ou Redis offline."""
    try:
        r = get_redis()
        if r is None:
            return None
        raw = r.get(key)
        if raw is None:
            return None
        return json.loads(raw)
    except Exception as e:
        logger.debug(f"Cache GET falhou ({key}): {e}")
        return None


def cache_set(key: str, value: Any, ttl: int = 300) -> bool:
    """Grava no cache com TTL em segundos. Retorna False se falhar."""
    try:
        r = get_redis()
        if r is None:
            return False
        r.setex(key, ttl, json.dumps(value, default=str))
        return True
    except Exception as e:
        logger.debug(f"Cache SET falhou ({key}): {e}")
        return False


def cache_delete(key: str) -> bool:
    """Remove uma chave do cache."""
    try:
        r = get_redis()
        if r is None:
            return False
        r.delete(key)
        return True
    except Exception as e:
        logger.debug(f"Cache DELETE falhou ({key}): {e}")
        return False


def cache_delete_pattern(pattern: str) -> bool:
    """Remove todas as chaves que correspondem ao padrão (ex: 'tenant:3:*')."""
    try:
        r = get_redis()
        if r is None:
            return False
        keys = r.keys(pattern)
        if keys:
            r.delete(*keys)
            logger.debug(f"Cache: removidas {len(keys)} chaves ({pattern})")
        return True
    except Exception as e:
        logger.debug(f"Cache DELETE PATTERN falhou ({pattern}): {e}")
        return False


def cache_health() -> dict:
    """Retorna status do Redis para healthcheck."""
    try:
        r = get_redis()
        if r is None:
            return {"status": "offline", "message": "Redis indisponível"}
        info = r.info("memory")
        return {
            "status": "online",
            "used_memory_human": info.get("used_memory_human", "?"),
            "connected_clients": r.info("clients").get("connected_clients", "?"),
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

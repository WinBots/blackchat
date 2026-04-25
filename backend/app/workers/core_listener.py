"""
CORE Listener — escuta eventos do CORE via Redis Pub/Sub
Cada bot Telegram registrado no CORE publica seus updates aqui.
"""
import asyncio
import json
import logging
import os
import threading
from typing import Optional

import redis
from sqlalchemy.orm import Session

logger = logging.getLogger("core_listener")


def _get_redis_url() -> str:
    try:
        from app.config import get_settings
        return get_settings().REDIS_URL
    except Exception:
        return os.getenv("REDIS_URL", "redis://localhost:6379/0")

# Store tasks para poder cancela-las no shutdown
_listener_tasks: list[asyncio.Task] = []
_listener_thread: Optional[threading.Thread] = None


def _process_core_update(update: dict, webhook_secret: str, db: Session) -> None:
    """
    Processa update recebido do CORE.
    Chama o handler de Telegram normalmente.
    """
    try:
        from app.api.v1.routers.telegram import _handle_telegram_update

        logger.info(f"[CORE] processando update_id={update.get('update_id')} webhook_secret={webhook_secret}")
        _handle_telegram_update(update, webhook_secret, db)
    except Exception as e:
        logger.error(f"[CORE] erro ao processar update: {e}", exc_info=True)


async def listen_bot_events(bot_id: str, webhook_secret: str) -> None:
    """
    Escuta eventos do CORE para um bot específico via Redis Pub/Sub.
    Processa updates diretamente.
    """
    from app.db.session import SessionLocal

    try:
        r = redis.from_url(_get_redis_url(), decode_responses=True)
        pubsub = r.pubsub()
        channel = f"events:{bot_id}"
        pubsub.subscribe(channel)

        logger.info(f"[CORE] iniciando listener para {bot_id} no canal {channel}")

        for message in pubsub.listen():
            if message["type"] != "message":
                continue

            try:
                event = json.loads(message["data"])
                update = event.get("update", {})
                request_id = event.get("request_id", "unknown")

                logger.debug(
                    f"[CORE] {bot_id} update_id={update.get('update_id')} "
                    f"type={list(update.keys())[1] if len(update) > 1 else 'unknown'} "
                    f"request_id={request_id}"
                )

                # Processar diretamente
                db = SessionLocal()
                try:
                    _process_core_update(update, webhook_secret, db)
                finally:
                    db.close()

            except json.JSONDecodeError as e:
                logger.warning(f"[CORE] erro ao decodificar JSON para {bot_id}: {e}")
            except Exception as e:
                logger.error(f"[CORE] erro ao processar update para {bot_id}: {e}", exc_info=True)

    except Exception as e:
        logger.error(f"[CORE] erro ao conectar Redis para {bot_id}: {e}", exc_info=True)


def _listen_bot_sync(core_bot_id: str, webhook_secret: str) -> None:
    """Listener síncrono para um bot — roda em thread dedicada."""
    from app.db.session import SessionLocal

    while True:
        try:
            r = redis.from_url(_get_redis_url(), decode_responses=True)
            pubsub = r.pubsub()
            channel = f"events:{core_bot_id}"
            pubsub.subscribe(channel)

            logger.info(f"[CORE] escutando: {channel}")

            for message in pubsub.listen():
                if message["type"] != "message":
                    continue
                try:
                    event = json.loads(message["data"])
                    update = event.get("update", {})
                    update_id = update.get("update_id", "?")
                    print(f"[CORE] {core_bot_id} recebeu update_id={update_id}", flush=True)
                    db = SessionLocal()
                    try:
                        _process_core_update(update, webhook_secret, db)
                    finally:
                        db.close()
                    print(f"[CORE] {core_bot_id} update_id={update_id} processado", flush=True)
                except Exception as e:
                    print(f"[CORE] {core_bot_id} ERRO: {e}", flush=True)
                    logger.error(f"[CORE] erro ao processar update {core_bot_id}: {e}", exc_info=True)

        except Exception as e:
            logger.error(f"[CORE] erro listener {core_bot_id}: {e} — reconectando em 5s")
            import time
            time.sleep(5)


def start_core_listeners() -> None:
    """Inicia uma thread por bot para escutar eventos do CORE."""
    from app.db.session import SessionLocal
    from app.db.models.channel import Channel

    db = SessionLocal()
    try:
        channels = db.query(Channel).filter(
            Channel.type == "telegram",
            Channel.is_active == True,  # noqa: E712
            Channel.core_bot_id != None,  # noqa: E712
        ).all()

        logger.info(f"[CORE] encontrados {len(channels)} bots para listeners")
        print(f"[CORE] encontrados {len(channels)} bots", flush=True)

        for ch in channels:
            webhook_secret = ch.webhook_secret
            core_bot_id = ch.core_bot_id

            if not webhook_secret or not core_bot_id:
                logger.warning(f"[CORE] canal {ch.id} sem webhook_secret ou core_bot_id")
                continue

            t = threading.Thread(
                target=_listen_bot_sync,
                args=(core_bot_id, webhook_secret),
                daemon=True,
                name=f"core-{core_bot_id}",
            )
            t.start()
            logger.info(f"[CORE] listener iniciado: {core_bot_id}")
            print(f"[CORE] listener iniciado: {core_bot_id}", flush=True)

    finally:
        db.close()

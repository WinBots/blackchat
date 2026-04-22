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

                # Processar em thread separada para não bloquear listener
                db = SessionLocal()
                try:
                    await asyncio.to_thread(_process_core_update, update, webhook_secret, db)
                finally:
                    db.close()

            except json.JSONDecodeError as e:
                logger.warning(f"[CORE] erro ao decodificar JSON para {bot_id}: {e}")
            except Exception as e:
                logger.error(f"[CORE] erro ao processar update para {bot_id}: {e}", exc_info=True)

    except Exception as e:
        logger.error(f"[CORE] erro ao conectar Redis para {bot_id}: {e}", exc_info=True)


def start_core_listeners() -> None:
    """
    Inicia listeners para todos os bots ativos no banco.
    Deve ser chamado no startup da API.
    """
    global _listener_thread

    def _run_listeners():
        """Thread que gerencia o event loop dos listeners."""
        try:
            from app.db.session import SessionLocal
            from app.db.models.channel import Channel

            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

            # Buscar todos os bots Telegram com core_bot_id
            db = SessionLocal()
            try:
                channels = db.query(Channel).filter(
                    Channel.type == "telegram",
                    Channel.is_active == True,  # noqa: E712
                    Channel.core_bot_id != None,  # noqa: E712
                ).all()

                logger.info(f"[CORE] encontrados {len(channels)} bots para listeners")

                tasks = []
                for ch in channels:
                    webhook_secret = ch.webhook_secret
                    core_bot_id = ch.core_bot_id

                    if not webhook_secret or not core_bot_id:
                        logger.warning(f"[CORE] canal {ch.id} sem webhook_secret ou core_bot_id")
                        continue

                    task = loop.create_task(listen_bot_events(core_bot_id, webhook_secret))
                    tasks.append(task)
                    logger.info(f"[CORE] listener criado: {core_bot_id}")

                # Manter event loop rodando
                loop.run_until_complete(asyncio.gather(*tasks))

            finally:
                db.close()

        except Exception as e:
            logger.error(f"[CORE] erro ao iniciar listeners: {e}", exc_info=True)

    # Iniciar thread daemon que roda o event loop
    _listener_thread = threading.Thread(target=_run_listeners, daemon=True, name="core-listeners")
    _listener_thread.start()
    logger.info("[CORE] thread de listeners iniciada")

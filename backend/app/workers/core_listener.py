"""
CORE Listener — escuta eventos do CORE via Redis Pub/Sub
Cada bot Telegram registrado no CORE publica seus updates aqui.
"""
import asyncio
import json
import logging
import os
from typing import Callable

import redis

logger = logging.getLogger("core_listener")

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")


async def listen_bot_events(bot_id: str, handler: Callable) -> None:
    """
    Escuta eventos do CORE para um bot específico.
    handler(update: dict) será chamado para cada update recebido.
    """
    try:
        r = redis.from_url(REDIS_URL, decode_responses=True)
        pubsub = r.pubsub()
        channel = f"events:{bot_id}"
        pubsub.subscribe(channel)

        logger.info(f"[CORE] escutando canal: {channel}")

        for message in pubsub.listen():
            if message["type"] != "message":
                continue

            try:
                event = json.loads(message["data"])
                update = event.get("update", {})
                request_id = event.get("request_id", "unknown")

                logger.debug(f"[CORE] {bot_id} update_id={update.get('update_id')} request_id={request_id}")

                # Chamar handler assincronamente
                if asyncio.iscoroutinefunction(handler):
                    await handler(update)
                else:
                    # Se handler for síncrono, executar em thread
                    await asyncio.to_thread(handler, update)

            except json.JSONDecodeError as e:
                logger.warning(f"[CORE] erro ao decodificar JSON: {e}")
            except Exception as e:
                logger.error(f"[CORE] erro ao processar update: {e}", exc_info=True)

    except Exception as e:
        logger.error(f"[CORE] erro ao conectar Redis para {bot_id}: {e}", exc_info=True)


def get_core_listeners_tasks(bots: list[dict], handler: Callable) -> list:
    """
    Cria tasks para todos os bots.

    Args:
        bots: lista de {bot_id, core_bot_id}
        handler: função que processa updates

    Returns:
        lista de asyncio.Task
    """
    tasks = []
    for bot_info in bots:
        core_bot_id = bot_info.get("core_bot_id")
        if not core_bot_id:
            continue

        task = asyncio.create_task(listen_bot_events(core_bot_id, handler))
        tasks.append(task)
        logger.info(f"[CORE] task criada para bot: {core_bot_id}")

    return tasks

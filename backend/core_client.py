"""
CORE SDK — Python Client
Biblioteca para integração com o CORE System.

Uso básico:
    from core_client import get_core_client, init_core_client

    # Inicializar (uma vez, no startup)
    init_core_client("https://telegram-core.blackchatpro.com")

    # Usar em qualquer lugar
    client = get_core_client()
    client.register_bot(bot_id, bot_token, user_id, webhook_url)
    client.send_event(bot_id, update)
"""
from __future__ import annotations

import logging
import os
import uuid
from typing import Optional

import requests

logger = logging.getLogger("core_sdk")


class CoreClient:
    def __init__(self, core_url: str, timeout: int = 10):
        """
        Args:
            core_url: URL base do CORE (ex: https://telegram-core.blackchatpro.com)
            timeout: Timeout em segundos para cada request
        """
        self.core_url = core_url.rstrip("/")
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})

    # ── Register Bot ───────────────────────────────────────────────────────
    def register_bot(
        self,
        bot_id: str,
        bot_token: str,
        user_id: int,
        webhook_url: str,
        allowed_updates: list[str] | None = None,
    ) -> Optional[dict]:
        """
        Registra bot no CORE.

        Returns:
            {"ok": True, "bot_id": "...", "registered_at": "..."} ou None se erro
        """
        if allowed_updates is None:
            allowed_updates = ["message", "callback_query", "my_chat_member"]

        payload = {
            "bot_id": bot_id,
            "bot_token": bot_token,
            "user_id": user_id,
            "webhook_url": webhook_url,
            "allowed_updates": allowed_updates,
        }

        try:
            response = self.session.post(
                f"{self.core_url}/core/register-bot",
                json=payload,
                timeout=self.timeout,
            )
            response.raise_for_status()
            result = response.json()
            logger.info(f"[CORE] bot registrado: {bot_id}")
            return result
        except requests.exceptions.Timeout:
            logger.error(f"[CORE] register_bot timeout: {bot_id}")
            return None
        except requests.exceptions.ConnectionError:
            logger.error(f"[CORE] register_bot connection error: {self.core_url}")
            return None
        except requests.exceptions.HTTPError as e:
            logger.error(f"[CORE] register_bot HTTP {e.response.status_code}: {bot_id} — {e.response.text}")
            return None
        except Exception as e:
            logger.error(f"[CORE] register_bot erro inesperado: {bot_id} — {e}")
            return None

    # ── Send Event ─────────────────────────────────────────────────────────
    def send_event(
        self,
        bot_id: str,
        update: dict,
        request_id: Optional[str] = None,
    ) -> bool:
        """
        Envia evento (Telegram Update) para o CORE processar.

        Returns:
            True se 202 Accepted, False se erro
        """
        if request_id is None:
            request_id = str(uuid.uuid4())

        payload = {
            "request_id": request_id,
            "bot_id": bot_id,
            "update": update,
        }

        try:
            response = self.session.post(
                f"{self.core_url}/core/events",
                json=payload,
                timeout=self.timeout,
            )
            if response.status_code == 202:
                logger.debug(f"[CORE] evento aceito: {bot_id} request_id={request_id}")
                return True
            elif response.status_code == 429:
                logger.warning(f"[CORE] rate limit atingido: {bot_id}")
                return False
            else:
                logger.error(f"[CORE] send_event HTTP {response.status_code}: {bot_id} — {response.text}")
                return False
        except requests.exceptions.Timeout:
            logger.error(f"[CORE] send_event timeout: {bot_id}")
            return False
        except requests.exceptions.ConnectionError:
            logger.error(f"[CORE] send_event connection error: {self.core_url}")
            return False
        except Exception as e:
            logger.error(f"[CORE] send_event erro inesperado: {bot_id} — {e}")
            return False

    # ── Health Check ───────────────────────────────────────────────────────
    def get_health(self) -> bool:
        """
        Verifica se o CORE está saudável.

        Returns:
            True se healthy, False se erro
        """
        try:
            response = self.session.get(
                f"{self.core_url}/health",
                timeout=self.timeout,
            )
            if response.status_code == 200:
                data = response.json()
                is_healthy = data.get("status") == "healthy"
                if is_healthy:
                    logger.debug("[CORE] health check: healthy")
                else:
                    logger.warning(f"[CORE] health check unhealthy: {data}")
                return is_healthy
            return False
        except Exception as e:
            logger.error(f"[CORE] health check falhou: {e}")
            return False


# ── Singleton ──────────────────────────────────────────────────────────────
_instance: Optional[CoreClient] = None


def init_core_client(url: Optional[str] = None, timeout: int = 10) -> CoreClient:
    """
    Inicializa o cliente global. Chamar uma vez no startup da aplicação.

    Args:
        url: URL do CORE. Se None, usa CORE_URL do ambiente ou http://localhost
        timeout: Timeout em segundos

    Returns:
        Instância do CoreClient
    """
    global _instance
    core_url = url or os.getenv("CORE_URL", "http://localhost")
    _instance = CoreClient(core_url, timeout=timeout)
    logger.info(f"[CORE] cliente inicializado: {core_url}")
    return _instance


def get_core_client() -> CoreClient:
    """
    Retorna a instância global. Inicializa automaticamente se ainda não foi chamado.

    Returns:
        Instância do CoreClient
    """
    global _instance
    if _instance is None:
        _instance = init_core_client()
    return _instance

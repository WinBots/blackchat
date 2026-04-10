"""
Configuração do worker ARQ — funções de job e WorkerSettings.

Para iniciar o worker (desenvolvimento — processa todas as filas):
    cd backend
    arq app.workers.worker_settings.WorkerSettings

Para iniciar workers especializados (produção):
    arq app.workers.worker_settings.WebhookWorkerSettings
    arq app.workers.worker_settings.FlowWorkerSettings
    arq app.workers.worker_settings.BulkWorkerSettings
    arq app.workers.worker_settings.SequenceWorkerSettings
"""
from __future__ import annotations

import asyncio
import json
import logging
import os
import time
from typing import List

logger = logging.getLogger("blackchat.worker")


# ══════════════════════════════════════════════════════════════
#  CONTEXTO DO WORKER (startup/shutdown)
# ══════════════════════════════════════════════════════════════

async def on_startup(ctx: dict) -> None:
    """
    Executado uma vez quando o worker inicia.
    Disponibiliza a fábrica de sessão DB para todos os jobs via ctx["db_factory"].
    """
    from app.db.session import SessionLocal
    ctx["db_factory"] = SessionLocal
    logger.info("✅ Worker ARQ iniciado — DB factory configurado")


async def on_shutdown(ctx: dict) -> None:
    """Executado quando o worker para."""
    logger.info("Worker ARQ encerrado")


# ══════════════════════════════════════════════════════════════
#  HELPERS INTERNOS
# ══════════════════════════════════════════════════════════════

def _update_job_progress(job_id: str, data: dict) -> None:
    """Grava progresso do job no Redis para polling pelo frontend. TTL: 2h."""
    try:
        from app.cache.redis_client import cache_set
        cache_set(f"bulk_job:{job_id}", data, ttl=7200)
    except Exception as e:
        logger.debug(f"Falha ao gravar progresso do job {job_id}: {e}")


def _resolve_contact_send_info(db, contact_id: int) -> dict | None:
    """
    Retorna {chat_id, bot_token, channel_id} para um contato.
    Retorna None com motivo se não for possível enviar.
    """
    from app.db.models.contact import Contact
    from app.db.models.channel import Channel
    from app.db.models.message import Message

    contact = db.query(Contact).filter(Contact.id == contact_id).first()
    if not contact:
        return {"error": "Contato não encontrado"}

    channel = db.query(Channel).filter(Channel.id == contact.default_channel_id).first()
    if not channel:
        return {"error": "Canal não configurado"}

    last_inbound = (
        db.query(Message)
        .filter(Message.contact_id == contact_id, Message.direction == "inbound")
        .order_by(Message.id.desc())
        .first()
    )
    if not last_inbound or not last_inbound.extra_data:
        return {"error": "Contato ainda não interagiu com o bot"}

    try:
        extra = (
            json.loads(last_inbound.extra_data)
            if isinstance(last_inbound.extra_data, str)
            else last_inbound.extra_data
        )
        chat_id = extra.get("chat_id")
    except Exception:
        chat_id = None

    if not chat_id:
        return {"error": "chat_id não encontrado"}

    try:
        cfg = (
            json.loads(channel.config)
            if isinstance(channel.config, str)
            else (channel.config or {})
        )
        bot_token = cfg.get("bot_token")
    except Exception:
        bot_token = None

    if not bot_token:
        return {"error": "Token do bot não configurado no canal"}

    return {"chat_id": chat_id, "bot_token": bot_token, "channel_id": channel.id}


# ══════════════════════════════════════════════════════════════
#  FUNÇÕES DE JOB
# ══════════════════════════════════════════════════════════════

async def process_webhook(ctx: dict, payload: dict, webhook_secret: str) -> None:
    """
    [Fase 3] Processa um update do Telegram de forma assíncrona via fila.
    Chamado pelo worker após o handler retornar 200 ao Telegram imediatamente.
    """
    from fastapi import HTTPException as _HTTPException
    from app.api.v1.routers.telegram import _handle_telegram_update, invalidate_trigger_cache

    # Invalida cache de triggers para evitar DetachedInstanceError:
    # o cache armazena objetos SQLAlchemy de sessões anteriores que já foram fechadas.
    invalidate_trigger_cache()

    db = ctx["db_factory"]()
    try:
        _handle_telegram_update(payload, webhook_secret, db)
    except _HTTPException as e:
        # Canal não encontrado, config inválido etc. — loga e descarta (não retry)
        logger.warning(f"process_webhook: HTTPException {e.status_code} — {e.detail}")
    except Exception as e:
        logger.error(f"process_webhook: erro inesperado — {e}", exc_info=True)
        raise  # relança para ARQ registrar falha (e tentar retry se max_tries > 1)
    finally:
        db.close()


async def run_flow_job(
    ctx: dict,
    channel_id: int,
    contact_id: int,
    flow_id: int,
    chat_id: int,
    bot_token: str,
    execution_id: int = None,
    start_from_step_id: int = None,
) -> None:
    """
    [Fase 4] Executa um fluxo de automação via fila ARQ.

    Usa run_in_executor para não bloquear o event loop do worker enquanto o fluxo
    executa (que é síncrono e pode levar segundos/minutos por delays internos).
    run_flow_background cria sua própria sessão DB internamente.
    """
    from app.api.v1.routers.telegram import run_flow_background

    loop = asyncio.get_event_loop()
    await loop.run_in_executor(
        None,  # ThreadPoolExecutor padrão do asyncio
        lambda: run_flow_background(
            channel_id=channel_id,
            contact_id=contact_id,
            flow_id=flow_id,
            chat_id=chat_id,
            bot_token=bot_token,
            execution_id=execution_id,
            start_from_step_id=start_from_step_id,
        ),
    )
    logger.info(f"run_flow_job concluído: flow_id={flow_id} contact_id={contact_id} exec_id={execution_id}")


async def send_bulk_message_job(
    ctx: dict,
    tenant_id: int,
    contact_ids: List[int],
    text: str,
    parse_mode: str = "MarkdownV2",
) -> dict:
    """
    [Fase 2] Envia mensagens em massa via fila — desbloqueia o HTTP request.

    Processa contatos em lotes com delay entre envios para respeitar o
    rate limit do Telegram (30 msg/s por bot, ~1 msg/s recomendado para broadcast).
    """
    from app.db.models.message import Message
    from app.services.telegram_sender import send_telegram_message

    # Obtém o job_id do contexto ARQ para atualizar progresso
    job_id = ctx.get("job_id", f"bulk_msg_{tenant_id}_unknown")
    db = ctx["db_factory"]()

    sent = 0
    failed = 0
    errors: List[dict] = []
    total = len(contact_ids)

    _update_job_progress(job_id, {
        "job_id": job_id,
        "tenant_id": tenant_id,
        "status": "running",
        "total": total,
        "sent": 0,
        "failed": 0,
        "errors": [],
        "started_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    })

    try:
        for i, contact_id in enumerate(contact_ids):
            try:
                info = _resolve_contact_send_info(db, contact_id)
                if "error" in info:
                    failed += 1
                    errors.append({"contact_id": contact_id, "reason": info["error"]})
                    continue

                result = send_telegram_message(
                    info["bot_token"], info["chat_id"], text, parse_mode=parse_mode
                )
                if result is None:
                    failed += 1
                    errors.append({"contact_id": contact_id, "reason": "Falha ao enviar pelo Telegram"})
                    continue

                msg = Message(
                    tenant_id=tenant_id,
                    contact_id=contact_id,
                    channel_id=info["channel_id"],
                    direction="outbound",
                    content=text,
                    message_type="text",
                    status="sent",
                    extra_data=json.dumps({"chat_id": info["chat_id"]}),
                )
                db.add(msg)
                sent += 1

                # Commit a cada 50 mensagens para não acumular transação longa
                if sent % 50 == 0:
                    db.commit()

            except Exception as e:
                failed += 1
                errors.append({"contact_id": contact_id, "reason": str(e)})

            # Atualiza progresso a cada 25 contatos processados
            if (i + 1) % 25 == 0:
                _update_job_progress(job_id, {
                    "job_id": job_id,
                    "tenant_id": tenant_id,
                    "status": "running",
                    "total": total,
                    "sent": sent,
                    "failed": failed,
                    "errors": errors[-20:],  # Mantém só os últimos 20 erros no progresso
                    "started_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                })

            # Rate limiting: ~10 msg/s (seguro para broadcast Telegram)
            await asyncio.sleep(0.1)

        db.commit()

    except Exception as e:
        logger.error(f"Erro crítico em send_bulk_message_job: {e}")
        try:
            db.rollback()
        except Exception:
            pass
    finally:
        db.close()

    result = {
        "job_id": job_id,
        "tenant_id": tenant_id,
        "status": "completed",
        "total": total,
        "sent": sent,
        "failed": failed,
        "errors": errors,
        "completed_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }
    _update_job_progress(job_id, result)
    logger.info(f"bulk_message_job concluído: {sent}/{total} enviados, {failed} falhas")
    return result


async def run_bulk_flow_job(
    ctx: dict,
    tenant_id: int,
    contact_ids: List[int],
    flow_id: int,
) -> dict:
    """
    [Fase 2] Inicia fluxos em massa para um segmento de contatos.

    Usa a implementação existente run_flow_background (via threading) para
    manter compatibilidade com a Fase 4, onde será migrada para run_flow_job.
    """
    import threading as _threading
    from app.db.models.contact import Contact
    from app.db.models.channel import Channel
    from app.db.models.flow import Flow
    from app.db.models.flow_execution import FlowExecution
    from app.api.v1.routers.telegram import run_flow_background

    job_id = ctx.get("job_id", f"bulk_flow_{tenant_id}_unknown")
    db = ctx["db_factory"]()

    # Valida que o fluxo existe e está ativo
    flow = db.query(Flow).filter(Flow.id == flow_id, Flow.tenant_id == tenant_id).first()
    if not flow or not flow.is_active:
        db.close()
        result = {
            "job_id": job_id,
            "tenant_id": tenant_id,
            "status": "failed",
            "error": "Fluxo não encontrado ou inativo",
        }
        _update_job_progress(job_id, result)
        return result

    started = 0
    failed = 0
    errors: List[dict] = []
    total = len(contact_ids)

    _update_job_progress(job_id, {
        "job_id": job_id,
        "tenant_id": tenant_id,
        "status": "running",
        "total": total,
        "started": 0,
        "failed": 0,
        "errors": [],
        "started_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    })

    try:
        for i, contact_id in enumerate(contact_ids):
            try:
                info = _resolve_contact_send_info(db, contact_id)
                if "error" in info:
                    failed += 1
                    errors.append({"contact_id": contact_id, "reason": info["error"]})
                    continue

                # Cria FlowExecution e dispara em background thread
                flow_execution = FlowExecution(
                    tenant_id=tenant_id,
                    contact_id=contact_id,
                    flow_id=flow_id,
                    trigger_type="manual",
                    status="active",
                )
                db.add(flow_execution)
                db.commit()
                db.refresh(flow_execution)

                _threading.Thread(
                    target=run_flow_background,
                    kwargs=dict(
                        channel_id=info["channel_id"],
                        contact_id=contact_id,
                        flow_id=flow_id,
                        chat_id=info["chat_id"],
                        bot_token=info["bot_token"],
                        execution_id=flow_execution.id,
                        start_from_step_id=None,
                    ),
                    daemon=True,
                ).start()

                started += 1

            except Exception as e:
                failed += 1
                errors.append({"contact_id": contact_id, "reason": str(e)})

            if (i + 1) % 25 == 0:
                _update_job_progress(job_id, {
                    "job_id": job_id,
                    "tenant_id": tenant_id,
                    "status": "running",
                    "total": total,
                    "started": started,
                    "failed": failed,
                    "errors": errors[-20:],
                    "started_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                })

            # Pequeno delay para não sobrecarregar o DB com criações simultâneas
            await asyncio.sleep(0.05)

    except Exception as e:
        logger.error(f"Erro crítico em run_bulk_flow_job: {e}")
    finally:
        db.close()

    result = {
        "job_id": job_id,
        "tenant_id": tenant_id,
        "status": "completed",
        "total": total,
        "started": started,
        "failed": failed,
        "errors": errors,
        "completed_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }
    _update_job_progress(job_id, result)
    logger.info(f"bulk_flow_job concluído: {started}/{total} fluxos iniciados, {failed} falhas")
    return result


async def advance_sequences_job(ctx: dict) -> None:
    """
    [Fase 5] Avança sequências cujo next_execution_at <= agora.

    Executa como cron job a cada minuto (definido em WorkerSettings.cron_jobs).
    Para cada ContactSequence vencida: envia a mensagem do step atual e agenda o próximo.
    """
    import json as _json
    from datetime import datetime, timezone, timedelta
    from app.db.models.sequence import Sequence, ContactSequence
    from app.db.models.contact import Contact
    from app.db.models.channel import Channel
    from app.db.models.message import Message
    from app.services.telegram_sender import send_telegram_message

    db = ctx["db_factory"]()
    now = datetime.now(timezone.utc)

    try:
        due = (
            db.query(ContactSequence)
            .filter(
                ContactSequence.status == "active",
                ContactSequence.next_execution_at <= now,
            )
            .order_by(ContactSequence.next_execution_at)
            .limit(100)  # processa no máximo 100 por ciclo para não sobrecarregar
            .all()
        )

        if not due:
            return

        logger.info(f"advance_sequences_job: {len(due)} ContactSequence(s) vencidas")

        for cs in due:
            try:
                seq = db.query(Sequence).filter(
                    Sequence.id == cs.sequence_id,
                    Sequence.is_active == True,
                ).first()

                if not seq:
                    cs.status = "cancelled"
                    db.commit()
                    continue

                steps = seq.steps if isinstance(seq.steps, list) else (_json.loads(seq.steps) if seq.steps else [])

                if cs.current_step >= len(steps):
                    cs.status = "completed"
                    cs.completed_at = now
                    db.commit()
                    continue

                step = steps[cs.current_step]
                step_type = step.get("type", "message")

                if step_type == "message":
                    # Resolver chat_id e bot_token do contato
                    contact = db.query(Contact).filter(Contact.id == cs.contact_id).first()
                    if not contact:
                        cs.status = "cancelled"
                        db.commit()
                        continue

                    channel = db.query(Channel).filter(Channel.id == contact.default_channel_id).first()
                    if not channel:
                        cs.status = "cancelled"
                        db.commit()
                        continue

                    last_inbound = (
                        db.query(Message)
                        .filter(Message.contact_id == cs.contact_id, Message.direction == "inbound")
                        .order_by(Message.id.desc())
                        .first()
                    )
                    if not last_inbound or not last_inbound.extra_data:
                        cs.status = "cancelled"
                        db.commit()
                        continue

                    try:
                        extra = _json.loads(last_inbound.extra_data) if isinstance(last_inbound.extra_data, str) else last_inbound.extra_data
                        chat_id = extra.get("chat_id")
                    except Exception:
                        chat_id = None

                    if not chat_id:
                        cs.status = "cancelled"
                        db.commit()
                        continue

                    try:
                        cfg = _json.loads(channel.config) if isinstance(channel.config, str) else (channel.config or {})
                        bot_token = cfg.get("bot_token")
                    except Exception:
                        bot_token = None

                    if not bot_token:
                        cs.status = "cancelled"
                        db.commit()
                        continue

                    content = step.get("content", "")
                    if content:
                        send_telegram_message(bot_token, chat_id, content)
                        msg = Message(
                            tenant_id=seq.tenant_id,
                            contact_id=cs.contact_id,
                            channel_id=channel.id,
                            direction="outbound",
                            content=content,
                            message_type="text",
                            status="sent",
                            extra_data=_json.dumps({"chat_id": chat_id}),
                        )
                        db.add(msg)

                # Avançar para próximo step
                cs.current_step += 1
                if cs.current_step >= len(steps):
                    cs.status = "completed"
                    cs.completed_at = now
                else:
                    next_step = steps[cs.current_step]
                    delay = int(next_step.get("delay", 0))
                    unit = next_step.get("delay_unit", "minutes")
                    _UNITS = {"seconds": 1, "minutes": 60, "hours": 3600, "days": 86400}
                    seconds = delay * _UNITS.get(unit, 60)
                    cs.next_execution_at = now + timedelta(seconds=max(seconds, 60))

                db.commit()
                await asyncio.sleep(0.05)  # throttle entre registros

            except Exception as e:
                logger.error(f"advance_sequences_job: erro em ContactSequence {cs.id}: {e}")
                try:
                    db.rollback()
                except Exception:
                    pass

    except Exception as e:
        logger.error(f"advance_sequences_job: erro geral: {e}")
    finally:
        db.close()


async def send_email_job(
    ctx: dict,
    email_type: str,
    to_email: str,
    **kwargs,
) -> None:
    """
    [Fase 5] Envia e-mail via fila — desbloqueia endpoints de auth.

    email_type: 'welcome' | 'plan_activated' | 'plan_upgraded' |
                'plan_limit_reached' | 'subscription_canceled' | 'password_reset'
    """
    try:
        from app.services import email_sender as _es

        dispatch = {
            "welcome": _es.send_welcome_email,
            "plan_activated": _es.send_plan_activated_email,
            "plan_upgraded": _es.send_plan_upgraded_email,
            "plan_limit_reached": _es.send_plan_limit_reached_email,
            "subscription_canceled": _es.send_subscription_canceled_email,
            "password_reset": _es.send_password_reset_email,
        }
        fn = dispatch.get(email_type)
        if fn is None:
            logger.warning(f"send_email_job: tipo desconhecido '{email_type}'")
            return

        await fn(to_email=to_email, **kwargs)
        logger.info(f"send_email_job: '{email_type}' enviado para {to_email}")
    except Exception as e:
        logger.error(f"send_email_job: erro ao enviar '{email_type}' para {to_email}: {e}")
        raise  # Permite retry pelo ARQ


async def generate_ai_flow_job(ctx: dict, tenant_id: int, payload: dict) -> dict:
    """
    [Fase 5] Gera fluxo com IA de forma assíncrona (Claude API ~30s).
    """
    logger.warning("generate_ai_flow_job: stub — implementação pendente (Fase 5)")
    return {"status": "not_implemented"}


# ══════════════════════════════════════════════════════════════
#  REDIS SETTINGS
# ══════════════════════════════════════════════════════════════

def _make_redis_settings():
    from arq.connections import RedisSettings
    try:
        from app.config import get_settings
        url = get_settings().REDIS_URL
    except Exception:
        url = os.getenv("REDIS_URL", "redis://127.0.0.1:6379/0")
    return RedisSettings.from_dsn(url)


# ══════════════════════════════════════════════════════════════
#  WORKER SETTINGS
# ══════════════════════════════════════════════════════════════

class WorkerSettings:
    """Worker geral — processa todas as filas. Use em desenvolvimento."""
    functions = [
        process_webhook,
        run_flow_job,
        send_bulk_message_job,
        run_bulk_flow_job,
        advance_sequences_job,
        send_email_job,
        generate_ai_flow_job,
    ]
    on_startup = on_startup
    on_shutdown = on_shutdown
    redis_settings = _make_redis_settings()
    max_jobs = 10
    job_timeout = 600
    max_tries = 2
    log_results_ms = 1000
    # Cron: avança sequências a cada minuto (second=0 → no início de cada minuto)
    cron_jobs = [__import__("arq").cron(advance_sequences_job, second=0)]


class WebhookWorkerSettings(WorkerSettings):
    """Worker dedicado a webhooks — alta concorrência, jobs rápidos."""
    functions = [process_webhook]
    max_jobs = 20
    job_timeout = 30
    max_tries = 1


class FlowWorkerSettings(WorkerSettings):
    """Worker dedicado a execução de fluxos."""
    functions = [run_flow_job]
    max_jobs = 10
    job_timeout = 300
    max_tries = 2


class BulkWorkerSettings(WorkerSettings):
    """Worker dedicado a disparos em massa — concorrência baixa intencional."""
    functions = [send_bulk_message_job, run_bulk_flow_job]
    max_jobs = 2
    job_timeout = 3600
    max_tries = 1  # bulk não deve reprocessar (evita duplicatas)


class SequenceWorkerSettings(WorkerSettings):
    """Worker para sequências, e-mail e IA."""
    functions = [advance_sequences_job, send_email_job, generate_ai_flow_job]
    max_jobs = 5
    job_timeout = 120
    max_tries = 3
    cron_jobs = [__import__("arq").cron(advance_sequences_job, second=0)]

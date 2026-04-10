"""Router para webhook do Telegram"""
from fastapi import APIRouter, Depends, Body, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
import json
import logging
import threading
import time
import httpx
import random
from typing import Dict, Any

from app.db.session import get_db, SessionLocal
from app.db.models.channel import Channel
from app.db.models.contact import Contact
from app.db.models.flow import Flow
from app.db.models.flow_step import FlowStep
from app.db.models.message import Message
from app.db.models.tag import ContactTag
from app.db.models.sequence import Sequence, ContactSequence
from app.db.models.flow_execution import FlowExecution
from app.db.models.flow_execution_log import FlowExecutionLog
from app.services.telegram_sender import send_telegram_message, send_telegram_photo, send_telegram_audio, send_telegram_video, send_telegram_video_note
from app.services.flow_logger import FlowLogger
from app.services.billing_service import check_contact_limit, get_plan_for_tenant, LimitExceededError
from app.config import get_settings
from datetime import datetime, timedelta
from sqlalchemy import and_, or_, case, func, cast, String

logger = logging.getLogger(__name__)

router = APIRouter()

# ── Cache em memória para trigger maps (evita re-query em rajadas de webhooks) ──
_trigger_cache: Dict[str, Any] = {}  # {cache_key: {"ts": float, "data": {...}}}
_TRIGGER_CACHE_TTL = 30  # segundos


def _load_trigger_map(db: Session, tenant_id: int, channel_id: int):
    """
    Carrega TODOS os flows ativos + seus trigger steps em 2 queries (em vez de N+1).
    Cache em memória de 30s evita re-query em rajadas de webhooks do mesmo tenant.

    Resultado: {
        "flows": [Flow, ...],
        "trigger_by_flow": {flow_id: {"config": dict, "step": FlowStep}},
        "keyword_to_flow": {"keyword_lower": Flow},
        "ref_flows": [(Flow, ref_key, save_ref_field), ...],
    }
    """
    cache_key = f"{tenant_id}:{channel_id}"
    cached = _trigger_cache.get(cache_key)
    if cached and (time.time() - cached["ts"]) < _TRIGGER_CACHE_TTL:
        return cached["data"]

    flows = db.query(Flow).filter(
        Flow.tenant_id == tenant_id,
        Flow.is_active == True,
        ((Flow.channel_id == channel_id) | (Flow.channel_id == None))
    ).all()

    if not flows:
        result = {"flows": [], "trigger_by_flow": {}, "keyword_to_flow": {}, "ref_flows": []}
        _trigger_cache[cache_key] = {"ts": time.time(), "data": result}
        return result

    flow_ids = [f.id for f in flows]
    flow_map = {f.id: f for f in flows}

    # UMA query para TODOS os trigger steps dos flows ativos
    trigger_steps = db.query(FlowStep).filter(
        FlowStep.flow_id.in_(flow_ids),
        FlowStep.type == "trigger"
    ).all()

    trigger_by_flow = {}
    keyword_to_flow = {}
    ref_flows = []

    for ts in trigger_steps:
        try:
            cfg = json.loads(ts.config) if ts.config else {}
        except Exception:
            cfg = {}

        flow = flow_map.get(ts.flow_id)
        if not flow:
            continue

        trigger_by_flow[ts.flow_id] = {"config": cfg, "step": ts}
        trigger_type = cfg.get("triggerType")

        if trigger_type == "message":
            for kw in cfg.get("keywords", []):
                kw_text = kw if isinstance(kw, str) else kw.get("text", "")
                if kw_text:
                    kw_lower = kw_text.lower().strip()
                    if kw_lower not in keyword_to_flow:
                        keyword_to_flow[kw_lower] = flow

        elif trigger_type == "telegram_ref_url":
            ref_key = cfg.get("ref_key", "").strip()
            save_ref_field = cfg.get("save_ref_field", "").strip()
            if ref_key:
                ref_flows.append((flow, ref_key, save_ref_field))

    result = {
        "flows": flows,
        "trigger_by_flow": trigger_by_flow,
        "keyword_to_flow": keyword_to_flow,
        "ref_flows": ref_flows,
    }
    _trigger_cache[cache_key] = {"ts": time.time(), "data": result}
    return result


def invalidate_trigger_cache(tenant_id: int = None):
    """Limpa o cache de triggers. Chamar ao salvar/alterar fluxos."""
    if tenant_id:
        keys_to_remove = [k for k in _trigger_cache if k.startswith(f"{tenant_id}:")]
        for k in keys_to_remove:
            _trigger_cache.pop(k, None)
    else:
        _trigger_cache.clear()


def normalize_media_url(url: str) -> str:
    """Substitui URLs localhost pelo PUBLIC_BASE_URL configurado em runtime.
    Garante que imagens/áudios/vídeos enviados ao Telegram sejam acessíveis publicamente."""
    if not url:
        return url
    if 'localhost' in url or '127.0.0.1' in url:
        settings = get_settings()
        public_base = settings.PUBLIC_BASE_URL.rstrip('/')
        # Extrair o path após a porta
        import re
        path_match = re.search(r'(?:localhost|127\.0\.0\.1)(?::\d+)?(.+)', url)
        if path_match:
            path = path_match.group(1)
            return public_base + path
    return url


def save_outbound_message(
    db: Session,
    tenant_id: int,
    contact_id: int,
    channel_id: int,
    flow_id: int,
    content: str,
    message_type: str = 'text',
    flow_execution_id: int = None,
    step_id: int = None,
    auto_commit: bool = True,
):
    """Salva uma mensagem enviada pelo bot.
    Se auto_commit=False, apenas faz db.add() sem commit (caller agrupa)."""
    message = Message(
        tenant_id=tenant_id,
        contact_id=contact_id,
        channel_id=channel_id,
        flow_id=flow_id,
        flow_execution_id=flow_execution_id,
        step_id=step_id,
        direction='outbound',
        content=content,
        message_type=message_type,
        status='sent'
    )
    db.add(message)
    if auto_commit:
        db.flush()  # gera msg.id sem round-trip de commit completo
    return message


def contact_full_name(contact: Contact | None) -> str:
    if not contact:
        return ""

    parts = [contact.first_name, contact.last_name]
    return " ".join(part for part in parts if part).strip()


def execute_action(
    db: Session,
    action: Dict[str, Any],
    contact: Contact,
    channel: Channel,
    flow: Flow
):
    """Executa uma ação do tipo action step"""
    action_type = action.get("type")
    
    try:
        if action_type == "set_field":
            field_name = action.get("field_name", "").strip()
            raw_value = action.get("field_value") or action.get("value") or action.get("fieldValue") or ""
            field_value = personalize_text(raw_value, contact)

            # Campos nativos do modelo Contact (não vão para custom_fields)
            _SYSTEM_FIELDS = {"first_name", "last_name", "username"}

            if field_name:
                if field_name in _SYSTEM_FIELDS:
                    setattr(contact, field_name, field_value or None)
                    db.commit()
                    logger.info(f"   OK Set System Field: {field_name} = {field_value!r}")
                else:
                    # Campo personalizado → salva em custom_fields (JSON)
                    custom_fields = json.loads(contact.custom_fields) if isinstance(contact.custom_fields, str) else (contact.custom_fields or {})
                    custom_fields[field_name] = field_value
                    contact.custom_fields = json.dumps(custom_fields, ensure_ascii=False)
                    db.commit()
                    logger.info(f"   OK Set Field: {field_name} = {field_value}")
        
        elif action_type == "add_tag":
            tag_name = action.get("tag_name", "").strip()
            if tag_name:
                # Verificar se a tag já existe
                existing_tag = db.query(ContactTag).filter(
                    and_(
                        ContactTag.contact_id == contact.id,
                        ContactTag.tag_name == tag_name
                    )
                ).first()
                
                if not existing_tag:
                    new_tag = ContactTag(
                        tenant_id=contact.tenant_id,
                        contact_id=contact.id,
                        tag_name=tag_name
                    )
                    db.add(new_tag)
                    db.commit()
                    logger.info(f"   OK Add Tag: {tag_name}")
                else:
                    logger.info(f"   INFO Tag ja existe: {tag_name}")
        
        elif action_type == "remove_tag":
            tag_name = action.get("tag_name", "").strip()
            if tag_name:
                deleted = db.query(ContactTag).filter(
                    and_(
                        ContactTag.contact_id == contact.id,
                        ContactTag.tag_name == tag_name
                    )
                ).delete()
                db.commit()
                if deleted:
                    logger.info(f"   OK Remove Tag: {tag_name}")
                else:
                    logger.info(f"   INFO Tag nao encontrada: {tag_name}")
        
        elif action_type == "start_sequence":
            sequence_name = action.get("sequence_name", "").strip()
            if sequence_name:
                # Buscar sequência pelo nome
                sequence = db.query(Sequence).filter(
                    and_(
                        Sequence.tenant_id == contact.tenant_id,
                        Sequence.name == sequence_name,
                        Sequence.is_active == True
                    )
                ).first()
                
                if sequence:
                    # Verificar se já está inscrito
                    existing = db.query(ContactSequence).filter(
                        and_(
                            ContactSequence.contact_id == contact.id,
                            ContactSequence.sequence_id == sequence.id,
                            ContactSequence.status.in_(['active', 'paused'])
                        )
                    ).first()
                    
                    if not existing:
                        enrollment = ContactSequence(
                            tenant_id=contact.tenant_id,
                            contact_id=contact.id,
                            sequence_id=sequence.id,
                            status='active',
                            current_step=0,
                            next_execution_at=datetime.now()
                        )
                        db.add(enrollment)
                        db.commit()
                        logger.info(f"   OK Start Sequence: {sequence_name}")
                    else:
                        logger.info(f"   INFO Ja inscrito na sequence: {sequence_name}")
                else:
                    logger.warning(f"   WARN Sequence nao encontrada: {sequence_name}")
        
        elif action_type == "stop_sequence":
            sequence_name = action.get("sequence_name", "").strip()
            if sequence_name:
                # Buscar sequência pelo nome
                sequence = db.query(Sequence).filter(
                    and_(
                        Sequence.tenant_id == contact.tenant_id,
                        Sequence.name == sequence_name
                    )
                ).first()
                
                if sequence:
                    # Cancelar inscrição
                    updated = db.query(ContactSequence).filter(
                        and_(
                            ContactSequence.contact_id == contact.id,
                            ContactSequence.sequence_id == sequence.id,
                            ContactSequence.status.in_(['active', 'paused'])
                        )
                    ).update({
                        'status': 'cancelled',
                        'completed_at': datetime.now()
                    })
                    db.commit()
                    if updated:
                        logger.info(f"   OK Stop Sequence: {sequence_name}")
                    else:
                        logger.info(f"   INFO Nao inscrito na sequence: {sequence_name}")
                else:
                    logger.warning(f"   WARN Sequence nao encontrada: {sequence_name}")
        
        elif action_type == "go_to_flow":
            target_flow_id = action.get("flow_id")
            if target_flow_id:
                logger.info(f"   OK Go to Flow: {target_flow_id}")
                # Retornar código especial para interromper fluxo atual
                return {"action": "redirect_flow", "flow_id": target_flow_id}
        
        elif action_type == "go_to_step":
            target_step_id = action.get("step_id")
            if target_step_id:
                logger.info(f"   OK Go to Step: {target_step_id}")
                # Retornar código especial para pular para step específico
                return {"action": "redirect_step", "step_id": target_step_id}
        
        elif action_type == "smart_delay":
            delay_value = action.get("delay_value", 1)
            delay_unit = action.get("delay_unit", "minutes")
            
            # Converter para segundos
            if delay_unit == "minutes":
                seconds = delay_value * 60
            elif delay_unit == "hours":
                seconds = delay_value * 3600
            elif delay_unit == "days":
                seconds = delay_value * 86400
            else:
                seconds = delay_value * 60
            
            logger.info(f"   OK Smart Delay: {delay_value} {delay_unit} ({seconds}s)")
            time.sleep(min(seconds, 300))  # Máximo 5 minutos em execução síncrona
        
        elif action_type == "webhook":
            webhook_url = action.get("webhook_url", "").strip()
            method = action.get("method", "POST")
            headers_str = action.get("headers", "{}")
            
            if webhook_url:
                try:
                    headers = json.loads(headers_str) if headers_str else {}
                    
                    # Preparar payload com dados do contato
                    payload = {
                        "contact_id": contact.id,
                        "contact_name": contact_full_name(contact),
                        "contact_username": contact.username,
                        "flow_id": flow.id,
                        "flow_name": flow.name,
                        "channel_id": channel.id,
                        "channel_type": channel.type
                    }
                    
                    with httpx.Client(timeout=10.0) as client:
                        if method == "GET":
                            response = client.get(webhook_url, params=payload, headers=headers)
                        elif method == "PUT":
                            response = client.put(webhook_url, json=payload, headers=headers)
                        else:  # POST
                            response = client.post(webhook_url, json=payload, headers=headers)
                        
                        response.raise_for_status()
                        logger.info(f"   OK Webhook executado: {webhook_url} - Status: {response.status_code}")
                except Exception as e:
                    logger.error(f"   ERRO ao executar webhook {webhook_url}: {str(e)}")
        
        elif action_type == "notify_admin":
            notification_message = action.get("notification_message", "").strip()
            notify_tag = action.get("notify_tag", "").strip()

            if notification_message:
                personalized_msg = personalize_text(notification_message, contact)
                logger.info(f"   OK Notify Admin: {personalized_msg}")

                # Tentar enviar mensagem via Telegram para o chat_id do admin
                try:
                    channel_config = json.loads(channel.config) if channel.config else {}
                    admin_chat_id = channel_config.get("admin_telegram_chat_id", "").strip()
                    bot_token = channel_config.get("bot_token", "").strip()
                    if admin_chat_id and bot_token:
                        send_telegram_message(
                            bot_token=bot_token,
                            chat_id=admin_chat_id,
                            text=f"🔔 *Notificação Blackchat Pro*\n\n{personalized_msg}"
                        )
                        logger.info(f"   ✓ Mensagem de notificação enviada para admin ({admin_chat_id})")
                    else:
                        logger.warning("   ⚠️ notify_admin: admin_telegram_chat_id não configurado no canal")
                except Exception as e:
                    logger.error(f"   ERRO ao enviar notificação para admin: {e}")
            
            if notify_tag:
                # Adicionar tag automaticamente
                existing_tag = db.query(ContactTag).filter(
                    and_(
                        ContactTag.contact_id == contact.id,
                        ContactTag.tag_name == notify_tag
                    )
                ).first()
                
                if not existing_tag:
                    new_tag = ContactTag(
                        tenant_id=contact.tenant_id,
                        contact_id=contact.id,
                        tag_name=notify_tag
                    )
                    db.add(new_tag)
                    db.commit()
                    logger.info(f"   OK Add Tag (notify): {notify_tag}")
        
        else:
            logger.warning(f"   WARN Tipo de acao desconhecido: {action_type}")
    
    except Exception as e:
        logger.error(f"   ERRO ao executar acao {action_type}: {str(e)}")


def personalize_text(text: str, contact: Contact | None):
    if not text or not contact:
        return text

    full_name = contact_full_name(contact)

    placeholders = {
        "{primeiro_nome}": contact.first_name or "",
        "{sobrenome}": contact.last_name or "",
        "{nome_completo}": full_name,
        "{email}": "",
        "{celular}": "",
        "{contact_id}": str(contact.id),
        "{telegram_username}": contact.username or "",
        "{instagram_username}": "",
        "{ultima_mensagem}": "",
        "{username}": contact.username or ""
    }

    result = text
    for placeholder, value in placeholders.items():
        result = result.replace(placeholder, value)

    return result


def evaluate_condition(db: Session, condition_type: str, field_name: str, operator: str, expected_value: str, contact: Contact) -> bool:
    """
    Avalia uma condição baseada nos dados do contato
    
    Args:
        db: Sessão do banco
        condition_type: 'field', 'tag' ou 'variable'
        field_name: Nome do campo, tag ou variável
        operator: 'equals', 'not_equals', 'contains', 'not_contains', 'exists', 'not_exists', 'greater_than', 'less_than'
        expected_value: Valor esperado para comparação
        contact: Objeto do contato
        
    Returns:
        bool: True se a condição for satisfeita, False caso contrário
    """
    try:
        actual_value = None
        
        # Obter valor atual baseado no tipo de condição
        if condition_type == "field":
            # Buscar no custom_fields JSON
            if contact.custom_fields:
                try:
                    custom_fields = json.loads(contact.custom_fields) if isinstance(contact.custom_fields, str) else contact.custom_fields
                    actual_value = custom_fields.get(field_name)
                except json.JSONDecodeError:
                    logger.warning(f"Erro ao decodificar custom_fields do contato {contact.id}")
                    actual_value = None
        
        elif condition_type == "tag":
            # Verificar se o contato tem a tag
            tag_exists = db.query(ContactTag).filter(
                and_(
                    ContactTag.contact_id == contact.id,
                    ContactTag.tag_name == field_name
                )
            ).first() is not None
            actual_value = "true" if tag_exists else "false"
        
        elif condition_type == "variable":
            # Buscar variável do contato (atributos diretos)
            if field_name == "username":
                actual_value = contact.username
            elif field_name == "first_name":
                actual_value = contact.first_name
            elif field_name == "last_name":
                actual_value = contact.last_name
            elif field_name == "phone":
                actual_value = contact.phone
        
        # Avaliar operador
        if operator == "exists":
            return actual_value is not None and actual_value != ""
        
        elif operator == "not_exists":
            return actual_value is None or actual_value == ""
        
        # Para operadores que precisam de valor
        actual_str = str(actual_value) if actual_value is not None else ""
        expected_str = str(expected_value) if expected_value is not None else ""
        
        if operator == "equals":
            return actual_str.lower() == expected_str.lower()
        
        elif operator == "not_equals":
            return actual_str.lower() != expected_str.lower()
        
        elif operator == "contains":
            return expected_str.lower() in actual_str.lower()
        
        elif operator == "not_contains":
            return expected_str.lower() not in actual_str.lower()
        
        elif operator == "greater_than":
            try:
                return float(actual_str) > float(expected_str)
            except (ValueError, TypeError):
                return False
        
        elif operator == "less_than":
            try:
                return float(actual_str) < float(expected_str)
            except (ValueError, TypeError):
                return False
        
        else:
            logger.warning(f"Operador desconhecido: {operator}")
            return False
            
    except Exception as e:
        logger.error(f"Erro ao avaliar condição: {str(e)}")
        return False


def find_next_step_by_output(flow_config: dict, current_step_id: int, output_id: str, all_steps: list) -> FlowStep | None:
    """
    Encontra o próximo step baseado no output_id da conexão
    
    Args:
        flow_config: Configuração do flow (JSON)
        current_step_id: ID do step atual
        output_id: ID da saída ('true', 'false', ou ID do path do randomizer)
        all_steps: Lista de todos os steps do fluxo
        
    Returns:
        FlowStep ou None se não encontrar
    """
    try:
        connections = flow_config.get("connections", [])
        
        # Buscar conexão que sai do step atual com o output_id especificado
        for conn in connections:
            from_id = conn.get("from")
            to_id = conn.get("to")
            conn_output = conn.get("outputId")
            # Alguns edges (ex: trigger) não possuem outputId; trate como 'default'
            if conn_output is None or str(conn_output).strip() == "":
                conn_output = "default"

            if from_id == current_step_id and conn_output == output_id:
                next_step_id = conn.get("to")
                # Encontrar o step na lista
                for step in all_steps:
                    if step.id == next_step_id:
                        return step
        
        logger.debug(f"Próximo step não encontrado para step {current_step_id} output {output_id}")
        return None
        
    except Exception as e:
        logger.error(f"Erro ao buscar próximo step: {str(e)}")
        return None


def run_flow_background(channel_id: int, contact_id: int, flow_id: int, chat_id: int, bot_token: str, execution_id: int = None, start_from_step_id: int = None):
    """
    Executa fluxo em background com suporte a pausar/continuar
    
    Args:
        execution_id: ID da execução existente (para continuar)
        start_from_step_id: ID do step para começar (quando continuar)
    """
    db = SessionLocal()
    try:
        channel = db.query(Channel).filter(Channel.id == channel_id).first()
        contact = db.query(Contact).filter(Contact.id == contact_id).first()
        flow = db.query(Flow).filter(Flow.id == flow_id).first()

        if not channel or not contact or not flow:
            logger.warning("Dados incompletos para executar o fluxo em background")
            return

        # Validar se o canal está ativo
        if not channel.is_active:
            logger.warning(f"❌ Canal {channel.id} ({channel.name}) está INATIVO. Fluxo bloqueado.")
            send_telegram_message(
                bot_token=bot_token,
                chat_id=chat_id,
                text="⚠️ Este bot está temporariamente desativado. Entre em contato com o suporte."
            )
            return
        
        # Buscar ou criar execução
        if execution_id:
            flow_execution = db.query(FlowExecution).filter(FlowExecution.id == execution_id).first()
            logger.info(f"🔄 Continuando execução {execution_id}")
        else:
            flow_execution = None
        
        if not flow_execution:
            logger.warning(f"FlowExecution {execution_id} não encontrada")
            return

        # Inicializar logger de fluxo
        flow_logger = FlowLogger(db, flow_execution.id)
        
        # Registrar início ou continuação (APENAS se estiver continuando uma execução existente)
        if start_from_step_id and execution_id:
            # Verificar se a execução já tinha logs anteriores (é uma continuação real)
            previous_logs_count = db.query(FlowExecutionLog).filter(
                FlowExecutionLog.flow_execution_id == execution_id
            ).count()
            
            if previous_logs_count > 0:
                flow_logger.flow_resumed(start_from_step_id, "Retomada após resposta do usuário")
        
        if not start_from_step_id or not execution_id:
            flow_logger.info(f"Iniciando execução do fluxo: {flow.name}")

        steps = db.query(FlowStep).filter(
            FlowStep.flow_id == flow.id
        ).order_by(FlowStep.order_index).all()

        logger.info(f"🚀 Executando fluxo: {flow.id} - {flow.name}")
        
        # Carregar configuração do flow para ter acesso às conexões
        flow_config = json.loads(flow.config) if flow.config else {}
        has_connections = bool(flow_config.get("connections"))
        
        # Determinar step inicial
        if start_from_step_id:
            step_index = next((i for i, s in enumerate(steps) if s.id == start_from_step_id), 0)
        else:
            step_index = 0
        
        # Execução com suporte a múltiplas saídas
        while step_index < len(steps):
            step = steps[step_index]
            logger.info(f"🔄 Processando step: {step.id} (tipo: {step.type}, ordem: {step.order_index})")
            
            # Registrar início do step
            step_config = json.loads(step.config) if step.config else {}
            flow_logger.step_start(step.id, step.type, step_config)
            
            if flow_execution:
                flow_execution.current_step_id = step.id
                db.commit()
            
            try:
                next_step = None  # Para blocos com múltiplas saídas
                
                # ============= BLOCO TRIGGER (ignorar) =============
                if step.type == "trigger":
                    # Se o flow usa connections, siga o próximo edge do trigger.
                    if has_connections:
                        next_step = find_next_step_by_output(flow_config, step.id, "default", steps)
                        if not next_step:
                            # fallback: pegar o primeiro edge que sair do trigger
                            for conn in flow_config.get("connections", []) or []:
                                if conn.get("from") == step.id and conn.get("to") is not None:
                                    next_step_id = conn.get("to")
                                    next_step = next((s for s in steps if s.id == next_step_id), None)
                                    if next_step:
                                        break
                        if next_step:
                            step_index = steps.index(next_step)
                            continue
                        # sem saída do trigger: encerra
                        break

                    step_index += 1
                    continue

                # ============= BLOCO CONDIÇÃO =============
                if step.type == "condition":
                    condition_type = step_config.get("conditionType", "field")
                    field_name = step_config.get("field", "")
                    operator = step_config.get("operator", "equals")
                    expected_value = step_config.get("value", "")
                    
                    logger.info(f"   🔀 Avaliando condição: {condition_type}.{field_name} {operator} {expected_value}")
                    
                    # Avaliar condição
                    result = evaluate_condition(db, condition_type, field_name, operator, expected_value, contact)
                    output_id = "true" if result else "false"
                    
                    # Registrar avaliação da condição
                    flow_logger.condition_evaluated(step.id, result, None)
                    
                    logger.info(f"   ✓ Resultado: {output_id}")
                    
                    # Buscar próximo step baseado no resultado
                    next_step = find_next_step_by_output(flow_config, step.id, output_id, steps)
                    if next_step:
                        step_index = steps.index(next_step)
                        continue
                    else:
                        logger.warning(f"   ⚠️ Nenhum próximo step encontrado para saída '{output_id}', continuando fluxo")
                        step_index += 1
                        continue
                
                # ============= BLOCO RANDOMIZADOR =============
                elif step.type == "randomizer":
                    paths = step_config.get("paths", [])
                    
                    if not paths:
                        logger.warning(f"   ⚠️ Randomizer sem paths configurados")
                        step_index += 1
                        continue
                    
                    # Extrair paths e percentuais
                    path_ids = [p.get("id") for p in paths]
                    percentages = [p.get("percentage", 0) for p in paths]
                    
                    # Selecionar path aleatório baseado nos percentuais
                    selected_path = random.choices(path_ids, weights=percentages, k=1)[0]
                    
                    logger.info(f"   🎲 Randomizer selecionou path: {selected_path} (opções: {len(paths)})")
                    
                    # Buscar próximo step baseado no path selecionado
                    next_step = find_next_step_by_output(flow_config, step.id, selected_path, steps)
                    if next_step:
                        step_index = steps.index(next_step)
                        continue
                    else:
                        logger.warning(f"   ⚠️ Nenhum próximo step encontrado para path '{selected_path}', continuando fluxo")
                        step_index += 1
                        continue
                
                # ============= BLOCO ATRASO INTELIGENTE =============
                elif step.type == "wait":
                    delay_type = step_config.get("delayType", "fixed")
                    
                    if delay_type == "fixed":
                        value = step_config.get("value", 1)
                        unit = step_config.get("unit", "minutes")
                        
                        # Converter para segundos
                        if unit == "seconds":
                            seconds = value
                        elif unit == "minutes":
                            seconds = value * 60
                        elif unit == "hours":
                            seconds = value * 3600
                        elif unit == "days":
                            seconds = value * 86400
                        else:
                            seconds = value * 60
                        
                        logger.info(f"   ⏱️ Delay fixo: {value} {unit} ({seconds}s)")
                        time.sleep(min(seconds, 300))  # Máximo 5 minutos em execução síncrona
                    
                    elif delay_type == "random":
                        min_val = step_config.get("randomMin", 1)
                        max_val = step_config.get("randomMax", 5)
                        unit = step_config.get("randomUnit", "minutes")
                        
                        # Gerar valor aleatório
                        random_value = random.randint(min_val, max_val)
                        
                        # Converter para segundos
                        if unit == "seconds":
                            seconds = random_value
                        elif unit == "minutes":
                            seconds = random_value * 60
                        elif unit == "hours":
                            seconds = random_value * 3600
                        elif unit == "days":
                            seconds = random_value * 86400
                        else:
                            seconds = random_value * 60
                        
                        logger.info(f"   🎲 Delay aleatório: {random_value} {unit} ({seconds}s)")
                        time.sleep(min(seconds, 300))
                    
                    elif delay_type == "smart":
                        # Delay inteligente: aguardar até horário comercial
                        now = datetime.now()
                        
                        # Se for fim de semana, pular para segunda
                        if now.weekday() >= 5:  # 5=Saturday, 6=Sunday
                            days_until_monday = 7 - now.weekday()
                            next_business_day = now + timedelta(days=days_until_monday)
                            next_business_day = next_business_day.replace(hour=9, minute=0, second=0)
                        # Se for fora do horário comercial (9h-18h)
                        elif now.hour < 9:
                            next_business_day = now.replace(hour=9, minute=0, second=0)
                        elif now.hour >= 18:
                            next_business_day = now + timedelta(days=1)
                            next_business_day = next_business_day.replace(hour=9, minute=0, second=0)
                        else:
                            # Já está em horário comercial
                            next_business_day = now
                        
                        seconds = (next_business_day - now).total_seconds()
                        logger.info(f"   🧠 Delay inteligente: aguardar até {next_business_day} ({seconds}s)")
                        time.sleep(min(seconds, 300))
                    
                    step_index += 1
                    continue
                
                # ============= BLOCO INICIAR AUTOMAÇÃO =============
                elif step.type == "start_automation":
                    target_flow_id = step_config.get("flowId")
                    
                    if target_flow_id:
                        logger.info(f"   🔄 Iniciando automação: flow {target_flow_id}")
                        
                        # Buscar flow de destino
                        target_flow = db.query(Flow).filter(Flow.id == target_flow_id).first()
                        
                        if target_flow:
                            # Executar novo fluxo recursivamente
                            run_flow_background(channel.id, contact.id, target_flow_id, chat_id, bot_token)
                            logger.info(f"   ✓ Automação {target_flow.name} iniciada")
                        else:
                            logger.warning(f"   ⚠️ Flow de destino {target_flow_id} não encontrado")
                        
                        # Continuar execução do fluxo atual
                        step_index += 1
                        continue
                    else:
                        logger.warning(f"   ⚠️ Start automation sem flowId configurado")
                        step_index += 1
                        continue
                
                # ============= BLOCO COMENTÁRIO (não faz nada) =============
                elif step.type == "comment":
                    comment_text = step_config.get("text", "")
                    logger.info(f"   💬 Comentário: {comment_text[:50]}...")
                    step_index += 1
                    continue
                
                # ============= PROCESSAR STEPS DE AÇÃO =============
                elif step.type == "action":
                    actions = step_config.get("actions", [])
                    if not actions:
                        logger.warning(f"Step {step.id} nao tem acoes, pulando...")
                        step_index += 1
                        continue
                    
                    logger.info(f"   Executando {len(actions)} acao(oes)")
                    should_wait_for_response = False
                    waiting_field = None
                    
                    # PRIMEIRO: Verificar se alguma ação precisa aguardar resposta
                    for action in actions:
                        action_type = action.get("type")
                        logger.info(f"   🔎 Action debug: {action}")
                        
                        if action_type == "set_field":
                            # Verificar chaves possíveis (field_value, value, fieldValue)
                            field_value = action.get("field_value") or action.get("value") or action.get("fieldValue") or ""
                            field_value_str = str(field_value)
                            logger.info(f"   🔎 set_field value: {field_value_str}")
                            # Se o valor contém {ultima_mensagem}, significa que aguarda input
                            if field_value_str and ("ultima_mensagem" in field_value_str or "last_message" in field_value_str):
                                should_wait_for_response = True
                                waiting_field = action.get("field_name")
                                logger.info(f"   ⏸️ Ação aguarda resposta do usuário para campo: {waiting_field}")
                                break  # Não precisa verificar mais ações
                    
                    # Se deve aguardar resposta, pausar ANTES de executar ações
                    if should_wait_for_response and waiting_field:
                        logger.info(f"   ⏸️ PAUSANDO fluxo para aguardar resposta do usuário")
                        
                        # Registrar pausa do fluxo
                        flow_logger.flow_paused(step.id, "Aguardando resposta do usuário", waiting_field)
                        
                        # Atualizar FlowExecution para aguardar resposta
                        flow_execution.status = 'waiting_response'
                        flow_execution.current_step_id = step.id
                        flow_execution.context = json.dumps({
                            "waiting_for_field": waiting_field,
                            "next_step_index": step_index + 1,
                            "channel_id": channel.id,
                            "chat_id": chat_id,
                            "bot_token": bot_token
                        })
                        db.commit()
                        
                        logger.info(f"   ✓ Execução {flow_execution.id} aguardando resposta para campo '{waiting_field}'")
                        return  # Parar execução aqui
                    
                    # SEGUNDO: Executar as ações normalmente
                    for action in actions:
                        action_type = action.get("type")
                        result = execute_action(db, action, contact, channel, flow)
                        
                        # Registrar ação executada
                        flow_logger.action_executed(step.id, action_type, result if isinstance(result, dict) else None)
                        
                        # Verificar se há redirecionamento
                        if result and isinstance(result, dict):
                            if result.get("action") == "redirect_flow":
                                target_flow_id = result.get("flow_id")
                                logger.info(f"Redirecionando para flow {target_flow_id}")
                                target_flow = db.query(Flow).filter(Flow.id == target_flow_id).first()
                                if target_flow:
                                    run_flow_background(channel.id, contact.id, target_flow_id, chat_id, bot_token)
                                return
                            
                            elif result.get("action") == "redirect_step":
                                target_step_id = result.get("step_id")
                                logger.info(f"Pulando para step {target_step_id}")
                                target_step = next((s for s in steps if s.id == target_step_id), None)
                                if target_step:
                                    step_index = steps.index(target_step)
                                break
                    
                    if has_connections:
                        next_step = find_next_step_by_output(flow_config, step.id, "default", steps)
                        if next_step:
                            step_index = steps.index(next_step)
                            continue
                        break

                    step_index += 1
                    continue
                
                # ============= PROCESSAR STEPS DE MENSAGEM =============
                # (tipo padrão ou 'message')
                else:
                    blocks = step_config.get("blocks", [])

                    if len(blocks) == 0:
                        logger.warning(f"Step {step.id} não tem blocos, pulando...")
                        step_index += 1
                        continue

                    for idx, block in enumerate(blocks):
                        block_type = block.get("type")
                        block_text = block.get("text", "")
                        logger.info(f"   [{idx+1}/{len(blocks)}] Tipo: {block_type}")

                        if block_type == "text":
                            if block_text:
                                personalized_text = personalize_text(block_text, contact)
                                send_telegram_message(
                                    bot_token=bot_token,
                                    chat_id=chat_id,
                                    text=personalized_text
                                )
                                msg = save_outbound_message(
                                    db=db,
                                    tenant_id=channel.tenant_id,
                                    contact_id=contact.id,
                                    channel_id=channel.id,
                                    flow_id=flow.id,
                                    content=personalized_text,
                                    message_type='text',
                                    flow_execution_id=flow_execution.id,
                                    step_id=step.id
                                )
                                flow_logger.message_sent(step.id, msg.id, personalized_text)
                        elif block_type == "delay":
                            seconds = block.get("seconds", 3)
                            logger.info(f"Delay de {seconds}s")
                            time.sleep(seconds)
                        elif block_type == "image":
                            image_url = normalize_media_url(block.get("url", ""))
                            caption = block.get("caption", "")
                            if image_url:
                                result = send_telegram_photo(
                                    bot_token=bot_token,
                                    chat_id=chat_id,
                                    photo_url=image_url,
                                    caption=caption
                                )
                                if result:
                                    msg = save_outbound_message(
                                        db=db,
                                        tenant_id=channel.tenant_id,
                                        contact_id=contact.id,
                                        channel_id=channel.id,
                                        flow_id=flow.id,
                                        content=image_url,
                                        message_type='image',
                                        flow_execution_id=flow_execution.id,
                                        step_id=step.id
                                    )
                                    flow_logger.message_sent(step.id, msg.id, f"Image: {image_url}")
                        elif block_type == "audio":
                            audio_url = normalize_media_url(block.get("url", ""))
                            title = block.get("title", "")
                            if audio_url:
                                send_telegram_audio(
                                    bot_token=bot_token,
                                    chat_id=chat_id,
                                    audio_url=audio_url,
                                    title=title
                                )
                                msg = save_outbound_message(
                                    db=db,
                                    tenant_id=channel.tenant_id,
                                    contact_id=contact.id,
                                    channel_id=channel.id,
                                    flow_id=flow.id,
                                    content=audio_url,
                                    message_type='audio',
                                    flow_execution_id=flow_execution.id,
                                    step_id=step.id
                                )
                                flow_logger.message_sent(step.id, msg.id, f"Audio: {title or audio_url}")
                        elif block_type == "video":
                            video_url = normalize_media_url(block.get("url", ""))
                            title = block.get("title", "")
                            is_video_note = block.get("is_video_note", False)  # Nova opção
                            
                            print(f"🎥 Processando bloco de vídeo:")
                            print(f"   URL: {video_url}")
                            print(f"   Título: {title}")
                            print(f"   É vídeo bolinha? {is_video_note}")
                            
                            if video_url:
                                if is_video_note:
                                    # Enviar como vídeo bolinha (sem legenda)
                                    print(f"🔵 Enviando como VÍDEO BOLINHA")
                                    print(f"   Token: {bot_token[:20]}...")
                                    print(f"   Chat ID: {chat_id}")
                                    print(f"   Video URL: {video_url}")
                                    
                                    result = send_telegram_video_note(
                                        bot_token=bot_token,
                                        chat_id=chat_id,
                                        video_url=video_url
                                    )
                                    
                                    if result:
                                        print(f"✅ Vídeo bolinha enviado com sucesso!")
                                    else:
                                        print(f"❌ ERRO ao enviar vídeo bolinha!")
                                else:
                                    # Enviar como vídeo normal (com legenda)
                                    print(f"🎬 Enviando como VÍDEO NORMAL")
                                    send_telegram_video(
                                        bot_token=bot_token,
                                        chat_id=chat_id,
                                        video_url=video_url,
                                        caption=title
                                    )
                                
                                msg = save_outbound_message(
                                    db=db,
                                    tenant_id=channel.tenant_id,
                                    contact_id=contact.id,
                                    channel_id=channel.id,
                                    flow_id=flow.id,
                                    content=video_url,
                                    message_type='video_note' if is_video_note else 'video',
                                    flow_execution_id=flow_execution.id,
                                    step_id=step.id
                                )
                                flow_logger.message_sent(step.id, msg.id, f"Video: {video_url}")
                        elif block_type == "button":
                            button_text = block.get("text", "").strip()
                            buttons = block.get("buttons", [])
                            block_id = block.get("id", "")
                            step_id_str = str(step.id)

                            # ── Pré-determinar se este bloco deve pausar o fluxo ──────────
                            # Prioridade: (1) conexões visuais do canvas, (2) targetStepId no config do botão
                            # As conexões são a fonte mais confiável (sempre atualizadas pelo saveWorkflow)
                            btn_has_flow_connection = has_connections and any(
                                str(c.get("from", "")) == step_id_str and
                                str(c.get("outputId", "")).startswith("btn-")
                                for c in flow_config.get("connections", [])
                            )
                            should_pause_for_buttons = btn_has_flow_connection or any(
                                b.get("action") == "flow" and b.get("targetStepId")
                                for b in buttons
                            )
                            logger.info(f"   🔘 Button block: block_id={block_id!r} buttons={len(buttons)} should_pause={should_pause_for_buttons} has_flow_conn={btn_has_flow_connection}")

                            if buttons:
                                inline_keyboard = []
                                for btn_idx, btn in enumerate(buttons):
                                    btn_text = btn.get("text", "")
                                    btn_action = btn.get("action") or "url"  # None-safe default
                                    btn_url = btn.get("url", "") or ""

                                    # SEMPRE priorizar conexões visuais do canvas para resolver targetStepId.
                                    # O targetStepId no config pode estar desatualizado (ex: ID da IA antes do remapeamento).
                                    btn_target_step_id = ""
                                    if btn_action == "flow" and has_connections:
                                        port_output_id = f"btn-{block_id}-{btn_idx}"
                                        conn_match = next(
                                            (c for c in flow_config.get("connections", [])
                                             if str(c.get("from", "")) == step_id_str
                                             and c.get("outputId") == port_output_id),
                                            None
                                        )
                                        if conn_match:
                                            btn_target_step_id = conn_match.get("to")
                                            logger.info(f"   🔗 targetStepId via conexão: btn {btn_idx} → step {btn_target_step_id}")

                                    # Fallback: usar targetStepId do config do botão
                                    if btn_action == "flow" and not btn_target_step_id:
                                        btn_target_step_id = btn.get("targetStepId") or ""
                                        if btn_target_step_id:
                                            logger.info(f"   🔗 targetStepId via config: btn {btn_idx} → step {btn_target_step_id}")
                                        else:
                                            logger.warning(f"   ⚠️ btn {btn_idx} action=flow mas sem target. block_id={block_id!r} port=btn-{block_id}-{btn_idx}")
                                            for c in flow_config.get("connections", []):
                                                logger.warning(f"      conn: from={c.get('from')!r}({type(c.get('from')).__name__}) outputId={c.get('outputId')!r} to={c.get('to')!r}")

                                    if not btn_text:
                                        continue

                                    if btn_action == "flow" and btn_target_step_id:
                                        inline_keyboard.append([{
                                            "text": personalize_text(btn_text, contact),
                                            "callback_data": f"goto_step:{btn_target_step_id}"
                                        }])
                                    elif btn_action == "url" and btn_url:
                                        inline_keyboard.append([{
                                            "text": personalize_text(btn_text, contact),
                                            "url": btn_url
                                        }])

                                if inline_keyboard:
                                    reply_markup = {"inline_keyboard": inline_keyboard}
                                    personalized_button_text = personalize_text(button_text, contact) if button_text else ""
                                    send_telegram_message(
                                        bot_token=bot_token,
                                        chat_id=chat_id,
                                        text=personalized_button_text,
                                        reply_markup=reply_markup
                                    )
                                    msg = save_outbound_message(
                                        db=db,
                                        tenant_id=channel.tenant_id,
                                        contact_id=contact.id,
                                        channel_id=channel.id,
                                        flow_id=flow.id,
                                        content=personalized_button_text if button_text else "[Botões]",
                                        message_type='button',
                                        flow_execution_id=flow_execution.id,
                                        step_id=step.id
                                    )
                                    flow_logger.message_sent(step.id, msg.id, "Buttons message")

                                # ── Pausar — só quando há botões flow reais ──────────────
                                if should_pause_for_buttons and flow_execution:
                                    from datetime import timezone
                                    _UNIT_SECONDS = {"seconds": 1, "minutes": 60, "hours": 3600, "days": 86400}
                                    _DEFAULT_TIMEOUT_SECONDS = 48 * 3600  # 48h padrão (CRM best-practice)

                                    timeout_deadline = None
                                    timeout_source = "default_48h"
                                    try:
                                        default_next = find_next_step_by_output(flow_config, step.id, "default", steps)
                                        if default_next and default_next.type == "wait":
                                            wait_cfg = json.loads(default_next.config) if default_next.config else {}
                                            if wait_cfg.get("delayType", "fixed") == "fixed":
                                                val = int(wait_cfg.get("value", 0))
                                                unit = wait_cfg.get("unit", "minutes")
                                                seconds = _UNIT_SECONDS.get(unit, 60) * val
                                                if seconds > 0:
                                                    deadline_dt = datetime.now(timezone.utc) + timedelta(seconds=seconds)
                                                    timeout_deadline = deadline_dt.isoformat()
                                                    timeout_source = f"wait_step ({val} {unit})"
                                    except Exception as te:
                                        logger.warning(f"   Falha ao calcular timeout de botão: {te}")

                                    # Fallback: timeout padrão de 48h se não houver step "Espera"
                                    if not timeout_deadline:
                                        deadline_dt = datetime.now(timezone.utc) + timedelta(seconds=_DEFAULT_TIMEOUT_SECONDS)
                                        timeout_deadline = deadline_dt.isoformat()

                                    flow_execution.status = 'waiting_response'
                                    flow_execution.context = json.dumps({
                                        "waiting_for": "button_click",
                                        "channel_id": channel.id,
                                        "chat_id": chat_id,
                                        "bot_token": bot_token,
                                        "step_id": step.id,
                                        "timeout_deadline": timeout_deadline,
                                    })
                                    db.commit()
                                    logger.info(f"   ⏸ Execução {flow_execution.id} pausada aguardando botão | timeout={timeout_source} | deadline={timeout_deadline}")
                                    return
                            elif button_text:
                                # Bloco button sem botões (buttons=[]) mas com texto → envia como mensagem simples
                                personalized_button_text = personalize_text(button_text, contact)
                                send_telegram_message(
                                    bot_token=bot_token,
                                    chat_id=chat_id,
                                    text=personalized_button_text
                                )
                                msg = save_outbound_message(
                                    db=db,
                                    tenant_id=channel.tenant_id,
                                    contact_id=contact.id,
                                    channel_id=channel.id,
                                    flow_id=flow.id,
                                    content=personalized_button_text,
                                    message_type='text',
                                    flow_execution_id=flow_execution.id,
                                    step_id=step.id
                                )
                                flow_logger.message_sent(step.id, msg.id, "Button-block sem botões → texto simples")
                        elif block_type == "data":
                            prompt = block.get("prompt", "")
                            if prompt:
                                send_telegram_message(
                                    bot_token=bot_token,
                                    chat_id=chat_id,
                                    text=prompt
                                )

                            # Se houver execução ativa, pausar aguardando resposta (bloco data é um prompt de input)
                            if flow_execution:
                                waiting_field = block.get("field") or block.get("field_name") or block.get("fieldName")
                                next_step = steps[step_index + 1] if (step_index + 1 < len(steps)) else None

                                pause_step_id = step.id
                                next_step_index = step_index + 1

                                # Se existir um próximo step de action que captura {ultima_mensagem}, pausar nele
                                # (assim a rotina de continuação sabe pular set_field placeholder).
                                if waiting_field and next_step and next_step.type == "action":
                                    try:
                                        next_config = json.loads(next_step.config) if next_step.config else {}
                                        next_actions = next_config.get("actions", [])

                                        has_placeholder_capture = False
                                        for action in next_actions:
                                            if action.get("type") != "set_field":
                                                continue
                                            field_value = action.get("field_value") or action.get("value") or action.get("fieldValue") or ""
                                            if field_value and ("ultima_mensagem" in str(field_value) or "last_message" in str(field_value)):
                                                has_placeholder_capture = True
                                                break

                                        if has_placeholder_capture:
                                            pause_step_id = next_step.id
                                            next_step_index = step_index + 2
                                    except Exception as e:
                                        logger.error(f"Erro ao inspecionar ação de captura (data block): {e}")

                                # Fallback legado: se não veio field no bloco, inferir pelo próximo action set_field
                                if not waiting_field and next_step and next_step.type == "action":
                                    try:
                                        next_config = json.loads(next_step.config) if next_step.config else {}
                                        next_actions = next_config.get("actions", [])
                                        for action in next_actions:
                                            if action.get("type") != "set_field":
                                                continue
                                            field_value = action.get("field_value") or action.get("value") or action.get("fieldValue") or ""
                                            if field_value and ("ultima_mensagem" in str(field_value) or "last_message" in str(field_value)):
                                                waiting_field = action.get("field_name")
                                                pause_step_id = next_step.id
                                                next_step_index = step_index + 2
                                                break
                                    except Exception as e:
                                        logger.error(f"Erro ao inspecionar ação de captura: {e}")

                                if waiting_field:
                                    flow_execution.status = 'waiting_response'
                                    flow_execution.current_step_id = pause_step_id
                                    flow_execution.context = json.dumps({
                                        "waiting_for_field": waiting_field,
                                        "next_step_index": next_step_index,
                                        "channel_id": channel.id,
                                        "chat_id": chat_id,
                                        "bot_token": bot_token
                                    })
                                    db.commit()
                                    logger.info(
                                        f"   ✓ Execução {flow_execution.id} aguardando resposta para campo '{waiting_field}' (data block)"
                                    )
                                    return

                    # Se o próximo step for ação com captura de resposta, pausar AQUI (depois de enviar todas as mensagens)
                    if flow_execution and (step_index + 1) < len(steps):
                        next_step = steps[step_index + 1]
                        if next_step.type == "action":
                            try:
                                next_config = json.loads(next_step.config) if next_step.config else {}
                                next_actions = next_config.get("actions", [])
                                waiting_field = None
                                for action in next_actions:
                                    if action.get("type") == "set_field":
                                        field_value = action.get("field_value") or action.get("value") or action.get("fieldValue") or ""
                                        if field_value and ("ultima_mensagem" in str(field_value) or "last_message" in str(field_value)):
                                            waiting_field = action.get("field_name")
                                            break
                                if waiting_field:
                                    flow_execution.status = 'waiting_response'
                                    flow_execution.current_step_id = next_step.id
                                    flow_execution.context = json.dumps({
                                        "waiting_for_field": waiting_field,
                                        "next_step_index": step_index + 2,
                                        "channel_id": channel.id,
                                        "chat_id": chat_id,
                                        "bot_token": bot_token
                                    })
                                    db.commit()
                                    logger.info(f"   ✓ Execução {flow_execution.id} aguardando resposta para campo '{waiting_field}'")
                                    return
                            except Exception as e:
                                logger.error(f"Erro ao preparar pausa pós-mensagem: {e}")

                    # Avançar para o próximo step
                    # Se o fluxo possui conexões, a ordem por order_index NÃO deve ser usada para navegar.
                    # Isso evita executar os dois ramos de um condition (true/false) quando os steps estão em sequência.
                    if has_connections:
                        next_step = find_next_step_by_output(flow_config, step.id, "default", steps)
                        if next_step:
                            step_index = steps.index(next_step)
                            continue
                        break

                    step_index += 1
                    continue
                    
            except json.JSONDecodeError:
                logger.error(f"Config do step {step.id} inválido")
                step_index += 1
            except Exception as e:
                logger.error(f"Erro ao processar step {step.id} em background: {e}")
                step_index += 1
        
        # Fluxo concluído - marcar como completo
        if flow_execution:
            flow_execution.status = 'completed'
            flow_execution.completed_at = datetime.now()
            flow_execution.current_step_id = None
            flow_execution.context = None
            db.commit()
            logger.info(f"✅ Fluxo {flow.name} concluído para contato {contact.id}")
    
    finally:
        db.close()


def check_timed_out_executions():
    """
    Verifica execuções pausadas (waiting_response) com timeout expirado e as avança
    via a saída default do step que as pausou (ignorando o wait step, pois o tempo já passou).
    Chamado periodicamente pela thread de fundo iniciada no startup da aplicação.
    """
    from datetime import timezone
    db = SessionLocal()
    try:
        waiting_execs = db.query(FlowExecution).filter(
            FlowExecution.status == 'waiting_response'
        ).all()

        if not waiting_execs:
            return

        now_iso = datetime.now(timezone.utc).isoformat()

        for ex in waiting_execs:
            try:
                ctx = json.loads(ex.context) if ex.context else {}
                if ctx.get("waiting_for") != "button_click":
                    continue
                deadline = ctx.get("timeout_deadline")
                if not deadline or now_iso < deadline:
                    continue  # sem deadline ou ainda não expirou

                bot_token  = ctx.get("bot_token")
                chat_id    = ctx.get("chat_id")
                channel_id = ctx.get("channel_id")
                paused_step_id = ctx.get("step_id")

                if not all([bot_token, chat_id, channel_id, paused_step_id]):
                    logger.warning(f"timeout_checker: contexto incompleto para exec {ex.id}")
                    continue

                flow = db.query(Flow).filter(Flow.id == ex.flow_id).first()
                if not flow:
                    ex.status = 'completed'
                    ex.completed_at = datetime.now()
                    ex.context = None
                    db.commit()
                    continue

                flow_config = json.loads(flow.config) if flow.config else {}
                all_steps = db.query(FlowStep).filter(
                    FlowStep.flow_id == flow.id
                ).order_by(FlowStep.order_index).all()

                # Próximo step via saída default do step que estava pausado
                next_step = find_next_step_by_output(flow_config, paused_step_id, "default", all_steps)

                if not next_step:
                    logger.info(f"timeout_checker: exec {ex.id} sem saída default, encerrando.")
                    ex.status = 'completed'
                    ex.completed_at = datetime.now()
                    ex.context = None
                    db.commit()
                    continue

                # Se o próximo step for o wait que gerou o timeout, pular para o step APÓS ele
                start_step_id = next_step.id
                if next_step.type == "wait":
                    after_wait = find_next_step_by_output(flow_config, next_step.id, "default", all_steps)
                    if after_wait:
                        start_step_id = after_wait.id
                    else:
                        logger.info(f"timeout_checker: exec {ex.id} sem step após wait, encerrando.")
                        ex.status = 'completed'
                        ex.completed_at = datetime.now()
                        ex.context = None
                        db.commit()
                        continue

                ex.status = 'running'
                ex.context = None
                db.commit()

                logger.info(
                    f"⏰ timeout_checker: avançando exec {ex.id} (flow {ex.flow_id}) "
                    f"via default → step {start_step_id}"
                )

                import threading as _threading
                _threading.Thread(
                    target=run_flow_background,
                    kwargs=dict(
                        channel_id=int(channel_id),
                        contact_id=ex.contact_id,
                        flow_id=ex.flow_id,
                        chat_id=int(chat_id),
                        bot_token=bot_token,
                        execution_id=ex.id,
                        start_from_step_id=start_step_id,
                    ),
                    daemon=True,
                ).start()

            except Exception as e:
                logger.error(f"timeout_checker: erro ao processar exec {ex.id}: {e}")
    finally:
        db.close()


def _handle_telegram_update(update: dict, webhook_secret: str, db: Session) -> dict:
    """
    Processa um update do Telegram de forma síncrona.
    Chamado diretamente quando ARQ está offline (fallback), ou pelo worker process_webhook.
    """
    import time as _time
    _t0 = _time.perf_counter()
    def _checkpoint(label):
        print(f"[PERF] {label}: {_time.perf_counter() - _t0:.3f}s", flush=True)

    print("=" * 80)
    print(f"📨 WEBHOOK RECEBIDO: {webhook_secret}")
    print(f"📦 Update: {update}")
    print("=" * 80)
    logger.info(f"Recebido update do Telegram para webhook_secret={webhook_secret}")
    
    # 1. Identificar o canal pelo webhook_secret (query direta indexada)
    channel = db.query(Channel).filter(
        Channel.type == "telegram",
        Channel.webhook_secret == webhook_secret
    ).first()
    _checkpoint("1-query-channel")

    # Fallback para canais sem webhook_secret desnormalizado (legado)
    if not channel:
        for ch in db.query(Channel).filter(Channel.type == "telegram", Channel.webhook_secret == None).all():
            try:
                config = json.loads(ch.config) if ch.config else {}
                if config.get("webhook_secret") == webhook_secret:
                    # Preencher coluna desnormalizada para próximas vezes
                    ch.webhook_secret = webhook_secret
                    db.commit()
                    channel = ch
                    break
            except json.JSONDecodeError:
                continue

    if not channel:
        logger.warning(f"Canal não encontrado para webhook_secret={webhook_secret}")
        raise HTTPException(status_code=404, detail="Canal não encontrado")
    
    # Verificar se o canal está ativo
    if not channel.is_active:
        logger.warning(f"❌ Canal {channel.id} ({channel.name}) está INATIVO. Webhook bloqueado.")
        print(f"⚠️ Canal INATIVO - mensagens bloqueadas")
        
        # Enviar mensagem informando que o bot está inativo
        try:
            config = json.loads(channel.config) if channel.config else {}
            bot_token = config.get("bot_token")
            
            if bot_token and update.get("message", {}).get("chat", {}).get("id"):
                chat_id = update["message"]["chat"]["id"]
                send_telegram_message(
                    bot_token=bot_token,
                    chat_id=chat_id,
                    text="⚠️ Este bot está temporariamente desativado. Entre em contato com o suporte."
                )
        except Exception as e:
            logger.error(f"Erro ao enviar mensagem de bot inativo: {e}")
        
        return {"status": "ok", "message": "Channel inactive"}
    
    # Carregar config do canal
    try:
        channel_config = json.loads(channel.config)
        bot_token = channel_config.get("bot_token")
    except (json.JSONDecodeError, KeyError):
        logger.error("Config do canal inválido")
        raise HTTPException(status_code=500, detail="Configuração do canal inválida")
    
    # 2. Extrair dados do update
    message = update.get("message")

    # ============= CALLBACK QUERY (clique em botão inline) =============
    callback_query = update.get("callback_query")
    if callback_query and not message:
        _checkpoint("cb-start")
        cq_id = callback_query.get("id")
        cq_data = callback_query.get("data", "")
        cq_from = callback_query.get("from", {})
        cq_message = callback_query.get("message", {})
        cq_chat_id = cq_message.get("chat", {}).get("id")
        cq_user_id = cq_from.get("id")

        # Recuperar o texto do botão clicado a partir do reply_markup da mensagem original
        btn_label = ""
        try:
            inline_kb = cq_message.get("reply_markup", {}).get("inline_keyboard", [])
            for row in inline_kb:
                for btn in row:
                    if btn.get("callback_data") == cq_data:
                        btn_label = btn.get("text", "")
                        break
                if btn_label:
                    break
        except Exception:
            pass

        # Responder o callback (remove o "relógio" no Telegram) e mostrar o texto selecionado
        try:
            import httpx
            httpx.post(
                f"https://api.telegram.org/bot{bot_token}/answerCallbackQuery",
                json={
                    "callback_query_id": cq_id,
                    "text": f"✅ {btn_label}" if btn_label else "✅",
                    "show_alert": False,
                },
                timeout=5
            )
        except Exception:
            pass

        # Nota: não enviamos btn_label como sendMessage porque isso viria do BOT (lado esquerdo),
        # o que confunde o usuário. O popup do answerCallbackQuery já é feedback suficiente.

        if cq_data.startswith("goto_step:") and cq_chat_id and cq_user_id:
            target_step_id_str = cq_data.split("goto_step:", 1)[1]
            try:
                target_step_id = int(target_step_id_str)
            except ValueError:
                logger.warning(f"callback_data inválido: {cq_data}")
                return {"status": "ok"}

            _checkpoint("cb-pre-message-query")
            # Buscar execução pausada do contato via mensagens inbound
            # Filtra apenas 'inbound' para garantir que são mensagens do usuário (com user_id no extra_data)
            user_id_patterns = [
                f'%"user_id": {cq_user_id}%',
                f'%"user_id":{cq_user_id}%'
            ]
            recent_contact_ids = [
                cid for (cid,) in db.query(Message.contact_id).filter(
                    Message.tenant_id == channel.tenant_id,
                    Message.direction == 'inbound',
                    or_(*[Message.extra_data.like(p) for p in user_id_patterns])
                ).order_by(Message.created_at.desc()).limit(25).all()
                if cid
            ]
            _checkpoint("cb-post-message-query")
            logger.info(f"   callback_query: cq_user_id={cq_user_id} recent_contact_ids={recent_contact_ids}")

            paused_exec = None
            if recent_contact_ids:
                paused_exec = db.query(FlowExecution).filter(
                    FlowExecution.contact_id.in_(recent_contact_ids),
                    FlowExecution.status == 'waiting_response'
                ).order_by(FlowExecution.updated_at.desc()).first()

            # Fallback: buscar por contact_id associado a execuções de qualquer canal do mesmo tenant
            if not paused_exec:
                logger.warning(f"   callback_query: paused_exec não encontrado via mensagens. Tentando fallback por chat_id...")
                # Tenta pelo chat_id no contexto da execução
                try:
                    all_waiting = db.query(FlowExecution).filter(
                        FlowExecution.status == 'waiting_response'
                    ).order_by(FlowExecution.updated_at.desc()).limit(50).all()
                    for ex in all_waiting:
                        ctx = json.loads(ex.context) if ex.context else {}
                        if ctx.get("bot_token") == bot_token and str(ctx.get("chat_id", "")) == str(cq_chat_id):
                            paused_exec = ex
                            logger.info(f"   callback_query: paused_exec encontrado via chat_id fallback: exec {ex.id}")
                            break
                except Exception as fe:
                    logger.warning(f"   callback_query fallback error: {fe}")

            _checkpoint("cb-post-paused-exec-search")
            if paused_exec:
                paused_exec.status = 'running'
                paused_exec.context = None
                db.commit()
                _checkpoint("cb-post-commit")
                logger.info(f"   ▶ Continuando execução {paused_exec.id} a partir do step {target_step_id} (botão: {btn_label!r})")
                threading.Thread(
                    target=run_flow_background,
                    kwargs=dict(
                        channel_id=channel.id,
                        contact_id=paused_exec.contact_id,
                        flow_id=paused_exec.flow_id,
                        chat_id=cq_chat_id,
                        bot_token=bot_token,
                        execution_id=paused_exec.id,
                        start_from_step_id=target_step_id,
                    ),
                    daemon=True,
                ).start()
            else:
                logger.warning(f"Nenhuma execução pausada encontrada para callback goto_step:{target_step_id} (botão: {btn_label!r})")

        return {"status": "ok"}
    # ============= FIM CALLBACK QUERY =============

    print(f"📩 Message encontrada: {message is not None}")
    if not message:
        logger.info("Update sem mensagem, ignorando")
        return {"status": "ok", "message": "No message in update"}
    
    chat_id = message.get("chat", {}).get("id")
    user_data = message.get("from", {})
    user_id = user_data.get("id")
    username = user_data.get("username")
    first_name = user_data.get("first_name", "")
    last_name = user_data.get("last_name", "")
    is_bot = user_data.get("is_bot", False)
    text = message.get("text", "")
    caption = message.get("caption", "")

    # Detectar tipo de mensagem (além de texto) para salvar no histórico corretamente
    inbound_type = "text"
    inbound_content = text
    inbound_extra = {
        "chat_id": chat_id,
        "user_id": user_id,
        "message_id": message.get("message_id"),
    }

    # Forward/encaminhada (melhor esforço; Telegram varia campos dependendo do tipo de forward)
    forwarded_from = None
    if message.get("forward_sender_name"):
        forwarded_from = message.get("forward_sender_name")
    elif isinstance(message.get("forward_from"), dict):
        f = message.get("forward_from") or {}
        forwarded_from = (f.get("first_name") or "").strip()
        if f.get("last_name"):
            forwarded_from = f"{forwarded_from} {f.get('last_name')}".strip()
        if not forwarded_from and f.get("username"):
            forwarded_from = f"@{f.get('username')}"
    elif isinstance(message.get("forward_from_chat"), dict):
        forwarded_from = (message.get("forward_from_chat") or {}).get("title")
    if forwarded_from:
        inbound_extra["forwarded_from"] = forwarded_from

    # Documentos/arquivos
    if isinstance(message.get("document"), dict):
        doc = message.get("document") or {}
        inbound_type = "file"
        inbound_content = caption or doc.get("file_name") or "[Arquivo]"
        inbound_extra.update(
            {
                "file_id": doc.get("file_id"),
                "file_unique_id": doc.get("file_unique_id"),
                "file_name": doc.get("file_name"),
                "mime_type": doc.get("mime_type"),
                "file_size": doc.get("file_size"),
                "caption": caption or None,
            }
        )

    # Voz (voice message)
    elif isinstance(message.get("voice"), dict):
        voice = message.get("voice") or {}
        inbound_type = "voice"
        inbound_content = caption or ""
        inbound_extra.update(
            {
                "file_id": voice.get("file_id"),
                "file_unique_id": voice.get("file_unique_id"),
                "duration": voice.get("duration"),
                "mime_type": voice.get("mime_type"),
                "file_size": voice.get("file_size"),
                "caption": caption or None,
            }
        )

    # Áudio (arquivo de áudio)
    elif isinstance(message.get("audio"), dict):
        audio = message.get("audio") or {}
        inbound_type = "audio"
        inbound_content = caption or audio.get("file_name") or ""
        inbound_extra.update(
            {
                "file_id": audio.get("file_id"),
                "file_unique_id": audio.get("file_unique_id"),
                "duration": audio.get("duration"),
                "performer": audio.get("performer"),
                "title": audio.get("title"),
                "file_name": audio.get("file_name"),
                "mime_type": audio.get("mime_type"),
                "file_size": audio.get("file_size"),
                "caption": caption or None,
            }
        )

    # Foto
    elif isinstance(message.get("photo"), list) and message.get("photo"):
        photos = message.get("photo")
        best = photos[-1] if photos else {}
        inbound_type = "image"
        inbound_content = caption or ""
        inbound_extra.update(
            {
                "file_id": best.get("file_id"),
                "file_unique_id": best.get("file_unique_id"),
                "width": best.get("width"),
                "height": best.get("height"),
                "file_size": best.get("file_size"),
                "caption": caption or None,
            }
        )

    # Vídeo
    elif isinstance(message.get("video"), dict):
        video = message.get("video") or {}
        inbound_type = "video"
        inbound_content = caption or ""
        inbound_extra.update(
            {
                "file_id": video.get("file_id"),
                "file_unique_id": video.get("file_unique_id"),
                "width": video.get("width"),
                "height": video.get("height"),
                "duration": video.get("duration"),
                "mime_type": video.get("mime_type"),
                "file_size": video.get("file_size"),
                "caption": caption or None,
            }
        )

    # Video note
    elif isinstance(message.get("video_note"), dict):
        vn = message.get("video_note") or {}
        inbound_type = "video_note"
        inbound_content = caption or ""
        inbound_extra.update(
            {
                "file_id": vn.get("file_id"),
                "file_unique_id": vn.get("file_unique_id"),
                "length": vn.get("length"),
                "duration": vn.get("duration"),
                "file_size": vn.get("file_size"),
                "caption": caption or None,
            }
        )
    
    # IMPORTANTE: Ignorar mensagens do próprio bot para evitar loop infinito
    if is_bot:
        print(f"🤖 Mensagem enviada pelo bot, ignorando para evitar loop")
        logger.info("Mensagem do bot ignorada")
        return {"status": "ok", "message": "Bot message ignored"}
    
    preview = inbound_content
    if not preview and inbound_type != "text":
        preview = f"[{inbound_type}]"
    print(f"💬 Mensagem recebida ({inbound_type}) de {first_name} (@{username}): '{preview}'")
    print(f"   user_id={user_id}, chat_id={chat_id}")
    
    # Detectar parâmetro de referência no /start (robusto)
    # Telegram pode enviar:
    # - "/start payload"
    # - "/start@seu_bot payload" (principalmente em grupos)
    # - "/start\npayload" (alguns clientes)
    ref_param = None
    normalized_text = (text or "").strip()
    text_lower = normalized_text.lower()
    is_start_command = normalized_text.startswith("/start")
    if is_start_command:
        # Quebra em comando + resto
        parts = normalized_text.split(maxsplit=1)
        command = parts[0]
        remainder = parts[1].strip() if len(parts) > 1 else ""

        # Suportar /start@botname
        if command.startswith("/start@"):  # ex: /start@blackchatpro_bot
            command = "/start"

        if command == "/start" and remainder:
            ref_param = remainder
        elif command == "/start" and "\n" in normalized_text:
            after = normalized_text.split("\n", 1)[1].strip()
            if after:
                ref_param = after

        print(f"🔗 /start detectado: text='{normalized_text}' | ref_param='{ref_param}'")
        logger.info(f"/start detectado | ref_param={ref_param}")
    
    if not chat_id or not user_id:
        logger.warning("Update sem chat_id ou user_id")
        return {"status": "ok", "message": "Missing required fields"}
    
    logger.info(f"Mensagem de user_id={user_id}, chat_id={chat_id}, type={inbound_type}")
    
    # 3. Criar/Atualizar Contact — busca por coluna indexada telegram_user_id (1 query)
    contact = None

    _checkpoint("2-pre-contact-query")
    # Busca principal: coluna dedicada telegram_user_id (indexada, O(1))
    if user_id:
        contact = db.query(Contact).filter(
            Contact.tenant_id == channel.tenant_id,
            Contact.telegram_user_id == str(user_id)
        ).first()

    # Fallback para contatos legados sem telegram_user_id preenchido
    if not contact and user_id:
        try:
            user_id_patterns = [
                f'%"user_id": {user_id}%',
                f'%"user_id":{user_id}%'
            ]
            recent_contact_ids = [
                cid for (cid,) in db.query(Message.contact_id).filter(
                    Message.tenant_id == channel.tenant_id,
                    Message.direction == 'inbound',
                    or_(*[Message.extra_data.like(p) for p in user_id_patterns])
                ).order_by(Message.created_at.desc()).limit(5).all()
                if cid
            ]
            if recent_contact_ids:
                contact = db.query(Contact).filter(Contact.id == recent_contact_ids[0]).first()
                # Preencher coluna dedicada para próximas buscas
                if contact and not contact.telegram_user_id:
                    contact.telegram_user_id = str(user_id)
        except Exception as e:
            logger.warning(f"Falha no fallback de busca por user_id: {e}")

    if not contact and username:
        contact = db.query(Contact).filter(
            Contact.tenant_id == channel.tenant_id,
            Contact.username == username
        ).first()
        if contact and user_id and not contact.telegram_user_id:
            contact.telegram_user_id = str(user_id)
    
    if not contact:
        # Verificar limite de contatos ativos do plano antes de criar
        try:
            plan = get_plan_for_tenant(db, channel.tenant_id)
            if plan:
                check_contact_limit(db, channel.tenant_id, plan)
        except LimitExceededError as exc:
            logger.warning(
                f"Limite de contatos atingido para tenant {channel.tenant_id}: "
                f"{exc.current}/{exc.limit} contatos ativos. Contato não criado."
            )
            return {"status": "ok", "message": "contact_limit_reached"}

        contact = Contact(
            tenant_id=channel.tenant_id,
            first_name=first_name,
            last_name=last_name,
            username=username,
            default_channel_id=channel.id,
            telegram_user_id=str(user_id) if user_id else None,
        )
        db.add(contact)
        db.commit()
        db.refresh(contact)
        logger.info(f"Contato criado: {contact.id} ({contact_full_name(contact)})")
    else:
        # Atualizar dados se necessário (tudo num commit só)
        contact.first_name = first_name or contact.first_name
        contact.last_name = last_name or contact.last_name
        contact.username = username or contact.username
        if user_id:
            contact.telegram_user_id = str(user_id)
        if contact.default_channel_id != channel.id:
            contact.default_channel_id = channel.id

        # IDs Telegram no custom_fields (debug)
        try:
            custom_fields = json.loads(contact.custom_fields) if isinstance(contact.custom_fields, str) else (contact.custom_fields or {})
            if custom_fields.get("telegram_user_id") != user_id or custom_fields.get("telegram_chat_id") != chat_id:
                custom_fields["telegram_user_id"] = user_id
                custom_fields["telegram_chat_id"] = chat_id
                contact.custom_fields = json.dumps(custom_fields, ensure_ascii=False)
        except Exception as e:
            logger.warning(f"Falha ao atualizar custom_fields: {e}")

        db.commit()
        logger.info(f"Contato atualizado: {contact.id} ({contact_full_name(contact)})")
    
    # 3.1. Salvar mensagem recebida (inbound)
    extra_data = json.dumps(inbound_extra, ensure_ascii=False)
    
    inbound_message = Message(
        tenant_id=channel.tenant_id,
        contact_id=contact.id,
        channel_id=channel.id,
        direction='inbound',
        content=inbound_content,
        message_type=inbound_type,
        external_id=str(message.get("message_id")),
        extra_data=extra_data,
        status='received'
    )
    db.add(inbound_message)
    db.commit()
    print(f"💾 Mensagem recebida salva (ID: {inbound_message.id})")

    # Qualquer /start (com ou sem parâmetro) deve SEMPRE iniciar do zero.
    # Nunca deve ser interpretado como "resposta" para um fluxo pausado.
    is_start_with_ref = is_start_command and bool(ref_param)

    if is_start_command:
        # Cancelar apenas execuções pertencentes a ESTE bot/canal.
        # (Contato pode conversar com vários bots; não queremos cancelar fluxos de outro bot.)
        cancelled = 0
        candidates = db.query(FlowExecution).filter(
            FlowExecution.contact_id == contact.id,
            FlowExecution.status.in_(['started', 'active', 'waiting_response', 'waiting_input'])
        ).order_by(FlowExecution.updated_at.desc()).all()

        for ex in candidates:
            ctx = {}
            try:
                ctx = json.loads(ex.context) if ex.context else {}
            except Exception:
                ctx = {}

            ctx_bot_token = ctx.get('bot_token')
            ctx_channel_id = ctx.get('channel_id')

            # Execuções legadas podem não ter context. Nesse caso, tente inferir o bot
            # pelo flow.channel_id para não cancelar execuções de outro bot por engano.
            if not ctx_bot_token and not ctx_channel_id:
                try:
                    ex_flow_channel_id = db.query(Flow.channel_id).filter(Flow.id == ex.flow_id).scalar()
                    if ex_flow_channel_id and int(ex_flow_channel_id) != int(channel.id):
                        continue
                except Exception:
                    pass

            # Se o contexto identifica outro bot, não cancele.
            if ctx_bot_token and ctx_bot_token != bot_token:
                continue
            if ctx_channel_id and int(ctx_channel_id) != int(channel.id):
                continue

            ex.status = 'cancelled'
            ex.completed_at = datetime.now()
            ex.current_step_id = None
            ex.context = None
            cancelled += 1

        if cancelled:
            db.commit()
            print(f"🧹 /start canceladas {cancelled} execucao(oes) deste bot → reinicio limpo (contact_id={contact.id}, channel_id={channel.id})")
            logger.info(f"/start: canceladas {cancelled} execucoes deste bot (contact_id={contact.id}, channel_id={channel.id})")
    
    # 3.2. VERIFICAR SE EXISTE FLUXO ATIVO AGUARDANDO RESPOSTA
    # IMPORTANTE: qualquer /start deve iniciar fluxo novo, nunca continuar execução pausada.
    active_execution = None
    if not is_start_command:
        # Somente continuar execuções que pertençam ao mesmo bot.
        # Caso contrário, um texto no bot B poderia continuar um "waiting_response" do bot A.
        candidates = db.query(FlowExecution).filter(
            FlowExecution.contact_id == contact.id,
            FlowExecution.status.in_(['waiting_response', 'waiting_input'])
        ).order_by(FlowExecution.updated_at.desc()).all()

        for ex in candidates:
            ctx = {}
            try:
                ctx = json.loads(ex.context) if ex.context else {}
            except Exception:
                ctx = {}

            ctx_bot_token = ctx.get('bot_token')
            ctx_channel_id = ctx.get('channel_id')

            # Execução legada sem context: inferir canal pelo flow.channel_id para
            # evitar continuar waiting de outro bot.
            if not ctx_bot_token and not ctx_channel_id:
                try:
                    ex_flow_channel_id = db.query(Flow.channel_id).filter(Flow.id == ex.flow_id).scalar()
                    if ex_flow_channel_id and int(ex_flow_channel_id) != int(channel.id):
                        continue
                except Exception:
                    pass

            if ctx_bot_token and ctx_bot_token != bot_token:
                continue
            if ctx_channel_id and int(ctx_channel_id) != int(channel.id):
                continue

            active_execution = ex
            break
    
    _checkpoint("3-pre-trigger-map")
    # Pré-carregar trigger_map UMA VEZ (2 queries) — usado em todo o matching abaixo
    trigger_map = _load_trigger_map(db, channel.tenant_id, channel.id)
    _checkpoint("4-post-trigger-map")

    if active_execution:
        # Se a mensagem é um gatilho explícito (keyword) de algum fluxo,
        # priorize iniciar o novo fluxo ao invés de tratar como "resposta".
        # (Usuário pode clicar/iniciar outro gatilho a qualquer momento.)
        try:
            keyword_match_flow = trigger_map["keyword_to_flow"].get(text_lower)

            if keyword_match_flow:
                # Se a execução ativa está aguardando clique de botão (não texto),
                # NÃO reiniciar o fluxo — o usuário ainda precisa clicar num botão.
                if active_execution:
                    try:
                        active_ctx = json.loads(active_execution.context) if active_execution.context else {}
                        if active_ctx.get("waiting_for") == "button_click":
                            logger.info(
                                f"Keyword '{text_lower}' ignorada: execução {active_execution.id} aguarda clique de botão. "
                                f"Mantendo execução pausada."
                            )
                            keyword_match_flow = None  # cancela a decisão de reiniciar
                    except Exception:
                        pass

            if keyword_match_flow:
                logger.info(
                    f"Keyword '{text_lower}' detectada durante waiting_response; "
                    f"cancelando execuções pausadas deste bot e iniciando flow_id={keyword_match_flow.id}"
                )

                # Cancelar execuções pausadas DESTE bot
                candidates = db.query(FlowExecution).filter(
                    FlowExecution.contact_id == contact.id,
                    FlowExecution.status.in_(['waiting_response', 'waiting_input'])
                ).order_by(FlowExecution.updated_at.desc()).all()

                cancelled = 0
                for ex in candidates:
                    ctx = {}
                    try:
                        ctx = json.loads(ex.context) if ex.context else {}
                    except Exception:
                        ctx = {}

                    ctx_bot_token = ctx.get('bot_token')
                    ctx_channel_id = ctx.get('channel_id')

                    # Execução legada sem context: inferir canal pelo flow.channel_id para
                    # evitar cancelar waiting de outro bot.
                    if not ctx_bot_token and not ctx_channel_id:
                        try:
                            ex_flow_channel_id = db.query(Flow.channel_id).filter(Flow.id == ex.flow_id).scalar()
                            if ex_flow_channel_id and int(ex_flow_channel_id) != int(channel.id):
                                continue
                        except Exception:
                            pass
                    if ctx_bot_token and ctx_bot_token != bot_token:
                        continue
                    if ctx_channel_id and int(ctx_channel_id) != int(channel.id):
                        continue

                    ex.status = 'cancelled'
                    ex.completed_at = datetime.now()
                    ex.current_step_id = None
                    ex.context = None
                    cancelled += 1

                if cancelled:
                    db.commit()
                    logger.info(f"Canceladas {cancelled} execuções pausadas deste bot para priorizar keyword")

                # Não continue execução antiga; siga para seleção/início do novo fluxo
                active_execution = None
        except Exception as e:
            logger.warning(f"Falha ao checar keyword durante waiting_response: {e}")

    if active_execution:
        print(f"\n🔄 CONTINUANDO FLUXO ATIVO (Execução ID: {active_execution.id})")
        logger.info(f"Contato tem fluxo ativo aguardando resposta - Execução {active_execution.id}")

        # Carregar contexto
        try:
            context = json.loads(active_execution.context) if active_execution.context else {}
            waiting_for_field = context.get("waiting_for_field")
            next_step_index = context.get("next_step_index", 0)
            saved_chat_id = context.get("chat_id")
            saved_bot_token = context.get("bot_token")

            # Se a execução está aguardando clique de botão, texto não deve continuar o fluxo.
            # Mantém pausado e avisa o usuário.
            if context.get("waiting_for") == "button_click":
                logger.info(f"   Execução {active_execution.id} aguarda botão, ignorando texto '{text[:30]}'")
                # Envia feedback ao usuário pedindo que clique em um botão
                _bt = saved_bot_token or bot_token
                _cid = saved_chat_id or chat_id
                if _bt and _cid:
                    try:
                        send_telegram_message(
                            bot_token=_bt,
                            chat_id=_cid,
                            text="👆 Por favor, clique em um dos botões acima para continuar."
                        )
                    except Exception:
                        pass
                return {"status": "ok", "message": "waiting_for_button"}

            print(f"   Campo esperado: {waiting_for_field}")
            print(f"   Próximo step index: {next_step_index}")

            # Salvar resposta no campo personalizado
            if waiting_for_field:
                custom_fields = json.loads(contact.custom_fields) if isinstance(contact.custom_fields, str) else (contact.custom_fields or {})
                custom_fields[waiting_for_field] = text
                contact.custom_fields = json.dumps(custom_fields, ensure_ascii=False)
                db.commit()
                print(f"   ✓ Resposta salva em campo: {waiting_for_field} = {text}")
                logger.info(f"Resposta salva: {waiting_for_field} = {text}")
            
            # Atualizar status para active e continuar execução
            active_execution.status = 'active'
            db.commit()
            
            # Buscar todos os steps do fluxo
            flow = db.query(Flow).filter(Flow.id == active_execution.flow_id).first()
            if not flow:
                logger.warning(f"Flow {active_execution.flow_id} não encontrado")
                active_execution.status = 'failed'
                db.commit()
                return {"status": "ok", "message": "Flow not found"}
            
            steps = db.query(FlowStep).filter(FlowStep.flow_id == flow.id).order_by(FlowStep.order_index).all()
            
            # Encontrar índice do step atual e avançar para o próximo
            current_step_index = next((i for i, s in enumerate(steps) if s.id == active_execution.current_step_id), -1)
            
            if current_step_index >= 0:
                current_step = steps[current_step_index]

                flow_config = json.loads(flow.config) if flow.config else {}
                has_connections = bool(flow_config.get("connections"))

                if has_connections:
                    next_step = find_next_step_by_output(flow_config, current_step.id, "default", steps)
                else:
                    next_step = steps[current_step_index + 1] if (current_step_index + 1 < len(steps)) else None

                if not next_step:
                    active_execution.status = 'completed'
                    active_execution.completed_at = datetime.now()
                    db.commit()
                    print(f"   ✓ Fluxo concluído (sem próximo step)")
                    return {"status": "ok", "message": "Flow completed"}
                
                # Se o step atual for de ação, executar ações que não dependem da resposta
                if current_step.type == "action":
                    try:
                        current_config = json.loads(current_step.config) if current_step.config else {}
                        current_actions = current_config.get("actions", [])
                        
                        redirect_result = None
                        for action in current_actions:
                            action_type = action.get("type")
                            if action_type == "set_field":
                                field_value = action.get("field_value") or action.get("value") or action.get("fieldValue") or ""
                                # Pular set_field com placeholder (já salvamos a resposta)
                                if field_value and ("ultima_mensagem" in str(field_value) or "last_message" in str(field_value)):
                                    continue
                            # Executar demais ações
                            result = execute_action(db, action, contact, channel, flow)
                            if result and isinstance(result, dict) and result.get("action") in ("redirect_flow", "redirect_step"):
                                redirect_result = result
                                break

                        if redirect_result:
                            if redirect_result.get("action") == "redirect_flow":
                                target_flow_id = redirect_result.get("flow_id")
                                logger.info(f"Pós-resposta: redirecionando para flow {target_flow_id}")
                                target_flow = db.query(Flow).filter(Flow.id == target_flow_id).first()
                                if target_flow:
                                    threading.Thread(
                                        target=run_flow_background,
                                        args=(channel.id, contact.id, target_flow_id, saved_chat_id or chat_id, saved_bot_token or bot_token),
                                        daemon=True,
                                    ).start()
                                return {"status": "ok", "message": "Flow redirected"}
                            elif redirect_result.get("action") == "redirect_step":
                                target_step_id = redirect_result.get("step_id")
                                logger.info(f"Pós-resposta: pulando para step {target_step_id}")
                                threading.Thread(
                                    target=run_flow_background,
                                    args=(channel.id, contact.id, active_execution.flow_id, saved_chat_id or chat_id, saved_bot_token or bot_token, active_execution.id, target_step_id),
                                    daemon=True,
                                ).start()
                                return {"status": "ok", "message": "Flow step redirected"}
                    except Exception as e:
                        logger.error(f"Erro ao executar ações pós-resposta: {e}")
                
                # Continuar fluxo a partir do próximo step
                threading.Thread(
                    target=run_flow_background,
                    args=(channel.id, contact.id, active_execution.flow_id, saved_chat_id or chat_id, saved_bot_token or bot_token, active_execution.id, next_step.id),
                    daemon=True,
                ).start()
                
                print(f"   ✓ Fluxo continuando a partir do step {next_step.id}")
                return {"status": "ok", "message": "Flow continued"}
            else:
                # Step atual não encontrado na lista - falhar para não corromper estado
                active_execution.status = 'failed'
                db.commit()
                logger.warning(f"Step atual {active_execution.current_step_id} não encontrado para continuar")
                return {"status": "ok", "message": "Flow step not found"}
        
        except Exception as e:
            logger.error(f"Erro ao continuar fluxo: {e}")
            active_execution.status = 'failed'
            db.commit()
    elif not is_start_command:
        # Fallback: se não encontrou waiting_response, verificar execução ativa recente
        active_exec = db.query(FlowExecution).filter(
            FlowExecution.contact_id == contact.id,
            FlowExecution.status == 'active'
        ).order_by(FlowExecution.started_at.desc()).first()
        if active_exec and active_exec.current_step_id:
            # Evitar continuar execução de outro bot
            try:
                ctx = json.loads(active_exec.context) if active_exec.context else {}
            except Exception:
                ctx = {}
            ctx_bot_token = ctx.get('bot_token')
            ctx_channel_id = ctx.get('channel_id')
            if ctx_bot_token and ctx_bot_token != bot_token:
                active_exec = None
            if active_exec and ctx_channel_id and int(ctx_channel_id) != int(channel.id):
                active_exec = None

        if active_exec and active_exec.current_step_id:
            current_step = db.query(FlowStep).filter(FlowStep.id == active_exec.current_step_id).first()
            if current_step and current_step.type == "action":
                try:
                    current_config = json.loads(current_step.config) if current_step.config else {}
                    current_actions = current_config.get("actions", [])
                    waiting_field = None
                    for action in current_actions:
                        if action.get("type") == "set_field":
                            field_value = action.get("field_value") or action.get("value") or action.get("fieldValue") or ""
                            if field_value and ("ultima_mensagem" in str(field_value) or "last_message" in str(field_value)):
                                waiting_field = action.get("field_name")
                                break
                    if waiting_field:
                        custom_fields = json.loads(contact.custom_fields) if isinstance(contact.custom_fields, str) else (contact.custom_fields or {})
                        custom_fields[waiting_field] = text
                        contact.custom_fields = json.dumps(custom_fields, ensure_ascii=False)
                        db.commit()
                        
                        active_exec.status = 'active'
                        db.commit()
                        
                        # Continuar fluxo a partir do próximo step (respeitando conexões se existirem)
                        flow = db.query(Flow).filter(Flow.id == active_exec.flow_id).first()
                        steps = db.query(FlowStep).filter(FlowStep.flow_id == flow.id).order_by(FlowStep.order_index).all()
                        flow_config = json.loads(flow.config) if flow and flow.config else {}
                        has_connections = bool(flow_config.get("connections"))
                        if has_connections:
                            next_step = find_next_step_by_output(flow_config, current_step.id, "default", steps)
                        else:
                            current_index = next((i for i, s in enumerate(steps) if s.id == current_step.id), -1)
                            next_step = steps[current_index + 1] if (current_index >= 0 and current_index + 1 < len(steps)) else None

                        if next_step:
                            threading.Thread(
                                target=run_flow_background,
                                args=(channel.id, contact.id, active_exec.flow_id, chat_id, bot_token, active_exec.id, next_step.id),
                                daemon=True,
                            ).start()
                            return {"status": "ok", "message": "Flow continued (fallback)"}
                except Exception as e:
                    logger.error(f"Erro no fallback de execucao ativa: {e}")
    
    # 4. Usar trigger_map já carregado (sem queries adicionais)
    flows = trigger_map["flows"]

    print(f"\n[VERIFICACAO] Verificando {len(flows)} fluxo(s) ativo(s)")
    logger.info(f"Verificando {len(flows)} fluxo(s) ativo(s)")

    selected_flow = None
    ref_flow_matched = None
    # `text_lower` já foi calculado acima a partir de `normalized_text`
    
    # Primeiro: verificar se há match de link de referência
    if ref_param and len(flows) > 0:
        print(f"\n[REF URL CHECK] Verificando match para ref_param: {ref_param}")

        for flow, ref_key, save_ref_field in trigger_map["ref_flows"]:
            if ref_param == ref_key or ref_param.startswith(ref_key):
                print(f"  MATCH! Fluxo '{flow.name}' (ref_key: {ref_key})")

                if save_ref_field:
                    custom_fields = json.loads(contact.custom_fields) if isinstance(contact.custom_fields, str) else (contact.custom_fields or {})
                    custom_fields[save_ref_field] = ref_param
                    contact.custom_fields = json.dumps(custom_fields, ensure_ascii=False)
                    db.commit()

                ref_flow_matched = flow
                break

        if ref_flow_matched:
            selected_flow = ref_flow_matched
            print(f"\n[MATCH REF URL] Fluxo selecionado: {selected_flow.name}")

    # Se o usuário mandou apenas "/start" (sem parâmetro), não há ref_param para dar match.
    # Para evitar que o bot fique mudo, fazemos um fallback:
    # - Se existir exatamente 1 fluxo com triggerType=telegram_ref_url, iniciamos ele.
    # - Se existirem vários, orientamos a usar o link com parâmetro.
    if not selected_flow and is_start_command and not ref_param:
        ref_url_flows = [f for f, _, _ in trigger_map["ref_flows"]]

        if len(ref_url_flows) == 1:
            selected_flow = ref_url_flows[0]
            print(f"\n[FALLBACK /start] Iniciando fluxo ref_url único: {selected_flow.name}")
            logger.info(f"/start sem ref: iniciando fluxo ref_url único (flow_id={selected_flow.id})")
        elif len(ref_url_flows) > 1:
            bot_username = (channel_config.get("bot_username") or "").replace("@", "")
            example = f"https://t.me/{bot_username}?start=SUA_CHAVE" if bot_username else "https://t.me/<seu_bot>?start=SUA_CHAVE"
            try:
                send_telegram_message(
                    bot_token=bot_token,
                    chat_id=chat_id,
                    text=(
                        "Este bot usa links de referência para iniciar o fluxo.\n\n"
                        "Envie o link com parâmetro (ex.: \"/start SUA_CHAVE\") ou use um link assim:\n"
                        f"{example}"
                    )
                )
            except Exception as e:
                logger.warning(f"Falha ao responder /start sem ref: {e}")
            return {"status": "ok", "message": "Start without ref - guidance sent"}
    
    # Verificar keyword ou trigger "any"/"first_message" usando trigger_map (sem N+1)
    if not selected_flow:
        # Lookup O(1) por keyword
        kw_flow = trigger_map["keyword_to_flow"].get(text_lower)
        if kw_flow:
            selected_flow = kw_flow
            print(f"  [SELECIONADO] Fluxo: '{kw_flow.name}' (keyword match)")
            logger.info(f"Fluxo selecionado por keyword: {kw_flow.name}")

    # Fallback: trigger "any" ou "first_message"
    if not selected_flow:
        for flow in flows:
            trig = trigger_map["trigger_by_flow"].get(flow.id)
            if not trig:
                continue
            trigger_type = trig["config"].get("triggerType")
            if trigger_type in ("any", "first_message"):
                selected_flow = flow
                print(f"  [SELECIONADO] Fluxo: '{flow.name}' (trigger: {trigger_type})")
                logger.info(f"Fluxo selecionado (always/first): {flow.name}")
                break
    
    # Se nenhum fluxo deu match, NÃO FAZER NADA (sem fluxo padrão)
    if not selected_flow:
        print(f"\n[SEM MATCH] Nenhuma keyword corresponde a mensagem '{text}' - Ignorando")
        logger.info(f"Nenhum fluxo match para mensagem: {text}")
        # NÃO ENVIA NADA quando não há match 100% de keyword
        return {"status": "ok", "message": "No flow match - ignored"}
    
    # 5. Registrar execução do fluxo
    _trigger_type = 'telegram_ref_url' if (ref_param or (is_start_command and not ref_param)) else 'keyword'
    flow_execution = FlowExecution(
        tenant_id=channel.tenant_id,
        contact_id=contact.id,
        flow_id=selected_flow.id,
        trigger_type=_trigger_type,
        status='active',
        context=json.dumps({
            "channel_id": channel.id,
            "chat_id": chat_id,
            "bot_token": bot_token,
        })
    )
    db.add(flow_execution)
    db.commit()
    db.refresh(flow_execution)
    _checkpoint("5-flow-execution-created")

    print(f"\n[EXECUTANDO] Fluxo: {selected_flow.id} - {selected_flow.name}")
    logger.info(f"Executando fluxo: {selected_flow.id} - {selected_flow.name} (execution_id={flow_execution.id})")

    threading.Thread(
        target=run_flow_background,
        args=(channel.id, contact.id, selected_flow.id, chat_id, bot_token, flow_execution.id, None),
        daemon=True,
    ).start()
    _checkpoint("6-thread-started")
    return {"status": "ok", "message": "Flow queued"}


@router.post("/{webhook_secret}")
async def telegram_webhook(
    webhook_secret: str,
    update: dict = Body(...),
    db: Session = Depends(get_db),
):
    """
    Webhook para receber updates do Telegram.

    Fase 3: Enfileira o update no ARQ e retorna 200 imediatamente ao Telegram.
    Fallback: se ARQ offline, processa síncronamente (comportamento original).
    Idempotência: job_id = tg_{secret[:8]}_{update_id} evita reprocessamento de retries do Telegram.
    """
    from app.workers.arq_pool import enqueue

    update_id = update.get("update_id")
    job_id = f"tg_{webhook_secret[:8]}_{update_id}" if update_id else None

    enqueued = await enqueue(
        "process_webhook",
        payload=update,
        webhook_secret=webhook_secret,
        _job_id=job_id,
    )
    if enqueued is not None:
        # Job enfileirado — retorna 200 imediato, worker processa assincronamente
        return {"ok": True}

    # ARQ offline: fallback para processamento síncrono (comportamento original preservado)
    logger.warning("ARQ offline — processando webhook síncronamente (fallback)")
    return _handle_telegram_update(update, webhook_secret, db)

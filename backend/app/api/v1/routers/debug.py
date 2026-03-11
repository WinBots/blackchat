"""Router para debugging e rastreamento de leads"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from typing import List, Dict, Any
import json
from pydantic import BaseModel
from sqlalchemy import or_, func

from app.core.auth import require_super_admin
from app.db.models.user import User
from app.db.session import get_db
from app.db.models.contact import Contact
from app.db.models.flow_execution import FlowExecution
from app.db.models.flow_execution_log import FlowExecutionLog
from app.db.models.message import Message
from app.db.models.flow import Flow
from app.db.models.flow_step import FlowStep
from app.db.models.channel import Channel
from app.db.models.tag import ContactTag
from app.db.models.sequence import ContactSequence

router = APIRouter()


def _parse_jsonish(value: Any) -> Any:
    if value is None:
        return None
    if isinstance(value, (dict, list)):
        return value
    if isinstance(value, str):
        try:
            return json.loads(value)
        except Exception:
            return None
    return None


@router.get("/contacts/{contact_id}/history")
def get_contact_history(contact_id: int, db: Session = Depends(get_db), _: User = Depends(require_super_admin)):
    """
    Retorna TODO o histórico de um lead:
    - Todas as execuções de fluxos
    - Todos os logs detalhados de cada execução
    - Todas as mensagens enviadas e recebidas
    """
    contact = db.query(Contact).filter(Contact.id == contact_id).first()
    if not contact:
        raise HTTPException(status_code=404, detail="Contato não encontrado")
    
    # Buscar todas as execuções do contato
    executions = db.query(FlowExecution).filter(
        FlowExecution.contact_id == contact_id
    ).order_by(FlowExecution.started_at.desc()).all()
    
    history = {
        "contact": {
            "id": contact.id,
            "username": contact.username,
            "first_name": contact.first_name,
            "last_name": contact.last_name,
            "custom_fields": _parse_jsonish(contact.custom_fields) or (contact.custom_fields if isinstance(contact.custom_fields, dict) else {})
        },
        "executions": []
    }
    
    for execution in executions:
        # Buscar logs da execução
        logs = db.query(FlowExecutionLog).filter(
            FlowExecutionLog.flow_execution_id == execution.id
        ).order_by(FlowExecutionLog.created_at).all()
        
        # Buscar mensagens da execução
        messages = db.query(Message).filter(
            Message.flow_execution_id == execution.id
        ).order_by(Message.created_at).all()
        
        # Buscar informações do fluxo
        flow = db.query(Flow).filter(Flow.id == execution.flow_id).first()
        
        execution_data = {
            "id": execution.id,
            "flow": {
                "id": flow.id if flow else None,
                "name": flow.name if flow else "Fluxo desconhecido"
            },
            "status": execution.status,
            "trigger_type": execution.trigger_type,
            "started_at": execution.started_at.isoformat() if execution.started_at else None,
            "completed_at": execution.completed_at.isoformat() if execution.completed_at else None,
            "updated_at": execution.updated_at.isoformat() if execution.updated_at else None,
            "current_step_id": execution.current_step_id,
            "context": json.loads(execution.context) if execution.context else None,
            "logs": [
                {
                    "id": log.id,
                    "step_id": log.step_id,
                    "log_type": log.log_type,
                    "description": log.description,
                    "data": json.loads(log.data) if log.data else None,
                    "error_message": log.error_message,
                    "created_at": log.created_at.isoformat() if log.created_at else None
                }
                for log in logs
            ],
            "messages": [
                {
                    "id": msg.id,
                    "step_id": msg.step_id,
                    "direction": msg.direction,
                    "content": msg.content,
                    "message_type": msg.message_type,
                    "status": msg.status,
                    "created_at": msg.created_at.isoformat() if msg.created_at else None
                }
                for msg in messages
            ]
        }
        
        history["executions"].append(execution_data)
    
    # Buscar todas as mensagens do contato (incluindo as sem execução)
    all_messages = db.query(Message).filter(
        Message.contact_id == contact_id
    ).order_by(Message.created_at.desc()).all()
    
    history["total_messages"] = len(all_messages)
    history["total_executions"] = len(executions)
    
    return history


@router.get("/contacts/{contact_id}/current-position", dependencies=[Depends(require_super_admin)])
def get_contact_current_position(contact_id: int, db: Session = Depends(get_db)):
    """
    Retorna a posição atual do lead nos fluxos ativos
    """
    contact = db.query(Contact).filter(Contact.id == contact_id).first()
    if not contact:
        raise HTTPException(status_code=404, detail="Contato não encontrado")
    
    # Buscar execuções ativas ou aguardando resposta
    active_executions = db.query(FlowExecution).filter(
        FlowExecution.contact_id == contact_id,
        FlowExecution.status.in_(['active', 'waiting_response'])
    ).all()
    
    positions = []
    
    for execution in active_executions:
        flow = db.query(Flow).filter(Flow.id == execution.flow_id).first()
        current_step = None
        
        if execution.current_step_id:
            current_step = db.query(FlowStep).filter(
                FlowStep.id == execution.current_step_id
            ).first()
        
        # Contar total de steps do fluxo
        total_steps = db.query(FlowStep).filter(
            FlowStep.flow_id == execution.flow_id
        ).count()
        
        # Buscar último log
        last_log = db.query(FlowExecutionLog).filter(
            FlowExecutionLog.flow_execution_id == execution.id
        ).order_by(FlowExecutionLog.created_at.desc()).first()
        
        positions.append({
            "execution_id": execution.id,
            "flow_name": flow.name if flow else "Desconhecido",
            "flow_id": execution.flow_id,
            "status": execution.status,
            "current_step": {
                "id": current_step.id if current_step else None,
                "type": current_step.type if current_step else None,
                "order_index": current_step.order_index if current_step else None
            } if current_step else None,
            "total_steps": total_steps,
            "context": json.loads(execution.context) if execution.context else None,
            "last_activity": last_log.created_at.isoformat() if last_log else execution.updated_at.isoformat(),
            "updated_at": execution.updated_at.isoformat() if execution.updated_at else None
        })
    
    return {
        "contact_id": contact_id,
        "username": contact.username,
        "active_flows": len(positions),
        "positions": positions
    }


@router.delete("/contacts/{contact_id}/clear-test-data", dependencies=[Depends(require_super_admin)])
def clear_contact_test_data(contact_id: int, db: Session = Depends(get_db)):
    """
    Limpa TODOS os dados de teste de um lead (para desenvolvimento):
    - Todas as execuções de fluxos
    - Todos os logs
    - Todas as mensagens
    
    ⚠️ ATENÇÃO: Esta ação é IRREVERSÍVEL!
    """
    contact = db.query(Contact).filter(Contact.id == contact_id).first()
    if not contact:
        raise HTTPException(status_code=404, detail="Contato não encontrado")
    
    # Buscar todas as execuções
    executions = db.query(FlowExecution).filter(
        FlowExecution.contact_id == contact_id
    ).all()
    
    execution_ids = [e.id for e in executions]
    
    # Deletar logs (cascade deve fazer isso automaticamente, mas garantindo)
    deleted_logs = 0
    if execution_ids:
        deleted_logs = db.query(FlowExecutionLog).filter(
            FlowExecutionLog.flow_execution_id.in_(execution_ids)
        ).delete(synchronize_session=False)
    
    # Deletar mensagens
    deleted_messages = db.query(Message).filter(
        Message.contact_id == contact_id
    ).delete(synchronize_session=False)
    
    # Deletar execuções
    deleted_executions = db.query(FlowExecution).filter(
        FlowExecution.contact_id == contact_id
    ).delete(synchronize_session=False)
    
    # Limpar custom_fields do contato
    contact.custom_fields = {}
    
    db.commit()
    
    return {
        "message": "Dados de teste limpos com sucesso",
        "contact_id": contact_id,
        "username": contact.username,
        "deleted": {
            "executions": deleted_executions,
            "logs": deleted_logs,
            "messages": deleted_messages
        }
    }


class TelegramMergeDuplicatesRequest(BaseModel):
    channel_id: int
    telegram_user_id: int
    keep_contact_id: int | None = None
    dry_run: bool = False


@router.post("/telegram/merge-duplicates", dependencies=[Depends(require_super_admin)])
def merge_telegram_contact_duplicates(payload: TelegramMergeDuplicatesRequest, db: Session = Depends(get_db)):
    """Mescla contatos duplicados do Telegram (principalmente quando username=None).

    Critério: mesmo telegram_user_id dentro do mesmo tenant/canal.
    Efeitos:
    - Reatribui messages.contact_id, flow_executions.contact_id, contact_tags.contact_id, contact_sequences.contact_id
    - Mescla custom_fields e remove contatos duplicados
    """
    channel = db.query(Channel).filter(Channel.id == payload.channel_id).first()
    if not channel:
        raise HTTPException(status_code=404, detail="Canal não encontrado")

    tenant_id = channel.tenant_id
    telegram_user_id = int(payload.telegram_user_id)

    user_id_patterns = [
        f'%"user_id": {telegram_user_id}%',
        f'%"user_id":{telegram_user_id}%'
    ]

    # 1) Coletar candidatos por messages.extra_data
    msg_contact_ids = [
        cid for (cid,) in db.query(Message.contact_id).filter(
            Message.tenant_id == tenant_id,
            Message.channel_id == payload.channel_id,
            Message.contact_id.isnot(None),
            or_(*[Message.extra_data.like(p) for p in user_id_patterns])
        ).distinct().all()
        if cid
    ]

    # 2) Coletar candidatos por contacts.custom_fields (varre tenant; ambiente dev costuma ser pequeno)
    contact_ids_from_custom_fields: list[int] = []
    contacts = db.query(Contact).filter(Contact.tenant_id == tenant_id).all()
    for c in contacts:
        fields = c.custom_fields
        if isinstance(fields, str):
            fields = _parse_jsonish(fields) or {}
        if isinstance(fields, dict) and fields.get("telegram_user_id") == telegram_user_id:
            contact_ids_from_custom_fields.append(c.id)

    candidate_ids = sorted(set(msg_contact_ids + contact_ids_from_custom_fields))
    if len(candidate_ids) <= 1:
        return {
            "message": "Nenhum duplicado encontrado",
            "channel_id": payload.channel_id,
            "telegram_user_id": telegram_user_id,
            "candidates": candidate_ids,
        }

    # Escolher contato principal
    keep_id = payload.keep_contact_id
    if keep_id is not None and keep_id not in candidate_ids:
        raise HTTPException(status_code=400, detail="keep_contact_id não pertence ao grupo de duplicados")

    if keep_id is None:
        waiting_exec = db.query(FlowExecution).filter(
            FlowExecution.contact_id.in_(candidate_ids),
            FlowExecution.status.in_(['waiting_response', 'waiting_input', 'active'])
        ).order_by(FlowExecution.updated_at.desc()).first()
        if waiting_exec:
            keep_id = waiting_exec.contact_id
        else:
            # Preferir quem tem mais mensagens
            counts = dict(
                db.query(Message.contact_id, func.count(Message.id)).filter(
                    Message.contact_id.in_(candidate_ids)
                ).group_by(Message.contact_id).all()
            )
            keep_id = max(candidate_ids, key=lambda cid: (counts.get(cid, 0), -cid))

    keep_contact = db.query(Contact).filter(Contact.id == keep_id).first()
    if not keep_contact:
        raise HTTPException(status_code=404, detail="Contato principal não encontrado")

    merge_ids = [cid for cid in candidate_ids if cid != keep_id]

    # Dry run: só reporta o que faria
    if payload.dry_run:
        return {
            "message": "Dry-run",
            "keep_contact_id": keep_id,
            "merge_contact_ids": merge_ids,
            "candidate_ids": candidate_ids,
        }

    # Mesclar custom_fields (mantém valores do principal, preenche lacunas dos duplicados)
    keep_fields = keep_contact.custom_fields
    if isinstance(keep_fields, str):
        keep_fields = _parse_jsonish(keep_fields) or {}
    if not isinstance(keep_fields, dict):
        keep_fields = {}

    keep_fields.setdefault("telegram_user_id", telegram_user_id)

    merged_contacts = db.query(Contact).filter(Contact.id.in_(merge_ids)).all() if merge_ids else []
    for dup in merged_contacts:
        dup_fields = dup.custom_fields
        if isinstance(dup_fields, str):
            dup_fields = _parse_jsonish(dup_fields) or {}
        if isinstance(dup_fields, dict):
            for k, v in dup_fields.items():
                if k not in keep_fields or keep_fields.get(k) in (None, "", [], {}):
                    keep_fields[k] = v

    keep_contact.custom_fields = keep_fields
    db.commit()

    # Reatribuir referências
    updated_messages = db.query(Message).filter(Message.contact_id.in_(merge_ids)).update(
        {"contact_id": keep_id},
        synchronize_session=False
    ) if merge_ids else 0

    updated_execs = db.query(FlowExecution).filter(FlowExecution.contact_id.in_(merge_ids)).update(
        {"contact_id": keep_id},
        synchronize_session=False
    ) if merge_ids else 0

    updated_tags = db.query(ContactTag).filter(ContactTag.contact_id.in_(merge_ids)).update(
        {"contact_id": keep_id},
        synchronize_session=False
    ) if merge_ids else 0

    updated_sequences = db.query(ContactSequence).filter(ContactSequence.contact_id.in_(merge_ids)).update(
        {"contact_id": keep_id},
        synchronize_session=False
    ) if merge_ids else 0

    # Remover duplicatas de tags (mesmo tag_name)
    tags = db.query(ContactTag).filter(ContactTag.contact_id == keep_id).all()
    seen = set()
    deleted_tag_dups = 0
    for t in tags:
        key = (t.tag_name or "").strip().lower()
        if key in seen:
            db.delete(t)
            deleted_tag_dups += 1
        else:
            seen.add(key)

    # Remover duplicatas de sequences (mesmo sequence_id)
    seqs = db.query(ContactSequence).filter(ContactSequence.contact_id == keep_id).all()
    seen_seq = set()
    deleted_seq_dups = 0
    for s in seqs:
        key = s.sequence_id
        if key in seen_seq:
            db.delete(s)
            deleted_seq_dups += 1
        else:
            seen_seq.add(key)

    # Deletar contatos duplicados
    deleted_contacts = db.query(Contact).filter(Contact.id.in_(merge_ids)).delete(synchronize_session=False) if merge_ids else 0
    db.commit()

    return {
        "message": "Contatos mesclados",
        "keep_contact_id": keep_id,
        "merged_contact_ids": merge_ids,
        "updated": {
            "messages": updated_messages,
            "flow_executions": updated_execs,
            "contact_tags": updated_tags,
            "contact_sequences": updated_sequences,
            "deleted_contacts": deleted_contacts,
            "deleted_tag_duplicates": deleted_tag_dups,
            "deleted_sequence_duplicates": deleted_seq_dups,
        }
    }


@router.get("/flows/{flow_id}/execution-summary", dependencies=[Depends(require_super_admin)])
def get_flow_execution_summary(flow_id: int, db: Session = Depends(get_db)):
    """
    Retorna um resumo de todas as execuções de um fluxo específico
    """
    flow = db.query(Flow).filter(Flow.id == flow_id).first()
    if not flow:
        raise HTTPException(status_code=404, detail="Fluxo não encontrado")
    
    executions = db.query(FlowExecution).filter(
        FlowExecution.flow_id == flow_id
    ).order_by(FlowExecution.started_at.desc()).all()
    
    summary = {
        "flow": {
            "id": flow.id,
            "name": flow.name
        },
        "total_executions": len(executions),
        "by_status": {},
        "recent_executions": []
    }
    
    # Contar por status
    for execution in executions:
        status = execution.status
        summary["by_status"][status] = summary["by_status"].get(status, 0) + 1
    
    # Últimas 20 execuções
    for execution in executions[:20]:
        contact = db.query(Contact).filter(Contact.id == execution.contact_id).first()
        
        # Contar logs da execução
        log_count = db.query(FlowExecutionLog).filter(
            FlowExecutionLog.flow_execution_id == execution.id
        ).count()
        
        summary["recent_executions"].append({
            "id": execution.id,
            "contact": {
                "id": contact.id if contact else None,
                "username": contact.username if contact else None
            },
            "status": execution.status,
            "current_step_id": execution.current_step_id,
            "log_count": log_count,
            "started_at": execution.started_at.isoformat() if execution.started_at else None,
            "updated_at": execution.updated_at.isoformat() if execution.updated_at else None
        })
    
    return summary

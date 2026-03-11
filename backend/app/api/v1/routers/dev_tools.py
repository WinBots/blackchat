"""
Endpoints para desenvolvimento e debugging
ATENÇÃO: Estes endpoints devem ser desabilitados em produção
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import desc
import json
import logging

from app.core.auth import require_super_admin
from app.db.models.user import User
from app.db.session import get_db
from app.db.models.contact import Contact
from app.db.models.channel import Channel
from app.db.models.flow import Flow
from app.db.models.flow_execution import FlowExecution
from app.db.models.flow_execution_log import FlowExecutionLog
from app.db.models.message import Message

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/dev/reset-lead/{username}")
async def reset_lead(username: str, db: Session = Depends(get_db), _: User = Depends(require_super_admin)):
    """
    Limpa todos os dados de teste de um lead específico.
    ÚTIL PARA DESENVOLVIMENTO: Limpa execuções, logs e mensagens para poder testar novamente.
    """
    contact = db.query(Contact).filter(Contact.username == username).first()
    
    if not contact:
        raise HTTPException(status_code=404, detail=f"Lead {username} não encontrado")
    
    # Buscar todas as execuções
    executions = db.query(FlowExecution).filter(
        FlowExecution.contact_id == contact.id
    ).all()
    
    execution_ids = [e.id for e in executions]
    
    # Contar o que será deletado
    logs_count = db.query(FlowExecutionLog).filter(
        FlowExecutionLog.flow_execution_id.in_(execution_ids)
    ).count() if execution_ids else 0
    
    messages_count = db.query(Message).filter(
        Message.contact_id == contact.id
    ).count()
    
    # Deletar logs (cascade vai deletar automaticamente, mas vamos ser explícitos)
    if execution_ids:
        db.query(FlowExecutionLog).filter(
            FlowExecutionLog.flow_execution_id.in_(execution_ids)
        ).delete(synchronize_session=False)
    
    # Deletar execuções
    db.query(FlowExecution).filter(
        FlowExecution.contact_id == contact.id
    ).delete(synchronize_session=False)
    
    # Deletar mensagens
    db.query(Message).filter(
        Message.contact_id == contact.id
    ).delete(synchronize_session=False)
    
    # Limpar custom_fields do contato
    contact.custom_fields = None
    
    db.commit()
    
    return {
        "success": True,
        "message": f"Lead {username} resetado com sucesso",
        "deleted": {
            "executions": len(executions),
            "logs": logs_count,
            "messages": messages_count
        }
    }


@router.post("/dev/start-flow", dependencies=[Depends(require_super_admin)])
async def start_flow_manual(
    username: str,
    flow_id: int,
    db: Session = Depends(get_db)
):
    """
    Inicia um fluxo manualmente para um lead de teste.
    ÚTIL PARA DESENVOLVIMENTO: Permite iniciar qualquer fluxo sem precisar usar gatilhos.
    """
    contact = db.query(Contact).filter(Contact.username == username).first()
    
    if not contact:
        raise HTTPException(status_code=404, detail=f"Lead {username} não encontrado")
    
    flow = db.query(Flow).filter(Flow.id == flow_id).first()
    
    if not flow:
        raise HTTPException(status_code=404, detail=f"Flow {flow_id} não encontrado")
    
    # Buscar canal do contato (primeiro canal ativo)
    channel = db.query(Channel).filter(
        Channel.tenant_id == contact.tenant_id,
        Channel.is_active == True
    ).first()
    
    if not channel:
        raise HTTPException(status_code=404, detail="Nenhum canal ativo encontrado")
    
    # Criar nova execução
    execution = FlowExecution(
        tenant_id=contact.tenant_id,
        contact_id=contact.id,
        flow_id=flow.id,
        trigger_type='manual',
        status='active'
    )
    db.add(execution)
    db.commit()
    db.refresh(execution)
    
    # Importar a função de execução de fluxo
    from app.api.v1.routers.telegram import run_flow_background
    
    # Executar fluxo em background
    import asyncio
    from fastapi import BackgroundTasks
    
    # Buscar informações do Telegram
    telegram_config = json.loads(channel.config) if channel.config else {}
    bot_token = telegram_config.get("bot_token", "")
    
    # Executar diretamente (não é ideal, mas funciona para dev)
    try:
        run_flow_background(
            channel_id=channel.id,
            contact_id=contact.id,
            flow_id=flow.id,
            chat_id=contact.external_id,
            bot_token=bot_token,
            execution_id=execution.id
        )
    except Exception as e:
        logger.error(f"Erro ao executar fluxo: {e}")
        raise HTTPException(status_code=500, detail=f"Erro ao executar fluxo: {str(e)}")
    
    return {
        "success": True,
        "message": f"Fluxo '{flow.name}' iniciado para {username}",
        "execution_id": execution.id,
        "flow_id": flow.id,
        "contact_id": contact.id
    }


@router.get("/dev/lead-history/{username}", dependencies=[Depends(require_super_admin)])
async def get_lead_history(username: str, db: Session = Depends(get_db)):
    """
    Retorna TODO o histórico de um lead: execuções, steps, logs, mensagens.
    ÚTIL PARA DESENVOLVIMENTO: Ver exatamente o que aconteceu com o lead.
    """
    contact = db.query(Contact).filter(Contact.username == username).first()
    
    if not contact:
        raise HTTPException(status_code=404, detail=f"Lead {username} não encontrado")
    
    # Buscar execuções
    executions = db.query(FlowExecution).filter(
        FlowExecution.contact_id == contact.id
    ).order_by(desc(FlowExecution.started_at)).all()
    
    result = {
        "contact": {
            "id": contact.id,
            "username": contact.username,
            "first_name": contact.first_name,
            "last_name": contact.last_name,
            "custom_fields": json.loads(contact.custom_fields) if contact.custom_fields else {}
        },
        "executions": []
    }
    
    for execution in executions:
        # Buscar logs dessa execução
        logs = db.query(FlowExecutionLog).filter(
            FlowExecutionLog.flow_execution_id == execution.id
        ).order_by(FlowExecutionLog.created_at).all()
        
        # Buscar mensagens dessa execução
        messages = db.query(Message).filter(
            Message.flow_execution_id == execution.id
        ).order_by(Message.created_at).all()
        
        execution_data = {
            "id": execution.id,
            "flow_id": execution.flow_id,
            "flow_name": execution.flow.name if execution.flow else None,
            "status": execution.status,
            "current_step_id": execution.current_step_id,
            "trigger_type": execution.trigger_type,
            "started_at": execution.started_at.isoformat() if execution.started_at else None,
            "completed_at": execution.completed_at.isoformat() if execution.completed_at else None,
            "updated_at": execution.updated_at.isoformat() if execution.updated_at else None,
            "context": json.loads(execution.context) if execution.context else None,
            "logs": [],
            "messages": []
        }
        
        # Adicionar logs
        for log in logs:
            execution_data["logs"].append({
                "id": log.id,
                "step_id": log.step_id,
                "log_type": log.log_type,
                "description": log.description,
                "data": json.loads(log.data) if log.data else None,
                "error_message": log.error_message,
                "created_at": log.created_at.isoformat() if log.created_at else None
            })
        
        # Adicionar mensagens
        for msg in messages:
            execution_data["messages"].append({
                "id": msg.id,
                "step_id": msg.step_id,
                "direction": msg.direction,
                "content": msg.content,
                "message_type": msg.message_type,
                "status": msg.status,
                "created_at": msg.created_at.isoformat() if msg.created_at else None
            })
        
        result["executions"].append(execution_data)
    
    # Adicionar também mensagens sem execução (antigas)
    orphan_messages = db.query(Message).filter(
        Message.contact_id == contact.id,
        Message.flow_execution_id == None
    ).order_by(desc(Message.created_at)).all()
    
    result["orphan_messages"] = []
    for msg in orphan_messages:
        result["orphan_messages"].append({
            "id": msg.id,
            "direction": msg.direction,
            "content": msg.content,
            "message_type": msg.message_type,
            "created_at": msg.created_at.isoformat() if msg.created_at else None
        })
    
    return result


@router.get("/dev/executions/active", dependencies=[Depends(require_super_admin)])
async def get_active_executions(db: Session = Depends(get_db)):
    """
    Lista todas as execuções ativas ou aguardando resposta.
    ÚTIL PARA DESENVOLVIMENTO: Ver quais fluxos estão rodando ou pausados.
    """
    executions = db.query(FlowExecution).filter(
        FlowExecution.status.in_(['active', 'waiting_response'])
    ).order_by(desc(FlowExecution.updated_at)).all()
    
    result = []
    for execution in executions:
        result.append({
            "id": execution.id,
            "contact_id": execution.contact_id,
            "contact_username": execution.contact.username if execution.contact else None,
            "flow_id": execution.flow_id,
            "flow_name": execution.flow.name if execution.flow else None,
            "status": execution.status,
            "current_step_id": execution.current_step_id,
            "context": json.loads(execution.context) if execution.context else None,
            "started_at": execution.started_at.isoformat() if execution.started_at else None,
            "updated_at": execution.updated_at.isoformat() if execution.updated_at else None
        })
    
    return {
        "count": len(result),
        "executions": result
    }

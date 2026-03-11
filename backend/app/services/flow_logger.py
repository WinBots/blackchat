"""
Helper para logging de execução de fluxos
"""
import json
from datetime import datetime
from sqlalchemy.orm import Session
from app.db.models.flow_execution_log import FlowExecutionLog


class FlowLogger:
    """Classe helper para registrar logs de execução de fluxos"""
    
    def __init__(self, db: Session, flow_execution_id: int):
        self.db = db
        self.flow_execution_id = flow_execution_id
    
    def log(
        self, 
        log_type: str, 
        description: str, 
        step_id: int = None,
        data: dict = None,
        error_message: str = None
    ):
        """Registra um log de execução"""
        log_entry = FlowExecutionLog(
            flow_execution_id=self.flow_execution_id,
            step_id=step_id,
            log_type=log_type,
            description=description,
            data=json.dumps(data, ensure_ascii=False) if data else None,
            error_message=error_message
        )
        self.db.add(log_entry)
        self.db.commit()
        return log_entry
    
    def step_start(self, step_id: int, step_type: str, step_config: dict = None):
        """Log de início de step"""
        return self.log(
            log_type='step_start',
            description=f'Iniciando step tipo: {step_type}',
            step_id=step_id,
            data=step_config
        )
    
    def step_complete(self, step_id: int, step_type: str, result: dict = None):
        """Log de conclusão de step"""
        return self.log(
            log_type='step_complete',
            description=f'Step concluído: {step_type}',
            step_id=step_id,
            data=result
        )
    
    def message_sent(self, step_id: int, message_id: int, content: str):
        """Log de mensagem enviada"""
        return self.log(
            log_type='message_sent',
            description=f'Mensagem enviada',
            step_id=step_id,
            data={'message_id': message_id, 'content': content}
        )
    
    def action_executed(self, step_id: int, action_type: str, result: dict = None):
        """Log de ação executada"""
        return self.log(
            log_type='action_executed',
            description=f'Ação executada: {action_type}',
            step_id=step_id,
            data=result
        )
    
    def condition_evaluated(self, step_id: int, condition_result: bool, next_step_id: int = None):
        """Log de avaliação de condição"""
        return self.log(
            log_type='condition_evaluated',
            description=f'Condição avaliada: {"✓ Verdadeira" if condition_result else "✗ Falsa"}',
            step_id=step_id,
            data={'result': condition_result, 'next_step_id': next_step_id}
        )
    
    def flow_paused(self, step_id: int, reason: str, waiting_for: str = None):
        """Log de pausa do fluxo"""
        return self.log(
            log_type='flow_paused',
            description=f'Fluxo pausado: {reason}',
            step_id=step_id,
            data={'waiting_for': waiting_for}
        )
    
    def flow_resumed(self, step_id: int, trigger_message: str = None):
        """Log de retomada do fluxo"""
        return self.log(
            log_type='flow_resumed',
            description='Fluxo retomado após resposta do usuário',
            step_id=step_id,
            data={'trigger_message': trigger_message}
        )
    
    def error(self, step_id: int, error_msg: str, error_data: dict = None):
        """Log de erro"""
        return self.log(
            log_type='error',
            description='Erro durante execução',
            step_id=step_id,
            data=error_data,
            error_message=error_msg
        )
    
    def info(self, description: str, data: dict = None):
        """Log de informação geral"""
        return self.log(
            log_type='info',
            description=description,
            data=data
        )

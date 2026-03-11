from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.session import Base

class FlowExecutionLog(Base):
    """
    Registra cada passo da execução de um fluxo.
    Permite rastreamento completo do histórico de um lead.
    """
    __tablename__ = "flow_execution_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    flow_execution_id = Column(Integer, ForeignKey("flow_executions.id"), nullable=False, index=True)
    step_id = Column(Integer, ForeignKey("flow_steps.id"), nullable=True)  # Null para eventos do sistema
    
    # Tipo de log: 'step_start', 'step_complete', 'message_sent', 'action_executed', 
    # 'condition_evaluated', 'flow_paused', 'flow_resumed', 'error', 'info'
    log_type = Column(String(50), nullable=False, index=True)
    
    # Descrição legível do que aconteceu
    description = Column(Text, nullable=True)
    
    # Dados em JSON: configuração do step, resultado da ação, etc
    data = Column(Text, nullable=True)
    
    # Para rastreamento de erros
    error_message = Column(Text, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    # Relationships
    flow_execution = relationship("FlowExecution", back_populates="logs")
    step = relationship("FlowStep")

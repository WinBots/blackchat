from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.db.session import Base


class FlowExecution(Base):
    """Registra cada execução de um fluxo para um contato"""
    __tablename__ = "flow_executions"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False, index=True)
    contact_id = Column(Integer, ForeignKey("contacts.id"), nullable=False, index=True)
    flow_id = Column(Integer, ForeignKey("flows.id"), nullable=False, index=True)
    
    # Tipo de execução
    trigger_type = Column(String(50), nullable=False)  # 'manual', 'keyword', 'webhook', 'schedule'
    
    # Status da execução
    status = Column(String(50), nullable=False, default='started', index=True)  # 'active', 'waiting_response', 'completed', 'failed', 'cancelled'
    
    # Step atual (para fluxos que aguardam input)
    current_step_id = Column(Integer, ForeignKey("flow_steps.id"), nullable=True)
    
    # Contexto da execução (JSON)
    # Armazena: waiting_for_field, last_question, temporary_data, etc
    context = Column(Text, nullable=True)
    
    # Metadados
    started_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relacionamentos
    contact = relationship("Contact")
    flow = relationship("Flow")
    logs = relationship("FlowExecutionLog", back_populates="flow_execution", cascade="all, delete-orphan")

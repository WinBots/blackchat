from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean
from sqlalchemy.sql import func

from app.db.session import Base


class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False, index=True)
    contact_id = Column(Integer, ForeignKey("contacts.id"), nullable=False, index=True)
    channel_id = Column(Integer, ForeignKey("channels.id"), nullable=True)
    flow_id = Column(Integer, ForeignKey("flows.id"), nullable=True)
    flow_execution_id = Column(Integer, ForeignKey("flow_executions.id"), nullable=True, index=True)
    step_id = Column(Integer, ForeignKey("flow_steps.id"), nullable=True)
    
    # Direção da mensagem
    direction = Column(String(20), nullable=False, index=True)  # 'inbound' ou 'outbound'
    
    # Conteúdo
    content = Column(Text, nullable=True)
    message_type = Column(String(50), nullable=True)  # 'text', 'image', 'button', etc
    
    # Metadados
    external_id = Column(String(255), nullable=True)  # ID da mensagem no Telegram, Instagram, etc
    extra_data = Column(Text, nullable=True)  # JSON com dados extras
    
    # Status
    status = Column(String(50), nullable=True)  # 'sent', 'delivered', 'read', 'failed'
    error_message = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


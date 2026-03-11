from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean, JSON, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.db.session import Base


class Sequence(Base):
    """Sequências de mensagens automáticas"""
    __tablename__ = "sequences"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False)
    name = Column(String(100), nullable=False, index=True)
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    steps = Column(JSON, default=list, nullable=False)  # Lista de passos com delays
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    enrollments = relationship("ContactSequence", back_populates="sequence", cascade="all, delete-orphan")


class ContactSequence(Base):
    """Relacionamento entre contatos e sequências"""
    __tablename__ = "contact_sequences"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False)
    contact_id = Column(Integer, ForeignKey("contacts.id", ondelete="CASCADE"), nullable=False)
    sequence_id = Column(Integer, ForeignKey("sequences.id", ondelete="CASCADE"), nullable=False)
    status = Column(String(20), default="active", nullable=False)  # active, paused, completed, cancelled
    current_step = Column(Integer, default=0, nullable=False)
    next_execution_at = Column(DateTime(timezone=True), nullable=True)
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    contact = relationship("Contact", back_populates="sequences")
    sequence = relationship("Sequence", back_populates="enrollments")

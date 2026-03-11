from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.db.session import Base


class LimitEvent(Base):
    """Registra eventos de limite atingido por tenant — auditoria e controle de grace period."""
    __tablename__ = "limit_events"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False, index=True)

    # Qual limite foi atingido
    limit_type = Column(String(50), nullable=False)   # contacts | flows | tags | sequences | users
    limit_value = Column(Integer, nullable=False)      # Valor do limite do plano
    current_value = Column(Integer, nullable=False)    # Valor atual do tenant

    # Ciclo de vida do evento
    detected_at = Column(DateTime(timezone=True), server_default=func.now())
    status = Column(String(50), default="warning")    # warning | grace_period | blocked_partial | resolved
    resolved_at = Column(DateTime(timezone=True), nullable=True)

    tenant = relationship("Tenant")

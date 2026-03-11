from sqlalchemy import Column, Integer, String, Numeric, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.db.session import Base


class BillingSnapshot(Base):
    """Snapshot mensal de billing por tenant — registra apuração VPM para auditoria e reconciliação."""
    __tablename__ = "billing_snapshots"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False, index=True)
    plan_id = Column(Integer, ForeignKey("plans.id"), nullable=True)

    # Período de apuração
    period_start = Column(DateTime(timezone=True), nullable=False)
    period_end = Column(DateTime(timezone=True), nullable=False)

    # Apuração VPM
    active_contacts_count = Column(Integer, nullable=False, default=0)   # Contatos ativos no período
    thousand_blocks = Column(Integer, nullable=False, default=0)          # ceil(active / 1000)
    vpm_value = Column(Numeric(10, 2), nullable=True)                    # VPM do plano na época
    minimum_applied = Column(Boolean, default=False)                     # Se o mínimo mensal foi aplicado
    final_amount = Column(Numeric(10, 2), nullable=False, default=0)     # Valor final cobrado/estimado

    # Referência do plano na época
    plan_name = Column(String(100), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relacionamentos
    tenant = relationship("Tenant")
    plan = relationship("Plan", back_populates="billing_snapshots")

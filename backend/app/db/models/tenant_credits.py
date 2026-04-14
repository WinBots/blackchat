from sqlalchemy import Column, Integer, String, Date, DateTime, ForeignKey
from sqlalchemy.sql import func

from app.db.session import Base


class TenantCredits(Base):
    """Saldo de créditos IA por workspace (tenant)."""
    __tablename__ = "tenant_credits"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False, unique=True, index=True)

    # Créditos do plano (renovam na data de vencimento, não acumulam)
    plan_balance = Column(Integer, nullable=False, default=0)
    plan_monthly_allocation = Column(Integer, nullable=False, default=0)
    plan_reset_date = Column(Date, nullable=True)

    # Créditos comprados (permanentes)
    purchased_balance = Column(Integer, nullable=False, default=0)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class CreditTransaction(Base):
    """Histórico de transações de créditos IA."""
    __tablename__ = "credit_transactions"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False, index=True)

    # Tipo: plan_allocation | purchased | consumed | refunded | admin_adjustment
    type = Column(String(50), nullable=False)
    source = Column(String(50), nullable=True)   # plan | purchased (para consumed)

    amount = Column(Integer, nullable=False)
    reason = Column(String(255), nullable=True)

    plan_balance_before = Column(Integer, nullable=True)
    plan_balance_after = Column(Integer, nullable=True)
    purchased_balance_before = Column(Integer, nullable=True)
    purchased_balance_after = Column(Integer, nullable=True)

    created_by = Column(String(50), nullable=True)    # system | stripe | admin
    stripe_event_id = Column(String(255), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

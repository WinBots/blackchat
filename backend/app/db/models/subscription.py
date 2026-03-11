from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum

from app.db.session import Base


class SubscriptionStatus(str, enum.Enum):
    """Status da assinatura"""
    TRIAL = "trial"       # Período de teste
    ACTIVE = "active"     # Ativa e em dia
    PAST_DUE = "past_due" # Pagamento atrasado (acesso mantido + avisos)
    UNPAID = "unpaid"     # Não pago após retentativas (ações sensíveis restritas)
    CANCELED = "canceled" # Cancelada
    EXPIRED = "expired"   # Expirada (trial encerrado)


class Subscription(Base):
    """Modelo de Assinatura"""
    __tablename__ = "subscriptions"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False, index=True)
    plan_id = Column(Integer, ForeignKey("plans.id"), nullable=False)
    
    status = Column(Enum(SubscriptionStatus), default=SubscriptionStatus.TRIAL, nullable=False)
    
    # Datas
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    trial_ends_at = Column(DateTime(timezone=True), nullable=True)  # Fim do trial
    current_period_start = Column(DateTime(timezone=True), nullable=True)
    current_period_end = Column(DateTime(timezone=True), nullable=True)
    canceled_at = Column(DateTime(timezone=True), nullable=True)
    
    # Uso atual (contadores para controle de limites)
    current_bots_count = Column(Integer, default=0)
    current_contacts_count = Column(Integer, default=0)       # Total de contatos
    active_contacts_count = Column(Integer, default=0)        # Contatos ativos (últimos 30 dias) — base do VPM
    current_messages_count = Column(Integer, default=0)       # Resetado mensalmente

    # Contatos contratados (Enterprise: valor escolhido no checkout; Pro: implícito pelo plano)
    contracted_contacts = Column(Integer, nullable=True)

    # Stripe linkage (opcional)
    stripe_subscription_id = Column(String(255), nullable=True)
    stripe_price_id = Column(String(255), nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relacionamentos
    tenant = relationship("Tenant", back_populates="subscriptions")
    plan = relationship("Plan", back_populates="subscriptions")


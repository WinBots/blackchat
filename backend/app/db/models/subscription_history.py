from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.sql import func

from app.db.session import Base


class SubscriptionHistory(Base):
    """
    Histórico de mudanças de plano/status de assinaturas.
    Gravado toda vez que ocorre upgrade, downgrade, cancelamento ou
    qualquer outra alteração relevante detectada via webhook Stripe.
    """
    __tablename__ = "subscription_history"

    id              = Column(Integer, primary_key=True, index=True)
    subscription_id = Column(Integer, ForeignKey("subscriptions.id"), nullable=True, index=True)
    tenant_id       = Column(Integer, nullable=True, index=True)

    # Tipo do evento: "plan_change", "status_change", "cancellation", "activation"
    event_type      = Column(String(50), nullable=False)

    old_plan_name   = Column(String(100), nullable=True)
    new_plan_name   = Column(String(100), nullable=True)
    old_status      = Column(String(50),  nullable=True)
    new_status      = Column(String(50),  nullable=True)

    stripe_mode     = Column(String(10),  nullable=True)   # "test" | "live"
    note            = Column(String(500), nullable=True)

    created_at      = Column(DateTime(timezone=True), server_default=func.now())

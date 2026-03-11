from sqlalchemy import Column, Integer, String, Numeric, Boolean, Text
from sqlalchemy.orm import relationship

from app.db.session import Base


class Plan(Base):
    __tablename__ = "plans"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, index=True, nullable=False)
    display_name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)

    # Preços
    price_monthly = Column(Numeric(10, 2), nullable=False, default=0)
    price_yearly = Column(Numeric(10, 2), nullable=True)
    vpm_price = Column(Numeric(10, 2), nullable=True)      # VPM (Valor Por Mil)
    min_monthly = Column(Numeric(10, 2), nullable=True)    # Mínimo pago no VPM

    # Limites
    max_bots = Column(Integer, nullable=True)
    max_contacts = Column(Integer, nullable=True)
    max_messages_per_month = Column(Integer, nullable=True)
    max_flows = Column(Integer, nullable=True)
    max_tags = Column(Integer, nullable=True)
    max_sequences = Column(Integer, nullable=True)

    # Features / Permissões
    has_advanced_flows = Column(Boolean, default=False)
    has_api_access = Column(Boolean, default=False)
    has_webhooks = Column(Boolean, default=False)
    has_priority_support = Column(Boolean, default=False)
    has_whitelabel = Column(Boolean, default=False)
    has_early_access = Column(Boolean, default=False)

    is_active = Column(Boolean, default=True)

    # Integração Stripe
    stripe_price_id_monthly = Column(String(255), nullable=True)
    stripe_price_id_yearly = Column(String(255), nullable=True)

    # Relacionamentos
    subscriptions = relationship("Subscription", back_populates="plan")
    billing_snapshots = relationship("BillingSnapshot", back_populates="plan")



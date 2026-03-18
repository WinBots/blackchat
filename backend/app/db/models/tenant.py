from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.db.session import Base


class Tenant(Base):
    """Modelo de Tenant (Empresa/Conta)"""
    __tablename__ = "tenants"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False, index=True)
    is_active = Column(Boolean, default=True)

    # Configurações gerais
    timezone = Column(String(64), nullable=True)

    # Billing / Stripe
    stripe_customer_id = Column(String(255), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relacionamentos
    users = relationship("User", back_populates="tenant", foreign_keys="[User.tenant_id]")
    subscriptions = relationship("Subscription", back_populates="tenant")
    channels = relationship("Channel", back_populates="tenant")
    flows = relationship("Flow", back_populates="tenant")
    workspace_members = relationship("TenantUser", back_populates="tenant", lazy="selectin")

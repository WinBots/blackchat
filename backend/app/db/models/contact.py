from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.db.session import Base


class Contact(Base):
    __tablename__ = "contacts"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False)
    first_name = Column(String(255), nullable=True)
    last_name = Column(String(255), nullable=True)
    username = Column(String(255), nullable=True)
    default_channel_id = Column(Integer, ForeignKey("channels.id"), nullable=True)
    custom_fields = Column(JSON, default=dict, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Data da última interação — define "contato ativo" para fins de billing VPM (últimos 30 dias)
    last_interaction_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    tags = relationship("ContactTag", back_populates="contact", cascade="all, delete-orphan")
    sequences = relationship("ContactSequence", back_populates="contact", cascade="all, delete-orphan")


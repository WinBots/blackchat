from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Index
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.db.session import Base


class ContactTag(Base):
    """Tags para segmentação de contatos"""
    __tablename__ = "contact_tags"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False)
    contact_id = Column(Integer, ForeignKey("contacts.id", ondelete="CASCADE"), nullable=False)
    tag_name = Column(String(100), nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    contact = relationship("Contact", back_populates="tags")
    
    # Índice único para evitar tags duplicadas no mesmo contato
    __table_args__ = (
        Index('idx_contact_tag_unique', 'contact_id', 'tag_name', unique=True),
        Index('idx_tenant_tag', 'tenant_id', 'tag_name'),
    )

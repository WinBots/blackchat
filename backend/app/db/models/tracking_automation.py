from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.sql import func

from app.db.session import Base


class TrackingAutomation(Base):
    """Automação disparada automaticamente ao receber evento de tracking."""
    __tablename__ = "tracking_automations"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False, index=True)
    channel_id = Column(Integer, ForeignKey("channels.id"), nullable=False, index=True)
    event = Column(String(20), nullable=False)   # "entrou" | "saiu"
    flow_id = Column(Integer, ForeignKey("flows.id"), nullable=True)  # None = desativado
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    __table_args__ = (
        UniqueConstraint("tenant_id", "channel_id", "event", name="uq_tracking_automation"),
    )

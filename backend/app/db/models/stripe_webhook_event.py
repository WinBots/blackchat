from sqlalchemy import Column, Integer, String, DateTime, Text
from sqlalchemy.sql import func

from app.db.session import Base


class StripeWebhookEvent(Base):
    """Armazena eventos do Stripe para garantir idempotência no processamento de webhooks."""
    __tablename__ = "stripe_webhook_events"

    id = Column(Integer, primary_key=True, index=True)
    stripe_event_id = Column(String(255), unique=True, nullable=False, index=True)  # Chave de idempotência
    event_type = Column(String(100), nullable=False)   # ex: checkout.session.completed
    received_at = Column(DateTime(timezone=True), server_default=func.now())
    processed_at = Column(DateTime(timezone=True), nullable=True)
    status = Column(String(50), default="received")    # received | processed | error
    payload_json = Column(Text, nullable=True)         # Payload completo para debug/reprocessamento
    error_message = Column(Text, nullable=True)        # Mensagem de erro se falhou

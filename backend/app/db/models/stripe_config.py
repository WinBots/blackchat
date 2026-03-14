from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.sql import func

from app.db.session import Base


class StripeConfig(Base):
    """
    Configuração Stripe persistida no banco — uma linha por instalação.
    O superadmin alterna o modo test/live e edita chaves/IDs aqui.
    Nunca há mais de um registro (id = 1 sempre).
    """
    __tablename__ = "stripe_config"

    id = Column(Integer, primary_key=True, default=1)

    # Ambiente ativo: "test" ou "live"
    mode_active = Column(String(10), nullable=False, default="test")

    # ── Chaves Teste ──────────────────────────────────────────────────
    test_secret_key        = Column(Text, nullable=True)   # sk_test_...
    test_publishable_key   = Column(Text, nullable=True)   # pk_test_...
    test_webhook_secret    = Column(Text, nullable=True)   # whsec_...
    # Pro (teste): price recorrente mensal
    test_pro_price_id      = Column(String(255), nullable=True)
    # Enterprise (teste): product_id do produto BlackChat Enterprise
    test_enterprise_product_id = Column(String(255), nullable=True)

    # ── Chaves Live ───────────────────────────────────────────────────
    live_secret_key        = Column(Text, nullable=True)   # sk_live_...
    live_publishable_key   = Column(Text, nullable=True)   # pk_live_...
    live_webhook_secret    = Column(Text, nullable=True)   # whsec_...
    # Pro (live): price recorrente mensal
    live_pro_price_id      = Column(String(255), nullable=True)
    # Enterprise (live): product_id do produto BlackChat Enterprise
    live_enterprise_product_id = Column(String(255), nullable=True)

    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey
from sqlalchemy.sql import func

from app.db.session import Base


class PasswordResetToken(Base):
    """Token de redefinição de senha — expira em 1 hora e pode ser usado apenas uma vez."""
    __tablename__ = "password_reset_tokens"

    id            = Column(Integer, primary_key=True, index=True)
    user_id       = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    token         = Column(String(255), unique=True, nullable=False, index=True)
    expires_at    = Column(DateTime(timezone=True), nullable=False)
    used          = Column(Boolean, default=False, nullable=False)
    created_at    = Column(DateTime(timezone=True), server_default=func.now())

from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Numeric, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from app.db.session import Base


class Affiliate(Base):
    __tablename__ = "affiliates"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False, unique=True, index=True)
    password_hash = Column(String(255), nullable=False)
    code = Column(String(100), nullable=False, unique=True, index=True)
    commission_pct = Column(Numeric(5, 2), nullable=False, default=0)
    stripe_fee_pct = Column(Numeric(5, 2), nullable=False, default=0)
    withdraw_fee = Column(Numeric(10, 2), nullable=False, default=0)
    tax_pct = Column(Numeric(5, 2), nullable=False, default=0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    referrals = relationship("AffiliateReferral", back_populates="affiliate")
    sales = relationship("AffiliateSale", back_populates="affiliate")


class AffiliateReferral(Base):
    __tablename__ = "affiliate_referrals"

    id = Column(Integer, primary_key=True, index=True)
    affiliate_id = Column(Integer, ForeignKey("affiliates.id"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, unique=True, index=True)
    registered_at = Column(DateTime, default=datetime.utcnow)

    affiliate = relationship("Affiliate", back_populates="referrals")


class AffiliateSale(Base):
    __tablename__ = "affiliate_sales"

    id = Column(Integer, primary_key=True, index=True)
    affiliate_id = Column(Integer, ForeignKey("affiliates.id"), nullable=False, index=True)
    user_id = Column(Integer, nullable=True)
    stripe_event_id = Column(String(255), nullable=False, unique=True, index=True)
    gross_amount = Column(Numeric(10, 2), nullable=False, default=0)
    stripe_fee = Column(Numeric(10, 2), nullable=False, default=0)
    net_amount = Column(Numeric(10, 2), nullable=False, default=0)
    commission = Column(Numeric(10, 2), nullable=False, default=0)
    tax_deduction = Column(Numeric(10, 2), nullable=False, default=0)
    withdraw_fee = Column(Numeric(10, 2), nullable=False, default=0)
    final_amount = Column(Numeric(10, 2), nullable=False, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

    affiliate = relationship("Affiliate", back_populates="sales")

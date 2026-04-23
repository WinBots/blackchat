"""
Sistema de afiliados — autenticação via cookie aff_token (JWT 7 dias)
"""
import logging
from datetime import datetime, timedelta
from typing import Optional

from fastapi import APIRouter, Cookie, Depends, HTTPException, Response, status
from pydantic import BaseModel, EmailStr
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.auth import verify_password, get_password_hash, create_access_token, decode_token
from app.db.session import get_db
from app.db.models.affiliate import Affiliate, AffiliateReferral, AffiliateSale
from app.db.models import User
from app.core.auth import get_current_user

logger = logging.getLogger("affiliate")

router = APIRouter()


# ── Schemas ────────────────────────────────────────────────────────────────────

class AffiliateLoginRequest(BaseModel):
    email: EmailStr
    password: str


class AffiliateCreate(BaseModel):
    name: str
    email: EmailStr
    password: str
    commission_pct: float = 0
    stripe_fee_pct: float = 2.9
    withdraw_fee: float = 0
    tax_pct: float = 0


class AffiliateUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    commission_pct: Optional[float] = None
    stripe_fee_pct: Optional[float] = None
    withdraw_fee: Optional[float] = None
    tax_pct: Optional[float] = None
    is_active: Optional[bool] = None


# ── Auth helpers ───────────────────────────────────────────────────────────────

def _get_current_affiliate(
    aff_token: Optional[str] = Cookie(default=None),
    db: Session = Depends(get_db),
) -> Affiliate:
    if not aff_token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Não autenticado")
    try:
        payload = decode_token(aff_token)
    except HTTPException:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token inválido ou expirado")

    aff_id = payload.get("aff_id")
    if not aff_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token inválido")

    aff = db.query(Affiliate).filter(Affiliate.id == int(aff_id)).first()
    if not aff or not aff.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Afiliado não encontrado ou inativo")
    return aff


def _require_super_admin(
    current_user: User = Depends(get_current_user),
) -> User:
    if not current_user.is_super_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Acesso restrito a super administradores")
    return current_user


# ── Affiliate auth endpoints ───────────────────────────────────────────────────

@router.post("/auth/login")
def affiliate_login(
    data: AffiliateLoginRequest,
    response: Response,
    db: Session = Depends(get_db),
):
    email = data.email.strip().lower()
    aff = db.query(Affiliate).filter(func.lower(Affiliate.email) == email).first()
    if not aff or not verify_password(data.password, aff.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Credenciais inválidas")
    if not aff.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Conta inativa")

    token = create_access_token(
        data={"aff_id": aff.id},
        expires_delta=timedelta(days=7),
    )
    response.set_cookie(
        key="aff_token",
        value=token,
        httponly=True,
        samesite="lax",
        secure=True,
        max_age=60 * 60 * 24 * 7,
    )
    return {"ok": True, "affiliate": {"id": aff.id, "name": aff.name, "email": aff.email, "code": aff.code}}


@router.post("/auth/logout")
def affiliate_logout(response: Response):
    response.delete_cookie("aff_token")
    return {"ok": True}


@router.get("/auth/me")
def affiliate_me(aff: Affiliate = Depends(_get_current_affiliate)):
    return {
        "id": aff.id,
        "name": aff.name,
        "email": aff.email,
        "code": aff.code,
        "commission_pct": float(aff.commission_pct),
    }


# ── Affiliate dashboard ────────────────────────────────────────────────────────

@router.get("/dashboard")
def affiliate_dashboard(
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    aff: Affiliate = Depends(_get_current_affiliate),
    db: Session = Depends(get_db),
):
    q_sales = db.query(AffiliateSale).filter(AffiliateSale.affiliate_id == aff.id)
    if date_from:
        try:
            q_sales = q_sales.filter(AffiliateSale.created_at >= datetime.fromisoformat(date_from))
        except ValueError:
            pass
    if date_to:
        try:
            q_sales = q_sales.filter(AffiliateSale.created_at <= datetime.fromisoformat(date_to))
        except ValueError:
            pass

    sales = q_sales.all()
    referrals_count = db.query(AffiliateReferral).filter(AffiliateReferral.affiliate_id == aff.id).count()

    total_gross = sum(float(s.gross_amount) for s in sales)
    total_commission = sum(float(s.commission) for s in sales)
    total_final = sum(float(s.final_amount) for s in sales)

    return {
        "referrals": referrals_count,
        "sales_count": len(sales),
        "total_gross": round(total_gross, 2),
        "total_commission": round(total_commission, 2),
        "total_final": round(total_final, 2),
        "sales": [
            {
                "id": s.id,
                "gross_amount": float(s.gross_amount),
                "commission": float(s.commission),
                "final_amount": float(s.final_amount),
                "created_at": s.created_at.isoformat() if s.created_at else None,
            }
            for s in sales
        ],
    }


# ── Admin endpoints ────────────────────────────────────────────────────────────

@router.get("/admin/affiliates")
def list_affiliates(
    db: Session = Depends(get_db),
    _: User = Depends(_require_super_admin),
):
    affs = db.query(Affiliate).order_by(Affiliate.created_at.desc()).all()
    return [
        {
            "id": a.id,
            "name": a.name,
            "email": a.email,
            "code": a.code,
            "commission_pct": float(a.commission_pct),
            "stripe_fee_pct": float(a.stripe_fee_pct),
            "withdraw_fee": float(a.withdraw_fee),
            "tax_pct": float(a.tax_pct),
            "is_active": a.is_active,
            "created_at": a.created_at.isoformat() if a.created_at else None,
        }
        for a in affs
    ]


@router.post("/admin/affiliates", status_code=201)
def create_affiliate(
    data: AffiliateCreate,
    db: Session = Depends(get_db),
    _: User = Depends(_require_super_admin),
):
    email = data.email.strip().lower()
    if db.query(Affiliate).filter(func.lower(Affiliate.email) == email).first():
        raise HTTPException(status_code=400, detail="E-mail já cadastrado")

    # Gerar code único a partir do nome se não fornecido
    base_code = data.name.lower().replace(" ", "").replace("-", "")[:20]
    code = base_code
    counter = 1
    while db.query(Affiliate).filter(Affiliate.code == code).first():
        code = f"{base_code}{counter}"
        counter += 1

    aff = Affiliate(
        name=data.name,
        email=email,
        password_hash=get_password_hash(data.password),
        code=code,
        commission_pct=data.commission_pct,
        stripe_fee_pct=data.stripe_fee_pct,
        withdraw_fee=data.withdraw_fee,
        tax_pct=data.tax_pct,
        is_active=True,
    )
    db.add(aff)
    db.commit()
    db.refresh(aff)
    return {"id": aff.id, "code": aff.code, "email": aff.email}


@router.put("/admin/affiliates/{affiliate_id}")
def update_affiliate(
    affiliate_id: int,
    data: AffiliateUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(_require_super_admin),
):
    aff = db.query(Affiliate).filter(Affiliate.id == affiliate_id).first()
    if not aff:
        raise HTTPException(status_code=404, detail="Afiliado não encontrado")

    if data.name is not None:
        aff.name = data.name
    if data.email is not None:
        aff.email = data.email.strip().lower()
    if data.password is not None:
        aff.password_hash = get_password_hash(data.password)
    if data.commission_pct is not None:
        aff.commission_pct = data.commission_pct
    if data.stripe_fee_pct is not None:
        aff.stripe_fee_pct = data.stripe_fee_pct
    if data.withdraw_fee is not None:
        aff.withdraw_fee = data.withdraw_fee
    if data.tax_pct is not None:
        aff.tax_pct = data.tax_pct
    if data.is_active is not None:
        aff.is_active = data.is_active

    db.commit()
    return {"ok": True}


@router.delete("/admin/affiliates/{affiliate_id}")
def delete_affiliate(
    affiliate_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(_require_super_admin),
):
    aff = db.query(Affiliate).filter(Affiliate.id == affiliate_id).first()
    if not aff:
        raise HTTPException(status_code=404, detail="Afiliado não encontrado")
    db.delete(aff)
    db.commit()
    return {"ok": True}


@router.get("/admin/affiliates/{affiliate_id}/stats")
def affiliate_stats(
    affiliate_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(_require_super_admin),
):
    aff = db.query(Affiliate).filter(Affiliate.id == affiliate_id).first()
    if not aff:
        raise HTTPException(status_code=404, detail="Afiliado não encontrado")

    sales = db.query(AffiliateSale).filter(AffiliateSale.affiliate_id == affiliate_id).all()
    referrals_count = db.query(AffiliateReferral).filter(AffiliateReferral.affiliate_id == affiliate_id).count()

    return {
        "affiliate": {"id": aff.id, "name": aff.name, "email": aff.email, "code": aff.code},
        "referrals": referrals_count,
        "sales_count": len(sales),
        "total_gross": round(sum(float(s.gross_amount) for s in sales), 2),
        "total_commission": round(sum(float(s.commission) for s in sales), 2),
        "total_final": round(sum(float(s.final_amount) for s in sales), 2),
    }


# ── Função interna para registrar venda (chamada pelo webhook Stripe) ──────────

def register_affiliate_sale(
    tenant_id: int,
    stripe_event_id: str,
    gross_amount_cents: int,
    db: Session,
) -> None:
    """
    Verifica se o tenant veio de indicação de afiliado e registra a comissão.
    gross_amount_cents: valor em centavos do Stripe
    """
    # Evitar duplicata
    if db.query(AffiliateSale).filter(AffiliateSale.stripe_event_id == stripe_event_id).first():
        return

    # Buscar vínculo de indicação pelo tenant (user_id do owner do tenant)
    from app.db.models import User as UserModel
    owner = db.query(UserModel).filter(UserModel.tenant_id == tenant_id).first()
    if not owner:
        return

    referral = db.query(AffiliateReferral).filter(AffiliateReferral.user_id == owner.id).first()
    if not referral:
        return

    aff = db.query(Affiliate).filter(Affiliate.id == referral.affiliate_id).first()
    if not aff or not aff.is_active:
        return

    gross = gross_amount_cents / 100.0
    stripe_fee = round(gross * float(aff.stripe_fee_pct) / 100, 2)
    net = round(gross - stripe_fee, 2)
    commission = round(net * float(aff.commission_pct) / 100, 2)
    tax_deduction = round(commission * float(aff.tax_pct) / 100, 2)
    final = round(commission - tax_deduction - float(aff.withdraw_fee), 2)

    sale = AffiliateSale(
        affiliate_id=aff.id,
        user_id=owner.id,
        stripe_event_id=stripe_event_id,
        gross_amount=gross,
        stripe_fee=stripe_fee,
        net_amount=net,
        commission=commission,
        tax_deduction=tax_deduction,
        withdraw_fee=float(aff.withdraw_fee),
        final_amount=max(final, 0),
    )
    db.add(sale)
    db.commit()
    logger.info("[affiliate] venda registrada: affiliate_id=%d tenant_id=%d gross=%.2f commission=%.2f", aff.id, tenant_id, gross, commission)

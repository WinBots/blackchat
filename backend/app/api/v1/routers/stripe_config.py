"""
Router de configuração Stripe — acessível apenas pelo superadmin.

GET  /api/v1/admin/stripe-config          → retorna config mascarada
PUT  /api/v1/admin/stripe-config          → salva/atualiza config
PUT  /api/v1/admin/stripe-config/mode     → alterna test | live
"""
from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.db.models.stripe_config import StripeConfig
from app.services.stripe_service import mask_key
from app.api.v1.routers.admin import get_super_admin_user
from app.db.models.user import User

router = APIRouter()


# ──────────────────────────────────────────────────────────────────────────────
# Schemas
# ──────────────────────────────────────────────────────────────────────────────

class StripeConfigOut(BaseModel):
    """Versão pública (mascarada) retornada ao frontend."""
    mode_active: str

    # ── Teste ─────────────────────────────────────────────────────────
    test_secret_key_masked:       Optional[str] = None
    test_publishable_key_masked:  Optional[str] = None
    test_webhook_secret_masked:   Optional[str] = None
    test_pro_price_id:            Optional[str] = None
    test_enterprise_product_id:   Optional[str] = None

    # Indica se as chaves sensíveis estão preenchidas (sem expor o valor)
    test_secret_key_set:      bool = False
    test_webhook_secret_set:  bool = False

    # ── Live ──────────────────────────────────────────────────────────
    live_secret_key_masked:       Optional[str] = None
    live_publishable_key_masked:  Optional[str] = None
    live_webhook_secret_masked:   Optional[str] = None
    live_pro_price_id:            Optional[str] = None
    live_enterprise_product_id:   Optional[str] = None

    live_secret_key_set:      bool = False
    live_webhook_secret_set:  bool = False


class StripeConfigIn(BaseModel):
    """Payload de atualização — aceitar quaisquer campos, todos opcionais."""
    test_secret_key:             Optional[str] = None
    test_publishable_key:        Optional[str] = None
    test_webhook_secret:         Optional[str] = None
    test_pro_price_id:           Optional[str] = None
    test_enterprise_product_id:  Optional[str] = None

    live_secret_key:             Optional[str] = None
    live_publishable_key:        Optional[str] = None
    live_webhook_secret:         Optional[str] = None
    live_pro_price_id:           Optional[str] = None
    live_enterprise_product_id:  Optional[str] = None


class StripeModeIn(BaseModel):
    mode: str  # "test" | "live"


# ──────────────────────────────────────────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────────────────────────────────────────

def _get_or_create(db: Session) -> StripeConfig:
    cfg = db.query(StripeConfig).filter(StripeConfig.id == 1).first()
    if cfg is None:
        cfg = StripeConfig(id=1, mode_active="test")
        db.add(cfg)
        db.commit()
        db.refresh(cfg)
    return cfg


def _to_out(cfg: StripeConfig) -> StripeConfigOut:
    return StripeConfigOut(
        mode_active=cfg.mode_active or "test",

        test_secret_key_masked=mask_key(cfg.test_secret_key),
        test_publishable_key=cfg.test_publishable_key or None,   # ret. completo (chave pública)
        test_webhook_secret_masked=mask_key(cfg.test_webhook_secret),
        test_pro_price_id=cfg.test_pro_price_id,
        test_enterprise_product_id=cfg.test_enterprise_product_id,
        test_secret_key_set=bool((cfg.test_secret_key or "").strip()),
        test_webhook_secret_set=bool((cfg.test_webhook_secret or "").strip()),

        live_secret_key_masked=mask_key(cfg.live_secret_key),
        live_publishable_key=cfg.live_publishable_key or None,   # ret. completo (chave pública)
        live_webhook_secret_masked=mask_key(cfg.live_webhook_secret),
        live_pro_price_id=cfg.live_pro_price_id,
        live_enterprise_product_id=cfg.live_enterprise_product_id,
        live_secret_key_set=bool((cfg.live_secret_key or "").strip()),
        live_webhook_secret_set=bool((cfg.live_webhook_secret or "").strip()),
    )


# ──────────────────────────────────────────────────────────────────────────────
# Endpoints
# ──────────────────────────────────────────────────────────────────────────────

@router.get("/stripe-config", response_model=StripeConfigOut)
def get_stripe_config(
    db: Session = Depends(get_db),
    _: User = Depends(get_super_admin_user),
):
    """Retorna configuração Stripe com campos sensíveis mascarados."""
    return _to_out(_get_or_create(db))


@router.put("/stripe-config", response_model=StripeConfigOut)
def update_stripe_config(
    body: StripeConfigIn,
    db: Session = Depends(get_db),
    _: User = Depends(get_super_admin_user),
):
    """
    Atualiza campos de configuração.
    Envie apenas os campos que deseja alterar; os demais são preservados.
    Strings vazias são convertidas para None (limpar o campo).
    """
    cfg = _get_or_create(db)

    field_map = {
        "test_secret_key":            "test_secret_key",
        "test_publishable_key":       "test_publishable_key",
        "test_webhook_secret":        "test_webhook_secret",
        "test_pro_price_id":          "test_pro_price_id",
        "test_enterprise_product_id": "test_enterprise_product_id",
        "live_secret_key":            "live_secret_key",
        "live_publishable_key":       "live_publishable_key",
        "live_webhook_secret":        "live_webhook_secret",
        "live_pro_price_id":          "live_pro_price_id",
        "live_enterprise_product_id": "live_enterprise_product_id",
    }

    data = body.model_dump(exclude_unset=True)
    for key, col in field_map.items():
        if key in data:
            val = (data[key] or "").strip() or None
            setattr(cfg, col, val)

    db.commit()
    db.refresh(cfg)
    return _to_out(cfg)


@router.put("/stripe-config/mode", response_model=StripeConfigOut)
def set_stripe_mode(
    body: StripeModeIn,
    db: Session = Depends(get_db),
    _: User = Depends(get_super_admin_user),
):
    """Alterna o ambiente Stripe ativo entre 'test' e 'live'."""
    mode = (body.mode or "").lower()
    if mode not in ("test", "live"):
        raise HTTPException(status_code=400, detail="mode deve ser 'test' ou 'live'.")

    cfg = _get_or_create(db)

    # Só bloqueia ativação de LIVE sem secret_key (modo perigoso = dinheiro real).
    # Modo TEST não exige validação — é o modo seguro/padrão.
    if mode == "live" and not (cfg.live_secret_key or "").strip():
        raise HTTPException(
            status_code=400,
            detail="Configure a Live Secret Key antes de ativar o modo Live (produção).",
        )

    cfg.mode_active = mode
    db.commit()
    db.refresh(cfg)
    return _to_out(cfg)

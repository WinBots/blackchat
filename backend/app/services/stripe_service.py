"""
Serviço de resolução de credenciais Stripe.

O superadmin persiste chaves e IDs na tabela stripe_config.
Este serviço centraliza:
  - descobrir o modo ativo (test | live)
  - retornar as credenciais corretas para cada operação
  - validar que as credenciais necessárias existem antes de iniciar checkout

Toda chamada Stripe passa por aqui; o billing.py nunca lê stripe_config diretamente.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.db.models.stripe_config import StripeConfig


@dataclass
class StripeCredentials:
    mode: str                          # "test" | "live"
    secret_key: str
    publishable_key: Optional[str]
    webhook_secret: Optional[str]
    pro_price_id: Optional[str]        # None = Pro não configurado
    enterprise_product_id: Optional[str]  # None = Enterprise não configurado
    credits_product_id: Optional[str]  # None = Credits não configurado


def _get_config(db: Session) -> StripeConfig:
    """Retorna o registro singleton (id=1). Cria com defaults se não existir."""
    cfg = db.query(StripeConfig).filter(StripeConfig.id == 1).first()
    if cfg is None:
        cfg = StripeConfig(id=1, mode_active="test")
        db.add(cfg)
        db.commit()
        db.refresh(cfg)
    return cfg


def get_active_mode(db: Session) -> str:
    """Retorna 'test' ou 'live'."""
    return _get_config(db).mode_active or "test"


def get_credentials(db: Session) -> StripeCredentials:
    """
    Retorna as credenciais do ambiente ativo.
    Levanta ValueError se a secret_key não estiver configurada.
    """
    cfg = _get_config(db)
    mode = (cfg.mode_active or "test").lower()

    if mode == "live":
        secret_key      = cfg.live_secret_key
        pub_key         = cfg.live_publishable_key
        whsec           = cfg.live_webhook_secret
        pro_price_id    = cfg.live_pro_price_id
        ent_prod_id     = cfg.live_enterprise_product_id
        credits_prod_id = cfg.live_credits_product_id
    else:
        secret_key      = cfg.test_secret_key
        pub_key         = cfg.test_publishable_key
        whsec           = cfg.test_webhook_secret
        pro_price_id    = cfg.test_pro_price_id
        ent_prod_id     = cfg.test_enterprise_product_id
        credits_prod_id = cfg.test_credits_product_id

    if not (secret_key or "").strip():
        raise ValueError(
            f"Stripe não configurado: secret_key do modo '{mode}' está vazia. "
            "Acesse o painel Super Admin → Stripe para configurar."
        )

    return StripeCredentials(
        mode=mode,
        secret_key=secret_key.strip(),
        publishable_key=(pub_key or "").strip() or None,
        webhook_secret=(whsec or "").strip() or None,
        pro_price_id=(pro_price_id or "").strip() or None,
        enterprise_product_id=(ent_prod_id or "").strip() or None,
        credits_product_id=(credits_prod_id or "").strip() or None,
    )


def require_pro_credentials(db: Session) -> StripeCredentials:
    """Garante que pro_price_id está configurado.  Levanta HTTPException se não."""
    creds = _safe_get_creds(db)
    if not creds.pro_price_id:
        raise HTTPException(
            status_code=400,
            detail=(
                f"Price ID do plano Pro ([{creds.mode}] mode) não está configurado. "
                "Acesse Super Admin → Stripe para adicionar o Price ID."
            ),
        )
    return creds


def require_credits_credentials(db: Session) -> StripeCredentials:
    """Garante que credits_product_id está configurado. Levanta HTTPException se não."""
    creds = _safe_get_creds(db)
    if not creds.credits_product_id:
        raise HTTPException(
            status_code=400,
            detail=(
                f"Product ID de Créditos IA ([{creds.mode}] mode) não está configurado. "
                "Acesse Super Admin → Stripe para adicionar o Product ID."
            ),
        )
    return creds


def require_enterprise_credentials(db: Session) -> StripeCredentials:
    """Garante que enterprise_product_id está configurado.  Levanta HTTPException se não."""
    creds = _safe_get_creds(db)
    if not creds.enterprise_product_id:
        raise HTTPException(
            status_code=400,
            detail=(
                f"Product ID do Enterprise ([{creds.mode}] mode) não está configurado. "
                "Acesse Super Admin → Stripe para adicionar o Product ID."
            ),
        )
    return creds


def _safe_get_creds(db: Session) -> StripeCredentials:
    try:
        return get_credentials(db)
    except ValueError as exc:
        raise HTTPException(status_code=500, detail=str(exc))


def is_configured(db: Session) -> bool:
    """Retorna True se o modo ativo tem ao menos a secret_key preenchida."""
    try:
        get_credentials(db)
        return True
    except (ValueError, Exception):
        return False


def mask_key(value: Optional[str]) -> Optional[str]:
    """Retorna versão mascarada de chave sensível para exibição no frontend."""
    if not value:
        return None
    v = value.strip()
    if len(v) <= 8:
        return "***"
    return v[:7] + "..." + v[-4:]

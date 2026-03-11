"""
Email sender — todos os templates transacionais do Blackchat Pro.

Templates disponíveis:
  1. Conta criada          → send_welcome_email_background
  2. Plano ativado         → send_plan_activated_email_background
  3. Upgrade de plano      → send_plan_upgraded_email_background
  4. Limite do plano       → send_plan_limit_reached_email_background
  5. Assinatura cancelada  → send_subscription_canceled_email_background
  6. Recuperação de senha  → send_password_reset_email_background

Usa aiosmtplib (async) + wrapper síncrono para FastAPI BackgroundTasks.
"""
from __future__ import annotations

import asyncio
import logging
from email.message import EmailMessage
from typing import Optional

import aiosmtplib

from app.config import get_settings

logger = logging.getLogger(__name__)

# ─── Paleta Blackchat Pro ────────────────────────────────────────────────────
_BRAND_COLOR = "#4f46e5"   # indigo-600
_BRAND_NAME  = "Blackchat Pro"


# ─── Layout base ──────────────────────────────────────────────────────────────

def _wrap_html(
    *,
    title: str,
    body_html: str,
    action_url: Optional[str] = None,
    action_label: Optional[str] = None,
) -> str:
    """Envolve o conteúdo num layout responsivo minimalista com a marca Blackchat Pro."""
    cta = ""
    if action_url and action_label:
        cta = f"""
        <div style="text-align:center; margin:24px 0;">
          <a href="{action_url}"
             style="background:{_BRAND_COLOR}; color:#fff; text-decoration:none;
                    padding:12px 28px; border-radius:6px; font-weight:600;
                    display:inline-block; font-size:15px;">
            {action_label}
          </a>
        </div>"""

    return f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
</head>
<body style="margin:0; padding:0; background:#f3f4f6; font-family:Arial,Helvetica,sans-serif;">
  <table width="100%" cellpadding="0" cellspacing="0"
         style="background:#f3f4f6; padding:32px 16px;">
    <tr><td align="center">
      <table width="560" cellpadding="0" cellspacing="0"
             style="background:#fff; border-radius:12px; overflow:hidden;
                    box-shadow:0 2px 8px rgba(0,0,0,.08); max-width:100%;">

        <!-- Header -->
        <tr>
          <td style="background:{_BRAND_COLOR}; padding:22px 32px;">
            <span style="color:#fff; font-size:22px; font-weight:700; letter-spacing:-0.5px;">
              {_BRAND_NAME}
            </span>
          </td>
        </tr>

        <!-- Title -->
        <tr>
          <td style="padding:28px 32px 0 32px;">
            <h2 style="margin:0; font-size:20px; color:#111827;">{title}</h2>
          </td>
        </tr>

        <!-- Body -->
        <tr>
          <td style="padding:16px 32px 0 32px; color:#374151; font-size:15px; line-height:1.6;">
            {body_html}
            {cta}
          </td>
        </tr>

        <!-- Footer -->
        <tr>
          <td style="padding:24px 32px 32px 32px; color:#9ca3af; font-size:12px;
                     border-top:1px solid #f3f4f6; margin-top:24px;">
            <p style="margin:0;">
              Você está recebendo este e-mail porque possui uma conta no {_BRAND_NAME}.
            </p>
            <p style="margin:6px 0 0 0;">
              Se isso não foi você, ignore este e-mail com segurança.
            </p>
          </td>
        </tr>

      </table>
    </td></tr>
  </table>
</body>
</html>"""


def _build_message(
    *, to_email: str, subject: str, html_body: str, text_body: Optional[str] = None
) -> EmailMessage:
    settings = get_settings()
    from_field = (
        f"{settings.SMTP_FROM_NAME} <{settings.SMTP_FROM_EMAIL}>"
        if settings.SMTP_FROM_EMAIL
        else settings.SMTP_FROM_NAME
    )
    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"]    = from_field
    msg["To"]      = to_email
    msg.set_content(text_body or "Este e-mail requer um cliente com suporte a HTML.")
    msg.add_alternative(html_body, subtype="html")
    return msg


async def _send(msg: EmailMessage) -> None:
    """Envia a mensagem usando aiosmtplib. Respeita SMTP_ENABLED."""
    settings = get_settings()
    if not settings.SMTP_ENABLED:
        logger.debug("SMTP desabilitado — e-mail ignorado: %s", msg["Subject"])
        return
    if not (settings.SMTP_HOST and settings.SMTP_USER and settings.SMTP_PASSWORD and settings.SMTP_FROM_EMAIL):
        logger.info("SMTP incompleto — e-mail ignorado: %s", msg["Subject"])
        return
    await aiosmtplib.send(
        msg,
        hostname=settings.SMTP_HOST,
        port=settings.SMTP_PORT,
        username=settings.SMTP_USER,
        password=settings.SMTP_PASSWORD,
        start_tls=settings.SMTP_USE_TLS,
        use_tls=settings.SMTP_USE_SSL,
        timeout=20,
    )


def _run_async(coro) -> None:
    """Wrapper síncrono seguro para BackgroundTasks — compatível com loop existente."""
    try:
        asyncio.run(coro)
    except RuntimeError:
        loop = asyncio.new_event_loop()
        try:
            loop.run_until_complete(coro)
        finally:
            loop.close()


def _public_url() -> str:
    settings = get_settings()
    # Usa FRONTEND_URL quando disponível — links nos e-mails devem apontar para o frontend
    return getattr(settings, "FRONTEND_URL", getattr(settings, "PUBLIC_BASE_URL", "")).rstrip("/")


# ─── 1. Conta criada ──────────────────────────────────────────────────────────

async def send_welcome_email(
    *,
    to_email: str,
    full_name: Optional[str] = None,
    company_name: Optional[str] = None,
) -> None:
    display = (full_name or "").strip() or to_email
    company = (company_name or "").strip()

    body = f"""
    <p>Olá, <strong>{display}</strong>!</p>
    <p>
      Sua conta no <strong>{_BRAND_NAME}</strong> foi criada com sucesso
      {f'para <strong>{company}</strong>' if company else ''}.
    </p>
    <p>
      Você já está no plano <strong>Free</strong> e pode começar agora mesmo
      a criar automações, organizar contatos e enviar mensagens em massa.
    </p>
    <p>Acesse o painel e explore tudo que preparamos para você 🚀</p>
    """
    html = _wrap_html(
        title="Bem-vindo ao Blackchat Pro! 🎉",
        body_html=body,
        action_url=f"{_public_url()}/#/dashboard",
        action_label="Acessar painel",
    )
    msg = _build_message(
        to_email=to_email,
        subject="Bem-vindo ao Blackchat Pro — sua conta foi criada",
        html_body=html,
    )
    try:
        await _send(msg)
    except Exception:
        logger.exception("Falha ao enviar e-mail de boas-vindas para %s", to_email)


def send_welcome_email_background(
    *,
    to_email: str,
    full_name: Optional[str] = None,
    company_name: Optional[str] = None,
) -> None:
    _run_async(send_welcome_email(to_email=to_email, full_name=full_name, company_name=company_name))


# ─── 2. Plano ativado ─────────────────────────────────────────────────────────

async def send_plan_activated_email(
    *,
    to_email: str,
    full_name: Optional[str] = None,
    plan_name: str = "",
    interval: str = "monthly",
) -> None:
    display        = (full_name or "").strip() or to_email
    interval_label = "anual" if interval == "yearly" else "mensal"

    body = f"""
    <p>Olá, <strong>{display}</strong>!</p>
    <p>
      Sua assinatura do plano <strong>{plan_name}</strong> ({interval_label})
      foi ativada com sucesso. ✅
    </p>
    <p>
      Agora você tem acesso a todos os recursos do seu plano.
      Qualquer dúvida, estamos à disposição.
    </p>
    """
    html = _wrap_html(
        title=f"Plano {plan_name} ativado",
        body_html=body,
        action_url=f"{_public_url()}/#/settings?tab=Assinaturas",
        action_label="Ver assinatura",
    )
    msg = _build_message(
        to_email=to_email,
        subject=f"Blackchat Pro — seu plano {plan_name} foi ativado",
        html_body=html,
    )
    try:
        await _send(msg)
    except Exception:
        logger.exception("Falha ao enviar e-mail de plano ativado para %s", to_email)


def send_plan_activated_email_background(
    *,
    to_email: str,
    full_name: Optional[str] = None,
    plan_name: str = "",
    interval: str = "monthly",
) -> None:
    _run_async(send_plan_activated_email(
        to_email=to_email, full_name=full_name, plan_name=plan_name, interval=interval
    ))


# ─── 3. Upgrade / Downgrade de plano ─────────────────────────────────────────

async def send_plan_upgraded_email(
    *,
    to_email: str,
    full_name: Optional[str] = None,
    old_plan: str = "",
    new_plan: str = "",
) -> None:
    display = (full_name or "").strip() or to_email

    body = f"""
    <p>Olá, <strong>{display}</strong>!</p>
    <p>
      Seu plano foi atualizado de <strong>{old_plan}</strong>
      para <strong>{new_plan}</strong>.
    </p>
    <p>As novas funcionalidades já estão disponíveis na sua conta. Aproveite! 🚀</p>
    """
    html = _wrap_html(
        title=f"Plano atualizado para {new_plan}",
        body_html=body,
        action_url=f"{_public_url()}/#/settings?tab=Assinaturas",
        action_label="Ver assinatura",
    )
    msg = _build_message(
        to_email=to_email,
        subject=f"Blackchat Pro — seu plano foi atualizado para {new_plan}",
        html_body=html,
    )
    try:
        await _send(msg)
    except Exception:
        logger.exception("Falha ao enviar e-mail de upgrade para %s", to_email)


def send_plan_upgraded_email_background(
    *,
    to_email: str,
    full_name: Optional[str] = None,
    old_plan: str = "",
    new_plan: str = "",
) -> None:
    _run_async(send_plan_upgraded_email(
        to_email=to_email, full_name=full_name, old_plan=old_plan, new_plan=new_plan
    ))


# ─── 4. Limite do plano atingido ─────────────────────────────────────────────

async def send_plan_limit_reached_email(
    *,
    to_email: str,
    full_name: Optional[str] = None,
    limit_type: str = "",
    current: int = 0,
    limit: int = 0,
    plan_name: str = "",
) -> None:
    display = (full_name or "").strip() or to_email
    type_labels = {
        "contacts":  "contatos ativos",
        "flows":     "fluxos",
        "sequences": "sequências",
        "tags":      "tags",
        "users":     "usuários",
    }
    type_label = type_labels.get(limit_type, limit_type)

    body = f"""
    <p>Olá, <strong>{display}</strong>!</p>
    <p>
      Você atingiu o limite de <strong>{type_label}</strong> do seu plano
      <strong>{plan_name}</strong>. ⚠️
    </p>
    <table style="border-collapse:collapse; margin:16px 0; width:100%;">
      <tr>
        <td style="padding:8px 12px; background:#f9fafb; border:1px solid #e5e7eb;
                   color:#6b7280; font-size:14px;">Limite do plano</td>
        <td style="padding:8px 12px; background:#f9fafb; border:1px solid #e5e7eb;
                   font-weight:600;">{limit} {type_label}</td>
      </tr>
      <tr>
        <td style="padding:8px 12px; border:1px solid #e5e7eb;
                   color:#6b7280; font-size:14px;">Uso atual</td>
        <td style="padding:8px 12px; border:1px solid #e5e7eb;
                   font-weight:600; color:#ef4444;">{current} {type_label}</td>
      </tr>
    </table>
    <p>Para continuar crescendo, considere fazer upgrade do seu plano.</p>
    """
    html = _wrap_html(
        title=f"Limite de {type_label} atingido",
        body_html=body,
        action_url=f"{_public_url()}/#/settings?tab=Assinaturas",
        action_label="Ver planos disponíveis",
    )
    msg = _build_message(
        to_email=to_email,
        subject=f"Blackchat Pro — você atingiu o limite de {type_label}",
        html_body=html,
    )
    try:
        await _send(msg)
    except Exception:
        logger.exception("Falha ao enviar e-mail de limite para %s", to_email)


def send_plan_limit_reached_email_background(
    *,
    to_email: str,
    full_name: Optional[str] = None,
    limit_type: str = "",
    current: int = 0,
    limit: int = 0,
    plan_name: str = "",
) -> None:
    _run_async(send_plan_limit_reached_email(
        to_email=to_email, full_name=full_name,
        limit_type=limit_type, current=current, limit=limit, plan_name=plan_name,
    ))


# ─── 5. Assinatura cancelada ──────────────────────────────────────────────────

async def send_subscription_canceled_email(
    *,
    to_email: str,
    full_name: Optional[str] = None,
    plan_name: str = "",
) -> None:
    display = (full_name or "").strip() or to_email

    body = f"""
    <p>Olá, <strong>{display}</strong>.</p>
    <p>
      Confirmamos o cancelamento da sua assinatura do plano
      <strong>{plan_name}</strong>.
    </p>
    <p>
      Sua conta foi movida para o plano <strong>Free</strong>.
      Seus dados foram preservados e você pode reativar a qualquer momento.
    </p>
    <p>
      Se tiver algum feedback sobre o motivo do cancelamento,
      adoraríamos ouvir — basta responder este e-mail.
    </p>
    """
    html = _wrap_html(
        title="Assinatura cancelada",
        body_html=body,
        action_url=f"{_public_url()}/#/settings?tab=Assinaturas",
        action_label="Reativar assinatura",
    )
    msg = _build_message(
        to_email=to_email,
        subject="Blackchat Pro — sua assinatura foi cancelada",
        html_body=html,
    )
    try:
        await _send(msg)
    except Exception:
        logger.exception("Falha ao enviar e-mail de cancelamento para %s", to_email)


def send_subscription_canceled_email_background(
    *,
    to_email: str,
    full_name: Optional[str] = None,
    plan_name: str = "",
) -> None:
    _run_async(send_subscription_canceled_email(
        to_email=to_email, full_name=full_name, plan_name=plan_name
    ))


# ─── 6. Recuperação de senha ──────────────────────────────────────────────────

async def send_password_reset_email(
    *,
    to_email: str,
    full_name: Optional[str] = None,
    reset_url: str,
) -> None:
    display = (full_name or "").strip() or to_email

    body = f"""
    <p>Olá, <strong>{display}</strong>!</p>
    <p>Recebemos uma solicitação de redefinição de senha para sua conta.</p>
    <p>
      Clique no botão abaixo para criar uma nova senha.
      O link é válido por <strong>1 hora</strong>.
    </p>
    <p style="margin-top:16px; color:#6b7280; font-size:13px;">
      Se você não solicitou a redefinição de senha, ignore este e-mail
      — sua senha não será alterada.
    </p>
    """
    html = _wrap_html(
        title="Redefinição de senha",
        body_html=body,
        action_url=reset_url,
        action_label="Redefinir senha",
    )
    msg = _build_message(
        to_email=to_email,
        subject="Blackchat Pro — redefinição de senha",
        html_body=html,
    )
    try:
        await _send(msg)
    except Exception:
        logger.exception("Falha ao enviar e-mail de redefinição para %s", to_email)


def send_password_reset_email_background(
    *,
    to_email: str,
    full_name: Optional[str] = None,
    reset_url: str,
) -> None:
    _run_async(send_password_reset_email(
        to_email=to_email, full_name=full_name, reset_url=reset_url
    ))

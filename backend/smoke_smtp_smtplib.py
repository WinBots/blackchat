from __future__ import annotations

import argparse
import os
import smtplib
from datetime import datetime
from email.message import EmailMessage
from pathlib import Path

from dotenv import dotenv_values


def _mask_email(value: str | None) -> str:
    if not value:
        return ""
    if "@" in value:
        name, domain = value.split("@", 1)
        if len(name) > 2:
            return name[:2] + "***@" + domain
        return "***@" + domain
    return (value[:2] + "***") if len(value) > 2 else "***"


def _parse_bool(value: str | None, default: bool) -> bool:
    if value is None:
        return default
    v = value.strip().lower()
    if v in {"1", "true", "t", "yes", "y", "on"}:
        return True
    if v in {"0", "false", "f", "no", "n", "off"}:
        return False
    return default


def _load_env() -> dict[str, str]:
    env_path = Path(__file__).resolve().parent / ".env"
    raw = dotenv_values(env_path)
    return {str(k): str(v) for k, v in raw.items() if k and v is not None}


def main() -> int:
    os.chdir(Path(__file__).resolve().parent)

    parser = argparse.ArgumentParser(description="SMTP smoke test using smtplib + backend/.env")
    parser.add_argument("--to", default="windson3433@gmail.com")
    parser.add_argument("--subject", default="Blackchat Pro — SMTP smoke test (smtplib)")
    parser.add_argument("--debug", action="store_true", help="Enable smtplib debug output")
    parser.add_argument("--ssl", action="store_true", help="Use SMTP over SSL (465)")
    parser.add_argument("--port", type=int, default=None)
    args = parser.parse_args()

    env = _load_env()

    enabled = _parse_bool(env.get("SMTP_ENABLED"), True)
    if not enabled:
        print("SMTP TEST (smtplib): FAILED: SMTP_ENABLED=false")
        return 1

    host = (env.get("SMTP_HOST") or "").strip() or "smtp.titan.email"
    user = (env.get("SMTP_USER") or "").strip()
    password = env.get("SMTP_PASSWORD") or ""
    from_email = (env.get("SMTP_FROM_EMAIL") or user).strip()
    from_name = (env.get("SMTP_FROM_NAME") or "Blackchat Pro").strip() or "Blackchat Pro"

    use_ssl = bool(args.ssl)
    port = args.port if args.port is not None else (465 if use_ssl else int((env.get("SMTP_PORT") or "587").strip() or 587))
    use_starttls = _parse_bool(env.get("SMTP_USE_TLS"), True) if not use_ssl else False

    missing = [k for k, v in {"SMTP_HOST": host, "SMTP_USER": user, "SMTP_PASSWORD": password, "SMTP_FROM_EMAIL": from_email}.items() if not v]
    if missing:
        print("SMTP TEST (smtplib): FAILED: faltando no .env:", ", ".join(missing))
        return 1

    print(
        "SMTP TEST (smtplib): config efetiva -> "
        f"host={host} port={port} ssl={use_ssl} starttls={use_starttls} "
        f"user={_mask_email(user)} from={_mask_email(from_email)}"
    )

    msg = EmailMessage()
    msg["From"] = f"{from_name} <{from_email}>"
    msg["To"] = args.to
    msg["Subject"] = args.subject
    msg.set_content(
        "Blackchat Pro — SMTP smoke test (smtplib)\n\n"
        f"Data/Hora: {datetime.now().isoformat()}\n"
        f"Servidor: {host}:{port}\n"
        "\nSe você recebeu este e-mail, o SMTP está funcionando."
    )

    try:
        if use_ssl:
            server: smtplib.SMTP = smtplib.SMTP_SSL(host, port, timeout=30)
        else:
            server = smtplib.SMTP(host, port, timeout=30)

        with server as smtp:
            if args.debug:
                smtp.set_debuglevel(1)
            smtp.ehlo()
            if use_starttls:
                smtp.starttls()
                smtp.ehlo()
            smtp.login(user, password)
            smtp.send_message(msg)
    except smtplib.SMTPAuthenticationError as exc:
        print(f"SMTP TEST (smtplib): FAILED: auth failed: {exc}")
        return 1
    except Exception as exc:
        print(f"SMTP TEST (smtplib): FAILED: {exc}")
        return 1

    print("SMTP TEST (smtplib): OK (email enviado)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

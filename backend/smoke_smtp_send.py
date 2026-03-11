from __future__ import annotations

import argparse
import asyncio
import getpass
import logging
import os
import sys
from datetime import datetime, timezone
from email.message import EmailMessage
from pathlib import Path

import aiosmtplib
from dotenv import dotenv_values

from app.config import get_settings


def _build_message(*, to_email: str, subject: str, text: str) -> EmailMessage:
    settings = get_settings()

    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = (
        f"{settings.SMTP_FROM_NAME} <{settings.SMTP_FROM_EMAIL}>"
        if settings.SMTP_FROM_EMAIL
        else settings.SMTP_FROM_NAME
    )
    msg["To"] = to_email
    msg.set_content(text)
    return msg


def _mask_email(value: str | None) -> str:
    if not value:
        return ""
    if "@" in value:
        name, domain = value.split("@", 1)
        if len(name) > 2:
            return name[:2] + "***@" + domain
        return "***@" + domain
    return (value[:2] + "***") if len(value) > 2 else "***"


def _print_masked_config(*, smtp_user: str, smtp_from_email: str) -> None:
    settings = get_settings()
    print(
        "SMTP TEST: usando config do .env -> "
        f"host={settings.SMTP_HOST} port={settings.SMTP_PORT} "
        f"starttls={settings.SMTP_USE_TLS} ssl={settings.SMTP_USE_SSL} "
        f"user={_mask_email(smtp_user)} from={_mask_email(smtp_from_email)}"
    )


def _parse_bool(value: str | None, default: bool) -> bool:
    if value is None:
        return default
    v = value.strip().lower()
    if v in {"1", "true", "t", "yes", "y", "on"}:
        return True
    if v in {"0", "false", "f", "no", "n", "off"}:
        return False
    return default


def _load_env_file() -> dict[str, str]:
    env_path = Path(__file__).resolve().parent / ".env"
    values = dotenv_values(env_path)
    out: dict[str, str] = {}
    for key, value in values.items():
        if key and value is not None:
            out[str(key)] = str(value)
    return out


def _effective_smtp_config(
    *,
    override_user: str | None,
    override_password: str | None,
    override_host: str | None,
    override_port: int | None,
    override_ssl: bool | None,
    override_starttls: bool | None,
) -> dict[str, object]:
    env = _load_env_file()

    host = (override_host or env.get("SMTP_HOST") or "").strip()
    port = override_port if override_port is not None else int((env.get("SMTP_PORT") or "587").strip() or 587)
    use_ssl = override_ssl if override_ssl is not None else _parse_bool(env.get("SMTP_USE_SSL"), False)
    use_starttls = override_starttls if override_starttls is not None else _parse_bool(env.get("SMTP_USE_TLS"), True)
    enabled = _parse_bool(env.get("SMTP_ENABLED"), True)

    user = (override_user or env.get("SMTP_USER") or "").strip()
    password = override_password if override_password is not None else (env.get("SMTP_PASSWORD") or "")

    from_email = (env.get("SMTP_FROM_EMAIL") or "").strip()
    from_name = (env.get("SMTP_FROM_NAME") or "Blackchat Pro").strip() or "Blackchat Pro"

    return {
        "enabled": enabled,
        "host": host,
        "port": port,
        "use_ssl": use_ssl,
        "use_starttls": use_starttls,
        "user": user,
        "password": password,
        "from_email": from_email,
        "from_name": from_name,
    }


async def _send(*, to_email: str, subject: str, smtp: dict[str, object]) -> None:
    missing = [
        key
        for key, value in {
            "SMTP_HOST": smtp.get("host"),
            "SMTP_USER": smtp.get("user"),
            "SMTP_PASSWORD": smtp.get("password"),
            "SMTP_FROM_EMAIL": smtp.get("from_email"),
        }.items()
        if not value
    ]
    if missing:
        raise RuntimeError(
            "SMTP não está completamente configurado no .env (faltando: "
            + ", ".join(missing)
            + ")"
        )

    if not bool(smtp.get("enabled")):
        raise RuntimeError("SMTP_ENABLED=false no .env; envio está desativado")

    print(
        "SMTP TEST: config efetiva -> "
        f"host={smtp['host']} port={smtp['port']} starttls={smtp['use_starttls']} ssl={smtp['use_ssl']} "
        f"user={_mask_email(str(smtp['user']))} from={_mask_email(str(smtp['from_email']))}"
    )

    now = datetime.now(timezone.utc).astimezone()
    text = (
        "Blackchat Pro — SMTP smoke test\n\n"
        f"Data/Hora: {now.isoformat()}\n"
        f"Host: {settings.SMTP_HOST}:{settings.SMTP_PORT}\n"
        f"STARTTLS: {settings.SMTP_USE_TLS}\n"
        f"SSL: {settings.SMTP_USE_SSL}\n"
        "\nSe você recebeu este e-mail, o SMTP está funcionando."
    )
    msg = _build_message(to_email=to_email, subject=subject, text=text)

    client = aiosmtplib.SMTP(
        hostname=str(smtp["host"]),
        port=int(smtp["port"]),
        timeout=20,
        use_tls=bool(smtp["use_ssl"]),
        start_tls=bool(smtp["use_starttls"]),
    )

    auth_mode = str(smtp.get("auth") or "auto").lower()
    try:
        await client.connect()

        if smtp.get("debug"):
            try:
                await client.ehlo()
            except Exception as exc:
                print("SMTP DEBUG: EHLO failed:", exc)
            print("SMTP DEBUG: last_ehlo_response:", getattr(client, "last_ehlo_response", None))
            print("SMTP DEBUG: esmtp_extensions:", getattr(client, "esmtp_extensions", None))
            print("SMTP DEBUG: server_auth_methods:", getattr(client, "server_auth_methods", None))

        if auth_mode == "plain":
            await client.auth_plain(str(smtp["user"]), str(smtp["password"]))
        elif auth_mode == "login":
            await client.auth_login(str(smtp["user"]), str(smtp["password"]))
        else:
            await client.login(str(smtp["user"]), str(smtp["password"]))

        await client.send_message(msg)
    finally:
        try:
            await client.quit()
        except Exception:
            pass


async def _check_only(*, smtp: dict[str, object]) -> None:
    missing = [
        key
        for key, value in {
            "SMTP_HOST": smtp.get("host"),
            "SMTP_USER": smtp.get("user"),
            "SMTP_PASSWORD": smtp.get("password"),
        }.items()
        if not value
    ]
    if missing:
        raise RuntimeError(
            "SMTP não está completamente configurado no .env (faltando: "
            + ", ".join(missing)
            + ")"
        )

    if not bool(smtp.get("enabled")):
        raise RuntimeError("SMTP_ENABLED=false no .env; envio está desativado")

    print(
        "SMTP TEST: config efetiva -> "
        f"host={smtp['host']} port={smtp['port']} starttls={smtp['use_starttls']} ssl={smtp['use_ssl']} "
        f"user={_mask_email(str(smtp['user']))} from={_mask_email(str(smtp['from_email']))}"
    )

    client = aiosmtplib.SMTP(
        hostname=str(smtp["host"]),
        port=int(smtp["port"]),
        timeout=20,
        use_tls=bool(smtp["use_ssl"]),
        start_tls=bool(smtp["use_starttls"]),
    )

    auth_mode = str(smtp.get("auth") or "auto").lower()

    try:
        try:
            await client.connect()
        except Exception as exc:
            raise RuntimeError(f"Falha ao conectar em {smtp['host']}:{smtp['port']}: {exc}") from exc

        if smtp.get("debug"):
            try:
                await client.ehlo()
            except Exception as exc:
                print("SMTP DEBUG: EHLO failed:", exc)

            print("SMTP DEBUG: supports_esmtp:", getattr(client, "supports_esmtp", None))
            print("SMTP DEBUG: last_ehlo_response:", getattr(client, "last_ehlo_response", None))
            print("SMTP DEBUG: esmtp_extensions:", getattr(client, "esmtp_extensions", None))
            print("SMTP DEBUG: server_auth_methods:", getattr(client, "server_auth_methods", None))
            print("SMTP DEBUG: supported_auth_methods:", getattr(client, "supported_auth_methods", None))

        try:
            if auth_mode == "plain":
                await client.auth_plain(str(smtp["user"]), str(smtp["password"]))
            elif auth_mode == "login":
                await client.auth_login(str(smtp["user"]), str(smtp["password"]))
            else:
                await client.login(str(smtp["user"]), str(smtp["password"]))
        except Exception as exc:
            raise RuntimeError(f"Falha ao autenticar (SMTP_USER/SMTP_PASSWORD): {exc}") from exc
    finally:
        try:
            await client.quit()
        except Exception:
            pass


def main() -> int:
    os.chdir(Path(__file__).resolve().parent)

    parser = argparse.ArgumentParser(description="Send a test email using backend/.env SMTP settings")
    parser.add_argument("--to", default="windson3433@gmail.com", help="Destination email")
    parser.add_argument(
        "--subject",
        default="Blackchat Pro — SMTP smoke test",
        help="Email subject",
    )
    parser.add_argument(
        "--check-only",
        action="store_true",
        help="Only connect and authenticate; do not send an email",
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable SMTP debug logging and print server capabilities",
    )
    parser.add_argument(
        "--auth",
        choices=["auto", "plain", "login"],
        default="auto",
        help="Force an AUTH mechanism (default: auto)",
    )
    parser.add_argument(
        "--user",
        default=None,
        help="Override SMTP_USER (default: from .env)",
    )
    parser.add_argument(
        "--password",
        default=None,
        help="Override SMTP_PASSWORD (NOT recommended; prefer --prompt-password)",
    )
    parser.add_argument(
        "--prompt-password",
        action="store_true",
        help="Prompt for SMTP password (overrides .env and --password)",
    )
    parser.add_argument(
        "--host",
        default=None,
        help="Override SMTP_HOST (default: from .env)",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=None,
        help="Override SMTP_PORT (default: from .env)",
    )
    parser.add_argument(
        "--ssl",
        action="store_true",
        help="Force SSL (SMTPS, usually port 465)",
    )
    parser.add_argument(
        "--no-ssl",
        action="store_true",
        help="Disable SSL",
    )
    parser.add_argument(
        "--starttls",
        action="store_true",
        help="Force STARTTLS (usually port 587)",
    )
    parser.add_argument(
        "--no-starttls",
        action="store_true",
        help="Disable STARTTLS",
    )
    args = parser.parse_args()

    smtp_password = None
    if args.prompt_password:
        smtp_password = getpass.getpass("SMTP password: ")
    elif args.password is not None:
        smtp_password = args.password

    override_ssl = None
    if args.ssl and args.no_ssl:
        print("SMTP TEST: FAILED: não use --ssl e --no-ssl juntos")
        return 2
    if args.ssl:
        override_ssl = True
    elif args.no_ssl:
        override_ssl = False

    override_starttls = None
    if args.starttls and args.no_starttls:
        print("SMTP TEST: FAILED: não use --starttls e --no-starttls juntos")
        return 2
    if args.starttls:
        override_starttls = True
    elif args.no_starttls:
        override_starttls = False

    smtp = _effective_smtp_config(
        override_user=args.user,
        override_password=smtp_password,
        override_host=args.host,
        override_port=args.port,
        override_ssl=override_ssl,
        override_starttls=override_starttls,
    )
    smtp["debug"] = bool(args.debug)
    smtp["auth"] = args.auth

    if args.debug:
        logging.basicConfig(level=logging.DEBUG)
        logging.getLogger("aiosmtplib").setLevel(logging.DEBUG)
        logging.getLogger("aiosmtplib.smtp").setLevel(logging.DEBUG)

    try:
        if args.check_only:
            asyncio.run(_check_only(smtp=smtp))
        else:
            asyncio.run(_send(to_email=args.to, subject=args.subject, smtp=smtp))
    except Exception as exc:
        print(f"SMTP TEST: FAILED: {exc}")
        return 1

    print("SMTP TEST: OK" + (" (auth ok)" if args.check_only else " (email enviado)"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

from __future__ import annotations

import argparse
import imaplib
import os
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


def _load_env() -> dict[str, str]:
    env_path = Path(__file__).resolve().parent / ".env"
    raw = dotenv_values(env_path)
    return {str(k): str(v) for k, v in raw.items() if k and v is not None}


def main() -> int:
    os.chdir(Path(__file__).resolve().parent)

    parser = argparse.ArgumentParser(description="IMAP smoke test for Titan using backend/.env")
    parser.add_argument("--host", default="imap.titan.email")
    parser.add_argument("--port", type=int, default=993)
    args = parser.parse_args()

    env = _load_env()
    user = (env.get("SMTP_USER") or "").strip()
    password = env.get("SMTP_PASSWORD") or ""

    if not user or not password:
        print("IMAP TEST: FAILED: faltando SMTP_USER/SMTP_PASSWORD no backend/.env")
        return 1

    print(f"IMAP TEST: tentando login -> host={args.host} port={args.port} user={_mask_email(user)}")

    try:
        imap = imaplib.IMAP4_SSL(args.host, args.port)
        try:
            imap.login(user, password)
            typ, _data = imap.list()
            print("IMAP TEST: OK (login ok)")
            if typ:
                print("IMAP TEST: list status:", typ)
        finally:
            try:
                imap.logout()
            except Exception:
                pass
    except imaplib.IMAP4.error as exc:
        print(f"IMAP TEST: FAILED: auth failed or protocol error: {exc}")
        return 1
    except Exception as exc:
        print(f"IMAP TEST: FAILED: {exc}")
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

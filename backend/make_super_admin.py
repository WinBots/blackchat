"""Dev utility: promote a user to super admin.

Usage:
  python make_super_admin.py admin@blackchatpro.com

This edits the configured database in app.config (sqlite data/app.db by default).
"""

from __future__ import annotations

import sys

from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.db.models.user import User


def main() -> int:
    if len(sys.argv) < 2:
        print("Usage: python make_super_admin.py <email>")
        return 2

    email = sys.argv[1].strip().lower()
    if not email:
        print("Email is required")
        return 2

    db: Session = SessionLocal()
    try:
        user = db.query(User).filter(User.email == email).first()
        if not user:
            print("User not found")
            return 1

        setattr(user, "is_super_admin", True)
        db.commit()
        print(f"OK: {user.email} is_super_admin={getattr(user, 'is_super_admin', None)}")
        return 0
    finally:
        db.close()


if __name__ == "__main__":
    raise SystemExit(main())

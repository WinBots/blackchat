from __future__ import annotations

import httpx


def main() -> None:
    base = "http://127.0.0.1:8061"
    login = httpx.post(
        f"{base}/api/v1/auth/login",
        json={"email": "admin@blackchatpro.com", "password": "admin123"},
        timeout=15,
    )
    login.raise_for_status()
    j = login.json()

    print("is_super_admin", j.get("user", {}).get("is_super_admin"))

    token = j["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    for path in ("/api/v1/admin/tenants", "/api/v1/admin/users", "/api/v1/admin/plans"):
        resp = httpx.get(f"{base}{path}", headers=headers, timeout=15)
        print(path, resp.status_code)
        try:
            data = resp.json()
            if isinstance(data, list):
                print("items", len(data))
                if data:
                    print("first_keys", list(data[0].keys()))
            else:
                print("type", type(data))
        except Exception:
            print(resp.text[:200])


if __name__ == "__main__":
    main()

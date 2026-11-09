#!/usr/bin/env python3
"""
Stremio Authentication Helper
Allows logging in with email/password or setting a manual authKey token.
Saves credentials to ~/.stremio-mcp
"""

import os
import sys
import json
import getpass
import argparse
import urllib.request
import urllib.error

CONFIG_PATH = os.path.expanduser("~/.stremio-mcp")
LOGIN_URL = "https://api.strem.io/api/login"

HEADERS = {
    "Content-Type": "application/json",
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}


def save_config(auth_key: str, email: str = ""):
    data = {
        "auth_key": auth_key,
        "email": email
    }
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)
    print(f"✅ Credenziali Stremio salvate con successo in: {CONFIG_PATH}")


def login_with_credentials(email: str, password: str):
    payload = {
        "email": email,
        "password": password
    }
    req = urllib.request.Request(LOGIN_URL, data=json.dumps(payload).encode("utf-8"), headers=HEADERS)
    try:
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            result = data.get("result", {})
            auth_key = result.get("authKey")
            if not auth_key:
                print(f"❌ Errore durante il login: {data}")
                sys.exit(1)
            save_config(auth_key, email)
    except urllib.error.HTTPError as e:
        print(f"❌ Errore HTTP {e.code}: {e.read().decode('utf-8')}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Errore di connessione: {e}")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="Autenticazione Stremio")
    parser.add_argument("--token", help="Salva direttamente l'authKey esistente (es. da web.stremio.com)")
    parser.add_argument("--email", help="Email dell'account Stremio")
    parser.add_argument("--password", help="Password dell'account Stremio")
    args = parser.parse_args()

    if args.token:
        save_config(args.token, args.email or "")
        return

    email = args.email or input("Inserisci l'email di Stremio: ").strip()
    password = args.password or getpass.getpass("Inserisci la password di Stremio: ")

    if not email or not password:
        print("❌ Email e password sono obbligatorie.")
        sys.exit(1)

    login_with_credentials(email, password)


if __name__ == "__main__":
    main()

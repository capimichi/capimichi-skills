#!/usr/bin/env python3
"""
Nuvio Authentication Helper
Allows logging in with email/password, custom server base URL, or saving existing tokens.
Saves credentials to ~/.nuvio-mcp
"""

import os
import sys
import json
import getpass
import argparse
import urllib.request
import urllib.error

CONFIG_PATH = os.path.expanduser("~/.nuvio-mcp")
DEFAULT_BASE_URL = "https://api.nuvio.tv"

HEADERS = {
    "Content-Type": "application/json",
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}


def save_config(base_url: str, api_key: str, access_token: str, refresh_token: str = "", email: str = "", profile_id: int = 0):
    data = {
        "base_url": base_url.rstrip("/"),
        "api_key": api_key,
        "access_token": access_token,
        "refresh_token": refresh_token,
        "email": email,
        "profile_id": profile_id
    }
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)
    print(f"✅ Credenziali Nuvio salvate con successo in: {CONFIG_PATH}")


def login_with_password(base_url: str, api_key: str, email: str, password: str, profile_id: int = 0):
    url = f"{base_url.rstrip('/')}/auth/v1/token?grant_type=password"
    payload = {
        "email": email,
        "password": password
    }
    headers = dict(HEADERS)
    if api_key:
        headers["apikey"] = api_key

    req = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"), headers=headers)
    try:
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            access_token = data.get("access_token")
            refresh_token = data.get("refresh_token", "")
            if not access_token:
                print(f"❌ Token non trovato nella risposta: {data}")
                sys.exit(1)
            save_config(base_url, api_key, access_token, refresh_token, email, profile_id)
    except urllib.error.HTTPError as e:
        print(f"❌ Errore HTTP {e.code}: {e.read().decode('utf-8')}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Errore di connessione: {e}")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="Autenticazione Nuvio")
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL, help="URL base API Nuvio (default: https://api.nuvio.tv)")
    parser.add_argument("--api-key", default="", help="Chiave publishable/anon di Supabase (se richiesta)")
    parser.add_argument("--token", help="Salva direttamente l'access_token esistente")
    parser.add_argument("--refresh-token", default="", help="Refresh token (se disponibile)")
    parser.add_argument("--email", help="Email dell'account Nuvio")
    parser.add_argument("--password", help="Password dell'account Nuvio")
    parser.add_argument("--profile-id", type=int, default=0, help="ID Profilo (default: 0)")
    args = parser.parse_args()

    if args.token:
        save_config(args.base_url, args.api_key, args.token, args.refresh_token, args.email or "", args.profile_id)
        return

    email = args.email or input("Inserisci l'email di Nuvio: ").strip()
    password = args.password or getpass.getpass("Inserisci la password di Nuvio: ")

    if not email or not password:
        print("❌ Email e password sono obbligatorie.")
        sys.exit(1)

    login_with_password(args.base_url, args.api_key, email, password, args.profile_id)


if __name__ == "__main__":
    main()

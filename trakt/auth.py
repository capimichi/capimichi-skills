#!/usr/bin/env python3
"""
Trakt OAuth Authentication Script (PIN Code & Localhost support)
"""

import os
import sys
import json
import argparse
import urllib.request
import urllib.parse

CREDENTIALS_FILE = os.path.expanduser("~/.trakt-mcp")
CLIENT_ID = "AuiiHzPF9DJxb9dBK9caSzaAUI2qOb-hFzglEZ2SAG0"
CLIENT_SECRET = "4h-B4Jk0Xz-Meyt9QKMSRMqmiRnPyS5xmRDN3VZrzjY"
REDIRECT_URI = "urn:ietf:wg:oauth:2.0:oob"


def exchange_code_for_token(code: str, redirect_uri: str = REDIRECT_URI) -> bool:
    token_data = {
        "code": code.strip(),
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "redirect_uri": redirect_uri,
        "grant_type": "authorization_code"
    }

    headers = {
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
    }

    req = urllib.request.Request("https://api.trakt.tv/oauth/token", data=json.dumps(token_data).encode("utf-8"), headers=headers)
    try:
        with urllib.request.urlopen(req) as response:
            token_res = json.loads(response.read().decode("utf-8"))
            save_data = {
                "client_id": CLIENT_ID,
                "client_secret": CLIENT_SECRET,
                "access_token": token_res["access_token"],
                "refresh_token": token_res["refresh_token"]
            }
            with open(CREDENTIALS_FILE, 'w', encoding="utf-8") as f:
                json.dump(save_data, f, indent=4)
            print(f"\n✅ Autenticazione riuscita! Credenziali salvate in: {CREDENTIALS_FILE}")
            return True
    except urllib.error.HTTPError as e:
        print(f"❌ Errore HTTP {e.code}: {e.read().decode('utf-8')}")
        return False
    except Exception as e:
        print(f"❌ Errore nello scambio del token: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(description="Autenticazione Trakt API")
    parser.add_argument("--pin", help="Codice PIN / Authorization Code fornito da Trakt")
    args = parser.parse_args()

    if args.pin:
        exchange_code_for_token(args.pin)
        return

    auth_url = f"https://trakt.tv/oauth/authorize?response_type=code&client_id={CLIENT_ID}&redirect_uri={urllib.parse.quote(REDIRECT_URI, safe='')}"
    print("=" * 70)
    print("🔑 AUTENTICAZIONE TRAKT.TV (PIN CODE)")
    print("=" * 70)
    print(f"\n1. Apri questo link nel browser:\n\n   {auth_url}\n")
    print("2. Clicca su 'Authorize' / 'Approva'.")
    print("3. Copia il codice PIN mostrato a schermo.\n")

    pin = input("Incolla qui il codice PIN: ").strip()
    if pin:
        exchange_code_for_token(pin)
    else:
        print("❌ Nessun codice inserito.")


if __name__ == "__main__":
    main()

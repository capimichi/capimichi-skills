#!/usr/bin/env python3
"""
Sync credentials from Bitwarden CLI (bw) for Stremio and Nuvio.
Searches Bitwarden for 'stremio' and 'nuvio' vault items, performs API authentication,
and automatically creates ~/.stremio-mcp and ~/.nuvio-mcp.
"""

import os
import sys
import json
import subprocess
import urllib.request
import urllib.error

HEADERS = {
    "Content-Type": "application/json",
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}


def run_bw_command(args: list) -> str:
    session = os.environ.get("BW_SESSION")
    cmd = ["bw"] + args
    if session and "--session" not in args:
        cmd.extend(["--session", session])

    try:
        res = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return res.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"❌ Errore Bitwarden CLI: {e.stderr.strip() or e.stdout.strip()}")
        return ""
    except FileNotFoundError:
        print("❌ Bitwarden CLI ('bw') non trovata nel PATH.")
        return ""


def find_item_in_vault(search_term: str) -> dict:
    output = run_bw_command(["list", "items", "--search", search_term])
    if not output:
        return {}
    try:
        items = json.loads(output)
        if isinstance(items, list) and items:
            # Ritorna il primo match rilevante
            for it in items:
                name = it.get("name", "").lower()
                if search_term.lower() in name:
                    return it
            return items[0]
    except Exception as e:
        print(f"❌ Errore parsing output BW per '{search_term}': {e}")
    return {}


def setup_stremio(bw_item: dict):
    print("\n📦 Configurazione Stremio...")
    login_info = bw_item.get("login", {})
    username = login_info.get("username", "")
    password = login_info.get("password", "")

    # Controlla se c'è un custom field "authKey" o simile
    fields = {f.get("name", "").lower(): f.get("value", "") for f in bw_item.get("fields", []) if isinstance(f, dict)}
    custom_auth_key = fields.get("authkey") or fields.get("auth_key") or fields.get("token")

    auth_key = None
    if custom_auth_key:
        print("  🔑 Trovato authKey nei campi personalizzati di Bitwarden.")
        auth_key = custom_auth_key
    elif username and password:
        print(f"  🔐 Tentativo di login a Stremio con utente: {username}...")
        req_payload = {"email": username, "password": password}
        req = urllib.request.Request("https://api.strem.io/api/login", data=json.dumps(req_payload).encode("utf-8"), headers=HEADERS)
        try:
            with urllib.request.urlopen(req) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                auth_key = data.get("result", {}).get("authKey")
        except urllib.error.HTTPError as e:
            print(f"  ❌ Errore login Stremio ({e.code}): {e.read().decode('utf-8')}")
        except Exception as e:
            print(f"  ❌ Errore connessione Stremio: {e}")

    if auth_key:
        dest_path = os.path.expanduser("~/.stremio-mcp")
        config_data = {
            "email": username,
            "auth_key": auth_key
        }
        with open(dest_path, "w", encoding="utf-8") as f:
            json.dump(config_data, f, indent=4)
        print(f"  ✅ File creato con successo: {dest_path}")
    else:
        print("  ⚠️ Impossibile generare ~/.stremio-mcp (credenziali non valide o authKey mancante).")


def setup_nuvio(bw_item: dict):
    print("\n📦 Configurazione Nuvio...")
    login_info = bw_item.get("login", {})
    username = login_info.get("username", "")
    password = login_info.get("password", "")

    fields = {f.get("name", "").lower(): f.get("value", "") for f in bw_item.get("fields", []) if isinstance(f, dict)}
    base_url = fields.get("base_url") or fields.get("url") or "https://api.nuvio.tv"
    api_key = fields.get("api_key") or fields.get("apikey") or fields.get("anon_key") or ""
    custom_access_token = fields.get("access_token") or fields.get("token")
    custom_refresh_token = fields.get("refresh_token") or ""

    access_token = custom_access_token
    refresh_token = custom_refresh_token

    if not access_token and username and password:
        print(f"  🔐 Tentativo di login a Nuvio con utente: {username}...")
        url = f"{base_url.rstrip('/')}/auth/v1/token?grant_type=password"
        headers = dict(HEADERS)
        if api_key:
            headers["apikey"] = api_key
        req_payload = {"email": username, "password": password}
        req = urllib.request.Request(url, data=json.dumps(req_payload).encode("utf-8"), headers=headers)
        try:
            with urllib.request.urlopen(req) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                access_token = data.get("access_token")
                refresh_token = data.get("refresh_token", "")
        except urllib.error.HTTPError as e:
            print(f"  ❌ Errore login Nuvio ({e.code}): {e.read().decode('utf-8')}")
        except Exception as e:
            print(f"  ❌ Errore connessione Nuvio: {e}")

    if access_token or (username and password):
        dest_path = os.path.expanduser("~/.nuvio-mcp")
        config_data = {
            "base_url": base_url,
            "api_key": api_key,
            "access_token": access_token or "",
            "refresh_token": refresh_token or "",
            "email": username,
            "profile_id": int(fields.get("profile_id", 0))
        }
        with open(dest_path, "w", encoding="utf-8") as f:
            json.dump(config_data, f, indent=4)
        print(f"  ✅ File creato con successo: {dest_path}")
    else:
        print("  ⚠️ Impossibile generare ~/.nuvio-mcp (credenziali non trovate).")


def setup_paperless(bw_item: dict):
    print("\n📦 Configurazione Paperless-ngx...")
    fields = {f.get("name", "").lower(): f.get("value", "") for f in bw_item.get("fields", []) if isinstance(f, dict)}
    base_url = fields.get("base_url") or fields.get("url") or "https://paperless.michelecapicchioni.com"
    api_key = fields.get("api_key") or fields.get("token") or fields.get("api_token") or ""

    if not api_key:
        login_info = bw_item.get("login", {})
        api_key = login_info.get("password", "")

    if base_url and api_key:
        print(f"  🔑 Trovato Paperless base_url: {base_url}")
        print("  ✅ Credenziali configurate nelle variabili d'ambiente (.config/zsh/envs/personal.zsh).")
        print("     Variabili esportate: PAPERLESS_BASE_URL, PAPERLESS_API_KEY, PAPERLESS_URL, PAPERLESS_TOKEN")
    else:
        print("  ⚠️ Credenziali Paperless non complete nell'item Bitwarden.")


def main():
    print("🔍 Verifica stato sessione Bitwarden...")
    status_out = run_bw_command(["status"])
    if not status_out:
        print("💡 Per sbloccare Bitwarden esegui:\n   export BW_SESSION=$(bw unlock --raw)")
        sys.exit(1)

    try:
        st = json.loads(status_out)
        if st.get("status") != "unlocked":
            print(f"⚠️ Bitwarden risulta nello stato: '{st.get('status')}'.")
            print("💡 Esegui nel terminale:\n   export BW_SESSION=$(bw unlock --raw)\ne poi rilancia questo script.")
            sys.exit(1)
    except Exception:
        pass

    print("✅ Vault Bitwarden sbloccato. Ricerca elementi in corso...")

    # Stremio
    stremio_item = find_item_in_vault("stremio")
    if stremio_item:
        setup_stremio(stremio_item)
    else:
        print("\n⚠️ Nessun elemento trovato in Bitwarden con nome 'stremio'.")

    # Nuvio
    nuvio_item = find_item_in_vault("nuvio")
    if nuvio_item:
        setup_nuvio(nuvio_item)
    else:
        print("\n⚠️ Nessun elemento trovato in Bitwarden con nome 'nuvio'.")

    # Paperless-ngx
    paperless_item = find_item_in_vault("paperless.michelecapicchioni.com capimichi") or find_item_in_vault("paperless")
    if paperless_item:
        setup_paperless(paperless_item)
    else:
        print("\n⚠️ Nessun elemento trovato in Bitwarden per 'paperless.michelecapicchioni.com capimichi'.")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Trakt API Client Helper.
"""

import os
import sys
import json
import urllib.request
import urllib.parse
import urllib.error
from datetime import datetime, timezone

HEADERS = {
    "Content-Type": "application/json",
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

CLIENT_ID_DEFAULT = "AuiiHzPF9DJxb9dBK9caSzaAUI2qOb-hFzglEZ2SAG0"
CLIENT_SECRET_DEFAULT = "4h-B4Jk0Xz-Meyt9QKMSRMqmiRnPyS5xmRDN3VZrzjY"
REDIRECT_URI = "urn:ietf:wg:oauth:2.0:oob"


def load_trakt_config() -> dict:
    token = os.environ.get("TRAKT_ACCESS_TOKEN")
    if not token:
        sys.exit("❌ Variabile d'ambiente TRAKT_ACCESS_TOKEN non impostata.")
    return {
        "client_id": os.environ.get("TRAKT_CLIENT_ID", CLIENT_ID_DEFAULT),
        "client_secret": os.environ.get("TRAKT_CLIENT_SECRET", CLIENT_SECRET_DEFAULT),
        "access_token": token,
        "refresh_token": os.environ.get("TRAKT_REFRESH_TOKEN", "")
    }


def load_nuvio_config() -> dict:
    token = os.environ.get("NUVIO_ACCESS_TOKEN")
    if not token:
        sys.exit("❌ Variabile d'ambiente NUVIO_ACCESS_TOKEN non impostata.")
    return {
        "base_url": os.environ.get("NUVIO_BASE_URL", "https://api.nuvio.tv"),
        "access_token": token,
        "api_key": os.environ.get("NUVIO_API_KEY", "")
    }


def exchange_code_for_token(code: str, client_id: str = CLIENT_ID_DEFAULT, client_secret: str = CLIENT_SECRET_DEFAULT) -> dict:
    token_data = {
        "code": code.strip(),
        "client_id": client_id,
        "client_secret": client_secret,
        "redirect_uri": REDIRECT_URI,
        "grant_type": "authorization_code"
    }

    req = urllib.request.Request("https://api.trakt.tv/oauth/token", data=json.dumps(token_data).encode("utf-8"), headers=HEADERS)
    try:
        with urllib.request.urlopen(req) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        sys.exit(f"❌ Errore HTTP {e.code}: {e.read().decode('utf-8')}")
    except Exception as e:
        sys.exit(f"❌ Errore scambio token: {e}")


def fetch_nuvio_history(since_days: int = 31) -> list:
    config = load_nuvio_config()
    base_url = config.get("base_url", "https://api.nuvio.tv").rstrip("/")
    access_token = config.get("access_token")
    api_key = config.get("api_key")

    headers = dict(HEADERS)
    headers["Authorization"] = f"Bearer {access_token}"
    if api_key:
        headers["apikey"] = api_key

    cutoff_ts = int((datetime.now().timestamp() - (since_days * 86400)) * 1000)
    url = f"{base_url}/rest/v1/watch_progress?select=*&last_watched=gte.{cutoff_ts}&order=last_watched.desc"

    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except Exception as e:
        sys.stderr.write(f"❌ Errore lettura cronologia Nuvio: {e}\n")
        return []


def push_to_trakt(trakt_config: dict, payload: dict) -> dict:
    access_token = trakt_config.get("access_token")
    client_id = trakt_config.get("client_id")

    headers = {
        "Content-Type": "application/json",
        "trakt-api-version": "2",
        "trakt-api-key": client_id,
        "Authorization": f"Bearer {access_token}",
        "User-Agent": "Mozilla/5.0"
    }

    url = "https://api.trakt.tv/sync/history"
    req = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"), headers=headers)
    try:
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        sys.stderr.write(f"❌ Errore Trakt HTTP {e.code}: {e.read().decode('utf-8')}\n")
        return {}
    except Exception as e:
        sys.stderr.write(f"❌ Errore Trakt: {e}\n")
        return {}

#!/usr/bin/env python3
"""
Nuvio API Client.
"""

import os
import sys
import json
import urllib.request
import urllib.error
from datetime import datetime

HEADERS = {
    "Content-Type": "application/json",
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

_TITLE_CACHE = {}


def load_config() -> dict:
    access_token = os.environ.get("NUVIO_ACCESS_TOKEN")
    if not access_token:
        sys.exit("❌ Variabile d'ambiente NUVIO_ACCESS_TOKEN non impostata.")
    return {
        "base_url": os.environ.get("NUVIO_BASE_URL", "https://api.nuvio.tv"),
        "api_key": os.environ.get("NUVIO_API_KEY", ""),
        "access_token": access_token,
        "refresh_token": os.environ.get("NUVIO_REFRESH_TOKEN", ""),
        "email": os.environ.get("NUVIO_EMAIL", ""),
        "profile_id": 0,
    }


def refresh_token_if_needed(config: dict) -> str:
    base_url = config.get("base_url", "https://api.nuvio.tv").rstrip("/")
    refresh_token = config.get("refresh_token")
    api_key = config.get("api_key", "")

    if not refresh_token:
        return config.get("access_token", "")

    url = f"{base_url}/auth/v1/token?grant_type=refresh_token"
    payload = {"refresh_token": refresh_token}
    headers = dict(HEADERS)
    if api_key:
        headers["apikey"] = api_key

    req = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"), headers=headers)
    try:
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            return data.get("access_token", config.get("access_token", ""))
    except Exception:
        return config.get("access_token", "")


def get_title_from_imdb(content_type: str, imdb_id: str) -> str:
    if not imdb_id or not imdb_id.startswith("tt"):
        return imdb_id or "Sconosciuto"

    if imdb_id in _TITLE_CACHE:
        return _TITLE_CACHE[imdb_id]

    media_type = "series" if content_type == "series" else "movie"
    url = f"https://v3-cinemeta.strem.io/meta/{media_type}/{imdb_id}.json"
    req = urllib.request.Request(url, headers={"User-Agent": HEADERS["User-Agent"]})
    try:
        with urllib.request.urlopen(req, timeout=3) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            title = data.get("meta", {}).get("name")
            if title:
                _TITLE_CACHE[imdb_id] = title
                return title
    except Exception:
        pass

    _TITLE_CACHE[imdb_id] = imdb_id
    return imdb_id


def fetch_watch_progress(base_url: str, access_token: str, api_key: str = "") -> list:
    url = f"{base_url}/rest/v1/watch_progress?select=*&order=last_watched.desc"
    headers = dict(HEADERS)
    headers["Authorization"] = f"Bearer {access_token}"
    if api_key:
        headers["apikey"] = api_key

    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            if isinstance(data, list):
                return data
    except Exception as e:
        sys.stderr.write(f"⚠️ Errore lettura watch_progress: {e}\n")
    return []


def parse_progress_item(raw: dict) -> dict:
    cid = raw.get("content_id", "")
    ctype = raw.get("content_type", "unknown")
    if ctype in ("tv", "show"):
        ctype = "series"
    elif ctype == "film":
        ctype = "movie"

    season = raw.get("season")
    episode = raw.get("episode")
    pos = raw.get("position", 0)
    dur = raw.get("duration", 0)
    ts = raw.get("last_watched")

    dt_str = "N/A"
    if ts:
        if isinstance(ts, (int, float)):
            dt_str = datetime.fromtimestamp(ts / 1000).strftime("%Y-%m-%d %H:%M:%S")
        else:
            dt_str = str(ts)

    pct = round((pos / dur) * 100, 1) if dur > 0 else 0.0
    title = get_title_from_imdb(ctype, cid)

    return {
        "id": cid,
        "title": title,
        "type": ctype,
        "season": season,
        "episode": episode,
        "last_watched": dt_str,
        "timestamp_ms": ts or 0,
        "progress_percent": pct,
        "position_sec": round(pos / 1000) if pos else 0,
        "duration_sec": round(dur / 1000) if dur else 0,
        "is_completed": pct >= 85.0
    }

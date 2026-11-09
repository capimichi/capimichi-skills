#!/usr/bin/env python3
"""
Nuvio Watched Items & Library Report Generator
Reads credentials from ~/.nuvio-mcp, auto-refreshes token if needed, and fetches watch history/library.
"""

import os
import sys
import json
import csv
import argparse
import urllib.request
import urllib.error
from datetime import datetime

CONFIG_PATH = os.path.expanduser("~/.nuvio-mcp")

HEADERS = {
    "Content-Type": "application/json",
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

_TITLE_CACHE = {}


def load_config() -> dict:
    access_token = os.environ.get("NUVIO_ACCESS_TOKEN")
    if not access_token:
        print("❌ Variabile d'ambiente NUVIO_ACCESS_TOKEN non impostata.")
        sys.exit(1)
    return {
        "base_url": os.environ.get("NUVIO_BASE_URL", "https://api.nuvio.tv"),
        "api_key": os.environ.get("NUVIO_API_KEY", ""),
        "access_token": access_token,
        "refresh_token": os.environ.get("NUVIO_REFRESH_TOKEN", ""),
        "email": os.environ.get("NUVIO_EMAIL", ""),
        "profile_id": 0,
    }


def save_config(config: dict):
    pass


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
            if "access_token" in data:
                config["access_token"] = data["access_token"]
                if "refresh_token" in data:
                    config["refresh_token"] = data["refresh_token"]
                save_config(config)
                return data["access_token"]
    except Exception:
        pass

    return config.get("access_token", "")


def get_title_from_imdb(content_type: str, imdb_id: str) -> str:
    if not imdb_id or not imdb_id.startswith("tt"):
        return imdb_id or "Sconosciuto"
    if imdb_id in _TITLE_CACHE:
        return _TITLE_CACHE[imdb_id]

    c_type = "series" if content_type in ("series", "tv", "show") else "movie"
    url = f"https://v3-cinemeta.strem.io/meta/{c_type}/{imdb_id}.json"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=4) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            name = data.get("meta", {}).get("name", imdb_id)
            _TITLE_CACHE[imdb_id] = name
            return name
    except Exception:
        _TITLE_CACHE[imdb_id] = imdb_id
        return imdb_id


def fetch_watch_progress(base_url: str, access_token: str, api_key: str) -> list:
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
        print(f"⚠️ Errore lettura watch_progress: {e}")
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


def main():
    parser = argparse.ArgumentParser(description="Report Serie TV e Film guardati su Nuvio")
    parser.add_argument("--type", choices=["all", "series", "movie"], default="all", help="Filtra per tipo (series, movie, all)")
    parser.add_argument("--format", choices=["text", "json", "csv"], default="text", help="Formato di output (text, json, csv)")
    parser.add_argument("--limit", type=int, default=50, help="Numero massimo di elementi da mostrare")
    args = parser.parse_args()

    config = load_config()
    base_url = config.get("base_url", "https://api.nuvio.tv").rstrip("/")
    api_key = config.get("api_key", "")
    access_token = refresh_token_if_needed(config)

    raw_items = fetch_watch_progress(base_url, access_token, api_key)
    parsed_items = [parse_progress_item(x) for x in raw_items]

    if args.type != "all":
        parsed_items = [it for it in parsed_items if it["type"] == args.type]

    # Limita output
    parsed_items = parsed_items[:args.limit]

    if args.format == "json":
        print(json.dumps(parsed_items, indent=2, ensure_ascii=False))
        return

    if args.format == "csv":
        fieldnames = ["id", "title", "type", "season", "episode", "last_watched", "progress_percent", "is_completed"]
        writer = csv.DictWriter(sys.stdout, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        for it in parsed_items:
            writer.writerow(it)
        return

    series_list = [it for it in parsed_items if it["type"] == "series"]
    movies_list = [it for it in parsed_items if it["type"] == "movie"]

    print("=" * 70)
    print(f"📊 REPORT NUVIO - Totale elementi: {len(parsed_items)}")
    print("=" * 70)

    if args.type in ("all", "series"):
        print(f"\n📺 SERIE TV ({len(series_list)} elementi):")
        print("-" * 70)
        if not series_list:
            print("  Nessuna serie TV trovata.")
        for s in series_list:
            ep_str = f"S{s['season']:02d}E{s['episode']:02d}" if s.get('season') and s.get('episode') else "N/A"
            status = "Completato" if s["is_completed"] else f"In corso ({s['progress_percent']}%)"
            print(f"• {s['title']} [{s['id']}] - {ep_str}")
            print(f"  - Stato: {status}")
            print(f"  - Data ultima visione: {s['last_watched']}")
            print()

    if args.type in ("all", "movie"):
        print(f"\n🎬 FILM ({len(movies_list)} elementi):")
        print("-" * 70)
        if not movies_list:
            print("  Nessun film trovato.")
        for m in movies_list:
            status = "Completato" if m["is_completed"] else f"In corso ({m['progress_percent']}%)"
            print(f"• {m['title']} [{m['id']}]")
            print(f"  - Stato: {status}")
            print(f"  - Data ultima visione: {m['last_watched']}")
            print()


if __name__ == "__main__":
    main()

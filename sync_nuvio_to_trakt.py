#!/usr/bin/env python3
"""
Sync watched history from Nuvio (and Stremio) to Trakt.tv.
Reads ~/.nuvio-mcp and ~/.trakt-mcp, extracts watched series and movies from the last month,
and batches them into Trakt's /sync/history endpoint.
"""

import os
import sys
import json
import argparse
import urllib.request
import urllib.error
from datetime import datetime, timezone

NUVIO_CONFIG_PATH = os.path.expanduser("~/.nuvio-mcp")
TRAKT_CONFIG_PATH = os.path.expanduser("~/.trakt-mcp")

HEADERS = {
    "Content-Type": "application/json",
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}


def load_nuvio_config():
    token = os.environ.get("NUVIO_ACCESS_TOKEN")
    if not token:
        print("❌ Variabile d'ambiente NUVIO_ACCESS_TOKEN non impostata.")
        sys.exit(1)
    return {
        "base_url": os.environ.get("NUVIO_BASE_URL", "https://api.nuvio.tv"),
        "access_token": token,
        "api_key": os.environ.get("NUVIO_API_KEY", "")
    }


def load_trakt_config():
    token = os.environ.get("TRAKT_ACCESS_TOKEN")
    if not token:
        print("❌ Variabile d'ambiente TRAKT_ACCESS_TOKEN non impostata.")
        sys.exit(1)
    return {
        "client_id": os.environ.get("TRAKT_CLIENT_ID", ""),
        "client_secret": os.environ.get("TRAKT_CLIENT_SECRET", ""),
        "access_token": token,
        "refresh_token": os.environ.get("TRAKT_REFRESH_TOKEN", "")
    }


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
        print(f"❌ Errore lettura cronologia Nuvio: {e}")
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
        print(f"❌ Errore Trakt HTTP {e.code}: {e.read().decode('utf-8')}")
        return {}
    except Exception as e:
        print(f"❌ Errore Trakt: {e}")
        return {}


def main():
    parser = argparse.ArgumentParser(description="Sincronizza cronologia Nuvio su Trakt")
    parser.add_argument("--days", type=int, default=31, help="Numero di giorni passati da sincronizzare (default: 31)")
    parser.add_argument("--dry-run", action="store_true", help="Mostra solo cosa verrebbe inviato senza modificare Trakt")
    parser.add_argument("--min-progress", type=float, default=60.0, help="Progresso minimo percentuale per considerare un episodio/film visto (default: 60.0)")
    args = parser.parse_args()

    trakt_config = load_trakt_config()
    nuvio_items = fetch_nuvio_history(args.days)

    print(f"📊 Elementi totali estratti da Nuvio negli ultimi {args.days} giorni: {len(nuvio_items)}")

    shows_map = {}
    movies_list = []
    skipped_count = 0

    for it in nuvio_items:
        cid = it.get("content_id", "")
        ctype = it.get("content_type", "")
        pos = it.get("position", 0)
        dur = it.get("duration", 0)
        ts = it.get("last_watched", 0)
        season = it.get("season")
        episode = it.get("episode")

        pct = (pos / dur * 100) if dur > 0 else 0
        if pct < args.min_progress and pct > 0:
            skipped_count += 1
            continue

        watched_dt = datetime.fromtimestamp(ts / 1000, tz=timezone.utc).isoformat() if ts else datetime.now(timezone.utc).isoformat()

        if ctype in ("series", "tv", "show") and cid and season is not None and episode is not None:
            if cid not in shows_map:
                shows_map[cid] = {}
            if season not in shows_map[cid]:
                shows_map[cid][season] = {}
            shows_map[cid][season][episode] = watched_dt

        elif ctype in ("movie", "film") and cid:
            movies_list.append({
                "watched_at": watched_dt,
                "ids": {"imdb": cid}
            })

    # Costruisci payload per Trakt
    trakt_shows = []
    total_episodes_count = 0
    for show_id, seasons in shows_map.items():
        seasons_payload = []
        for s_num, eps in seasons.items():
            episodes_payload = []
            for ep_num, w_dt in eps.items():
                episodes_payload.append({
                    "number": ep_num,
                    "watched_at": w_dt
                })
                total_episodes_count += 1
            seasons_payload.append({
                "number": s_num,
                "episodes": episodes_payload
            })
        trakt_shows.append({
            "ids": {"imdb": show_id},
            "seasons": seasons_payload
        })

    trakt_payload = {
        "movies": movies_list,
        "shows": trakt_shows
    }

    print(f"\n📦 Elementi pronti per Trakt:")
    print(f"   • Film: {len(movies_list)}")
    print(f"   • Serie TV: {len(trakt_shows)} differenti ({total_episodes_count} episodi totali)")
    print(f"   • Elementi scartati (progresso < {args.min_progress}%): {skipped_count}")

    if args.dry_run:
        print("\n🔍 Modalità DRY-RUN attiva. Nessuna modifica inviata a Trakt.")
        print(json.dumps(trakt_payload, indent=2))
        return

    print("\n🚀 Invio dati a Trakt.tv in corso...")
    result = push_to_trakt(trakt_config, trakt_payload)
    if result:
        added = result.get("added", {})
        not_found = result.get("not_found", {})
        print("\n" + "=" * 60)
        print("✅ SINCRONIZZAZIONE COMPLETATA SU TRAKT!")
        print(f"   • Episodi aggiunti: {added.get('episodes', 0)}")
        print(f"   • Film aggiunti: {added.get('movies', 0)}")
        if not_found.get("shows") or not_found.get("movies"):
            print(f"   ⚠️ Elementi non trovati su Trakt: {not_found}")
        print("=" * 60)


if __name__ == "__main__":
    main()

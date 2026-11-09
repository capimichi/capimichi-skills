#!/usr/bin/env python3
"""
Stremio Watched Items & Library Report Generator
Reads credentials from ~/.stremio-mcp, fetches library/watch data, and formats reports.
"""

import os
import sys
import json
import csv
import argparse
import urllib.request
import urllib.error
from datetime import datetime

CONFIG_PATH = os.path.expanduser("~/.stremio-mcp")
DATASTORE_URL = "https://api.strem.io/api/datastoreGet"

HEADERS = {
    "Content-Type": "application/json",
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}


def load_auth_key() -> str:
    auth_key = os.environ.get("STREMIO_AUTH_KEY")
    if not auth_key:
        print("❌ Variabile d'ambiente STREMIO_AUTH_KEY non impostata.")
        sys.exit(1)
    return auth_key


def fetch_library(auth_key: str) -> list:
    payload = {
        "authKey": auth_key,
        "collection": "library"
    }
    req = urllib.request.Request(DATASTORE_URL, data=json.dumps(payload).encode("utf-8"), headers=HEADERS)
    try:
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            return data.get("result", [])
    except urllib.error.HTTPError as e:
        print(f"❌ Errore HTTP {e.code}: {e.read().decode('utf-8')}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Errore di rete: {e}")
        sys.exit(1)


def parse_item(item: dict) -> dict:
    name = item.get("name", "Sconosciuto")
    media_type = item.get("type", "unknown")
    imdb_id = item.get("_id", "")
    state = item.get("state", {})

    last_watched = state.get("lastWatched")
    time_watched = state.get("timeWatched", 0)
    duration = state.get("duration", 0)
    times_watched = state.get("timesWatched", 0)
    season = state.get("season", 0)
    episode = state.get("episode", 0)
    video_id = state.get("video_id", "")

    # Se season/episode non sono impostati ma video_id ha formato tt...:season:episode
    if (season == 0 or episode == 0) and ":" in video_id:
        parts = video_id.split(":")
        if len(parts) >= 3:
            try:
                season = int(parts[1])
                episode = int(parts[2])
            except ValueError:
                pass

    progress_pct = 0.0
    if duration > 0 and time_watched > 0:
        progress_pct = round((time_watched / duration) * 100, 1)

    is_completed = times_watched > 0 or progress_pct >= 85.0
    is_watched = bool(last_watched or times_watched > 0 or time_watched > 0)

    return {
        "id": imdb_id,
        "title": name,
        "type": media_type,
        "last_watched": last_watched or "N/A",
        "season": season if media_type == "series" else None,
        "episode": episode if media_type == "series" else None,
        "time_watched_sec": round(time_watched / 1000) if time_watched else 0,
        "duration_sec": round(duration / 1000) if duration else 0,
        "progress_percent": progress_pct,
        "times_watched": times_watched,
        "is_completed": is_completed,
        "is_watched": is_watched
    }


def main():
    parser = argparse.ArgumentParser(description="Report Serie TV e Film guardati su Stremio")
    parser.add_argument("--type", choices=["all", "series", "movie"], default="all", help="Filtra per tipo (series, movie, all)")
    parser.add_argument("--format", choices=["text", "json", "csv"], default="text", help="Formato di output (text, json, csv)")
    parser.add_argument("--only-watched", action="store_true", default=True, help="Mostra solo i contenuti effettivamente guardati")
    parser.add_argument("--all-library", dest="only_watched", action="store_false", help="Includi anche i contenuti salvati in libreria ma mai avviati")
    args = parser.parse_args()

    auth_key = load_auth_key()
    raw_items = fetch_library(auth_key)

    parsed_items = [parse_item(it) for it in raw_items]

    # Filtra per tipo
    if args.type != "all":
        parsed_items = [it for it in parsed_items if it["type"] == args.type]

    # Filtra per guardati
    if args.only_watched:
        parsed_items = [it for it in parsed_items if it["is_watched"]]

    # Ordina per data di ultima visione decrescente
    def sort_key(x):
        lw = x["last_watched"]
        return lw if lw != "N/A" else ""

    parsed_items.sort(key=sort_key, reverse=True)

    if args.format == "json":
        print(json.dumps(parsed_items, indent=2, ensure_ascii=False))
        return

    if args.format == "csv":
        fieldnames = ["id", "title", "type", "season", "episode", "last_watched", "progress_percent", "times_watched", "is_completed"]
        writer = csv.DictWriter(sys.stdout, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        for it in parsed_items:
            writer.writerow(it)
        return

    # Output testuale formattato
    series_list = [it for it in parsed_items if it["type"] == "series"]
    movies_list = [it for it in parsed_items if it["type"] == "movie"]

    print("=" * 70)
    print(f"📊 REPORT STREMIO - Totale elementi: {len(parsed_items)}")
    print("=" * 70)

    if args.type in ("all", "series"):
        print(f"\n📺 SERIE TV ({len(series_list)} trovate):")
        print("-" * 70)
        if not series_list:
            print("  Nessuna serie TV trovata.")
        for s in series_list:
            ep_info = f"S{s['season']:02d}E{s['episode']:02d}" if s['season'] and s['episode'] else "Episodio sconosciuto"
            print(f"• {s['title']} [{s['id']}]")
            print(f"  - Ultimo episodio visto: {ep_info}")
            print(f"  - Data ultima visione: {s['last_watched']}")
            if s['progress_percent'] > 0:
                print(f"  - Progresso episodio: {s['progress_percent']}%")
            if s['times_watched'] > 0:
                print(f"  - Completata: {s['times_watched']} volta/e")
            print()

    if args.type in ("all", "movie"):
        print(f"\n🎬 FILM ({len(movies_list)} trovati):")
        print("-" * 70)
        if not movies_list:
            print("  Nessun film trovato.")
        for m in movies_list:
            status = "Completato" if m["is_completed"] else f"In corso ({m['progress_percent']}%)"
            print(f"• {m['title']} [{m['id']}]")
            print(f"  - Stato: {status}")
            print(f"  - Data ultima visione: {m['last_watched']}")
            if m['times_watched'] > 0:
                print(f"  - Volte visto: {m['times_watched']}")
            print()


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Stremio API Client.
"""

import os
import sys
import json
import urllib.request
import urllib.error

DATASTORE_URL = "https://api.strem.io/api/datastoreGet"
LOGIN_URL = "https://api.strem.io/api/login"

HEADERS = {
    "Content-Type": "application/json",
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}


def load_auth_key() -> str:
    auth_key = os.environ.get("STREMIO_AUTH_KEY")
    if not auth_key:
        sys.exit("❌ Variabile d'ambiente STREMIO_AUTH_KEY non impostata.")
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
        sys.exit(f"❌ Errore HTTP {e.code}: {e.read().decode('utf-8')}")
    except Exception as e:
        sys.exit(f"❌ Errore di rete: {e}")


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

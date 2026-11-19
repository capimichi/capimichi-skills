#!/usr/bin/env python3
"""
SoulSync Client Helper.
Provides access to SoulSync REST API, remote database extraction, and MCP orchestration.
"""

import os
import sys
import subprocess
import shlex
from pathlib import Path

DEFAULT_URL = "https://soulsync.michelecapicchioni.com"
DEFAULT_SSH_HOST = "root@192.168.1.100"
DEFAULT_DB_PATH = "/var/lib/docker/volumes/soulsync_soulsync_database/_data/music_library.db"

EXPORT_SQL = """
import sqlite3, json, csv, sys

db_path = sys.argv[1]
output_file = sys.argv[2]

conn = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
c = conn.cursor()

c.execute('''
    SELECT id, spotify_track_id, spotify_data, failure_reason, retry_count, last_attempted, date_added, source_type, source_info
    FROM wishlist_tracks
    ORDER BY date_added DESC, id DESC
''')

rows = c.fetchall()

with open(output_file, 'w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    writer.writerow([
        'ID',
        'Artist',
        'Title',
        'Album',
        'Release Date',
        'Failure Reason',
        'Retry Count',
        'Date Added',
        'Last Attempted',
        'Source Type',
        'Track ID'
    ])
    
    for r in rows:
        wid, track_id, raw_data, failure_reason, retry_count, last_attempted, date_added, source_type, raw_source_info = r
        title = ''
        artist = ''
        album = ''
        release_date = ''
        
        if raw_data:
            try:
                data = json.loads(raw_data)
                title = data.get('title') or data.get('name') or ''
                
                raw_artist = data.get('artist') or data.get('artists')
                if isinstance(raw_artist, list):
                    names = []
                    for a in raw_artist:
                        if isinstance(a, dict) and a.get('name'):
                            names.append(a['name'])
                        elif isinstance(a, str):
                            names.append(a)
                    artist = ', '.join(names)
                elif isinstance(raw_artist, str):
                    artist = raw_artist
                    
                raw_album = data.get('album')
                if isinstance(raw_album, dict):
                    album = raw_album.get('name', '')
                    release_date = raw_album.get('release_date', '')
                    if not artist:
                        album_artists = raw_album.get('artists', [])
                        if isinstance(album_artists, list):
                            names = []
                            for a in album_artists:
                                if isinstance(a, dict) and a.get('name'):
                                    names.append(a['name'])
                                elif isinstance(a, str):
                                    names.append(a)
                            artist = ', '.join(names)
                elif isinstance(raw_album, str):
                    album = raw_album
            except Exception:
                pass
                
        if not artist and raw_source_info:
            try:
                s_info = json.loads(raw_source_info)
                artist = s_info.get('artist_name') or ''
                if not album:
                    album = s_info.get('album_name') or ''
            except Exception:
                pass

        writer.writerow([
            wid,
            artist,
            title,
            album,
            release_date,
            failure_reason or '',
            retry_count or 0,
            date_added or '',
            last_attempted or '',
            source_type or '',
            track_id or ''
        ])

print(f"Export completato: {len(rows)} tracce esportate in {output_file}")
"""


def get_soulsync_headers():
    api_key = os.environ.get("SOULSYNC_API_KEY")
    if not api_key:
        sys.exit("❌ Variabile d'ambiente SOULSYNC_API_KEY non impostata.")
    return {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }


def fetch_wishlist_api(base_url: str = DEFAULT_URL) -> list:
    try:
        import requests
    except ImportError:
        sys.exit("Errore: modulo 'requests' non trovato. Installa le dipendenze richieste eseguendo: pip install requests")

    url = f"{base_url.rstrip('/')}/api/v1/wishlist"
    headers = get_soulsync_headers()
    resp = requests.get(url, headers=headers)
    if resp.status_code == 200:
        res_data = resp.json()
        return res_data.get("data", {}).get("tracks", [])
    else:
        sys.exit(f"❌ Errore API SoulSync {resp.status_code}: {resp.text}")


def export_wishlist_csv(output_path: str, ssh_host: str = DEFAULT_SSH_HOST, db_path: str = DEFAULT_DB_PATH):
    dest_path = Path(output_path).expanduser().resolve()
    dest_path.parent.mkdir(parents=True, exist_ok=True)
    remote_tmp_csv = "/tmp/soulsync_wishlist_export.csv"

    print(f"🚀 Estrazione wishlist dal database remoto ({ssh_host})...")
    res = subprocess.run(
        ["ssh", ssh_host, f"python3 - '{db_path}' '{remote_tmp_csv}'"],
        input=EXPORT_SQL,
        capture_output=True,
        text=True
    )
    if res.returncode != 0:
        sys.exit(f"❌ Errore durante l'estrazione remota:\n{res.stderr}")

    print(res.stdout.strip())
    print(f"📥 Download in corso verso: {dest_path}...")
    scp_res = subprocess.run(["scp", f"{ssh_host}:{remote_tmp_csv}", str(dest_path)], capture_output=True, text=True)
    if scp_res.returncode != 0:
        sys.exit(f"❌ Errore durante il download SCP:\n{scp_res.stderr}")

    subprocess.run(["ssh", ssh_host, f"rm -f {remote_tmp_csv}"])
    print(f"✅ File salvato con successo in: {dest_path}")


def run_mcp_command(remote_args: list, ssh_host: str = DEFAULT_SSH_HOST) -> str:
    cmd_parts = ["docker", "exec", "-i", "soulsync-webui", "python3", "/app/mcp_import.py"] + remote_args
    remote_cmd = shlex.join(cmd_parts)
    ssh_cmd = ["ssh", "-o", "StrictHostKeyChecking=no", ssh_host, remote_cmd]

    res = subprocess.run(ssh_cmd, capture_output=True, text=True)
    if res.returncode != 0:
        sys.exit(f"❌ Errore esecuzione MCP remoto ({res.returncode}):\n{res.stderr}")
    return res.stdout.strip()

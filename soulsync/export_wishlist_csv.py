#!/usr/bin/env python3
"""
Script per esportare la Wishlist completa di SoulSync direttamente dal database SQLite
in un file CSV formattato e pronto all'uso.
"""

import os
import sys
import json
import csv
import subprocess
import argparse

SSH_HOST = "root@192.168.1.100"
DB_PATH = "/var/lib/docker/volumes/soulsync_soulsync_database/_data/music_library.db"

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
                
                # Parsing artista da spotify_data
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
                    
                # Parsing album da spotify_data
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
                
        # Fallback su source_info se artista/album mancano
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

def main():
    parser = argparse.ArgumentParser(description="Esporta la Wishlist di SoulSync in formato CSV.")
    parser.add_argument(
        "-o", "--output",
        default=os.path.expanduser("~/Downloads/wishlist_tracks.csv"),
        help="Percorso locale del file CSV di output (default: ~/Downloads/wishlist_tracks.csv)"
    )
    args = parser.parse_args()

    remote_tmp_csv = "/tmp/soulsync_wishlist_export.csv"
    print(f"🚀 Estrazione wishlist dal database remoto ({SSH_HOST})...")

    # Esegui lo script Python via stdin sul server per evitare problemi di escaping
    res = subprocess.run(
        ["ssh", SSH_HOST, f"python3 - '{DB_PATH}' '{remote_tmp_csv}'"],
        input=EXPORT_SQL,
        capture_output=True,
        text=True
    )
    
    if res.returncode != 0:
        print(f"❌ Errore durante l'estrazione remota:\n{res.stderr}")
        sys.exit(1)
        
    print(res.stdout.strip())

    # Scarica il file CSV via SCP
    print(f"📥 Download in corso verso: {args.output}...")
    scp_res = subprocess.run(["scp", f"{SSH_HOST}:{remote_tmp_csv}", args.output], capture_output=True, text=True)
    
    if scp_res.returncode != 0:
        print(f"❌ Errore durante il download SCP:\n{scp_res.stderr}")
        sys.exit(1)

    # Pulizia remota temporanea
    subprocess.run(["ssh", SSH_HOST, f"rm -f {remote_tmp_csv}"])

    print(f"✅ File salvato con successo in: {args.output}")

if __name__ == "__main__":
    main()

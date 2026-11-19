#!/usr/bin/env python3
"""
SoulSync CLI Entrypoint.
Gestione integrata per SoulSync: wishlist (API & export SQLite), importazione guidata MCP e consultazione log.
"""

import sys
import subprocess
from pathlib import Path

try:
    import click
except ImportError:
    sys.exit("Errore: modulo 'click' non trovato. Installa le dipendenze richieste eseguendo: pip install click")


@click.group(help="CLI per la gestione e automazione di SoulSync.")
def cli():
    pass


# ---------------------------------------------------------
# Sottocomandi Wishlist
# ---------------------------------------------------------
@cli.group(name="wishlist", help="Operazioni sulla Wishlist di SoulSync.")
def wishlist_group():
    pass


@wishlist_group.command(name="list", help="Mostra i brani presenti nella wishlist interrogando l'API REST.")
@click.option("--limit", "-l", default=0, help="Numero massimo di brani da mostrare (0 per tutti).")
def wishlist_list(limit: int):
    from soulsync.client import fetch_wishlist_api
    tracks = fetch_wishlist_api()
    total = len(tracks)
    click.echo(f"Brani in wishlist trovati: {total}\n")

    items = tracks[:limit] if limit > 0 else tracks
    for idx, track in enumerate(items, 1):
        name = track.get("track_name", "Sconosciuto")
        artist = track.get("artist_name", "Sconosciuto")
        album = track.get("album_name", "N/D")
        spotify_id = track.get("spotify_track_id", "N/D")
        reason = track.get("failure_reason", "Nessun motivo specificato")

        click.echo(f"[{idx}] {artist} - {name}")
        click.echo(f"    Album: {album}")
        click.echo(f"    ID Spotify: {spotify_id}")
        click.echo(f"    Motivo: {reason}")
        click.echo("-" * 50)


@wishlist_group.command(name="export", help="Esporta l'intera wishlist direttamente dal database SQLite remoto in CSV.")
@click.option("-o", "--output", default="~/Downloads/wishlist_tracks.csv", help="Percorso locale del file CSV (default: ~/Downloads/wishlist_tracks.csv).")
@click.option("--host", default="root@192.168.1.100", help="Host SSH del server SoulSync.")
@click.option("--db-path", default="/var/lib/docker/volumes/soulsync_soulsync_database/_data/music_library.db", help="Percorso del file SQLite sul server.")
def wishlist_export(output: str, host: str, db_path: str):
    from soulsync.client import export_wishlist_csv
    export_wishlist_csv(output, host, db_path)


# ---------------------------------------------------------
# Sottocomandi Import MCP
# ---------------------------------------------------------
@cli.group(name="mcp", help="Strumentazione MCP per importazione e catalogazione brani.")
def mcp_group():
    pass


@mcp_group.command(name="scan", help="Esegue la scansione paginata di una cartella di staging.")
@click.argument("directory_path")
@click.option("--limit", default=20, help="Numero massimo di file da scansionare.")
@click.option("--offset", default=0, help="Offset di partenza.")
@click.option("--host", default="root@192.168.1.100", help="Host SSH del server.")
def mcp_scan(directory_path: str, limit: int, offset: int, host: str):
    from soulsync.client import run_mcp_command
    out = run_mcp_command(["scan", directory_path, str(limit), str(offset)], ssh_host=host)
    click.echo(out)


@mcp_group.command(name="identify", help="Tenta l'identificazione automatica di un singolo file musicale.")
@click.argument("file_path")
@click.option("--host", default="root@192.168.1.100", help="Host SSH del server.")
def mcp_identify(file_path: str, host: str):
    from soulsync.client import run_mcp_command
    out = run_mcp_command(["identify", file_path], ssh_host=host)
    click.echo(out)


@mcp_group.command(name="search", help="Ricerca manuale di album sulle API di metadati.")
@click.argument("query")
@click.option("--source", default="deezer", help="Sorgente metadati (es. deezer, spotify, musicbrainz).")
@click.option("--host", default="root@192.168.1.100", help="Host SSH del server.")
def mcp_search(query: str, source: str, host: str):
    from soulsync.client import run_mcp_command
    out = run_mcp_command(["search", query, source], ssh_host=host)
    click.echo(out)


@mcp_group.command(name="tracklist", help="Restituisce la tracklist di un album.")
@click.argument("album_id")
@click.option("--source", default="deezer", help="Sorgente metadati (es. deezer, spotify).")
@click.option("--host", default="root@192.168.1.100", help="Host SSH del server.")
def mcp_tracklist(album_id: str, source: str, host: str):
    from soulsync.client import run_mcp_command
    out = run_mcp_command(["tracklist", album_id, source], ssh_host=host)
    click.echo(out)


@mcp_group.command(name="fuzzy-match", help="Calcola l'associazione ottimale tra un file e le tracce dell'album.")
@click.argument("file_path")
@click.argument("album_id")
@click.option("--source", default="deezer", help="Sorgente metadati.")
@click.option("--host", default="root@192.168.1.100", help="Host SSH del server.")
def mcp_fuzzy_match(file_path: str, album_id: str, source: str, host: str):
    from soulsync.client import run_mcp_command
    out = run_mcp_command(["fuzzy_match", file_path, album_id, source], ssh_host=host)
    click.echo(out)


@mcp_group.command(name="import-track", help="Esegue l'importazione definitiva del file associato alla traccia specificata.")
@click.argument("file_path")
@click.argument("album_id")
@click.argument("source")
@click.argument("track_index", type=int)
@click.option("--host", default="root@192.168.1.100", help="Host SSH del server.")
def mcp_import_track(file_path: str, album_id: str, source: str, track_index: int, host: str):
    from soulsync.client import run_mcp_command
    out = run_mcp_command(["import", file_path, album_id, source, str(track_index)], ssh_host=host)
    click.echo(out)


# ---------------------------------------------------------
# Sottocomandi Log & Diagnostica
# ---------------------------------------------------------
@cli.command(name="logs", help="Mostra o monitora i log applicativi di SoulSync sul server.")
@click.option("-n", "--lines", default=50, help="Numero di righe da mostrare (default: 50).")
@click.option("-f", "--follow", is_flag=True, help="Segui i log in tempo reale.")
@click.option("--errors", is_flag=True, help="Mostra solo le righe con ERROR o WARNING.")
@click.option("--host", default="root@192.168.1.100", help="Host SSH del server.")
def show_logs(lines: int, follow: bool, errors: bool, host: str):
    log_path = "/home/capimichi/docker/soulsync/logs/app.log"
    if errors:
        remote_cmd = f"grep -E 'ERROR|WARNING' {log_path} | tail -n {lines}"
    elif follow:
        remote_cmd = f"tail -f {log_path}"
    else:
        remote_cmd = f"tail -n {lines} {log_path}"

    cmd = ["ssh", host, remote_cmd]
    try:
        subprocess.run(cmd)
    except KeyboardInterrupt:
        click.echo("\nInterrotto.")


if __name__ == "__main__":
    cli()

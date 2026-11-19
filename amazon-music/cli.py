#!/usr/bin/env python3
"""
Amazon Music CLI Entrypoint.
Automazione e navigazione su Amazon Music con CloakBrowser: login, ricerca e ispezione album/tracce.
"""

import sys
import json
from pathlib import Path

current_dir = Path(__file__).resolve().parent
if str(current_dir) not in sys.path:
    sys.path.insert(0, str(current_dir))

try:
    import click
except ImportError:
    sys.exit("Errore: modulo 'click' non trovato. Installa le dipendenze richieste eseguendo: pip install click")


@click.group(help="CLI per l'automazione e ricerca su Amazon Music.")
def cli():
    pass


@cli.command(name="login", help="Avvia il browser visibile per effettuare il login manuale su Amazon Music.")
def login_cmd():
    from client import login_manual
    login_manual()


@cli.command(name="search", help="Cerca brani, album o artisti su Amazon Music.")
@click.argument("query")
@click.option("--section", "-s", default=None, help="Filtra per nome sezione (es. 'Brani', 'Album', 'Risultati migliori').")
@click.option("--visible", is_flag=True, default=False, help="Mostra il browser durante l'esecuzione.")
@click.option("--json", "as_json", is_flag=True, default=False, help="Output in formato JSON.")
def search_cmd(query: str, section: str, visible: bool, as_json: bool):
    from client import search_music
    click.echo(f"Ricerca in corso per '{query}'...")
    results = search_music(query, headless=not visible)

    if section:
        results = [r for r in results if section.lower() in r.get("section", "").lower()]

    if as_json:
        click.echo(json.dumps(results, indent=2, ensure_ascii=False))
        return

    click.echo(f"\n--- Risultati trovati ({len(results)}) ---")
    for idx, r in enumerate(results, 1):
        click.echo(f"[{idx:2d}] [{r['section']}] ({r['type']}) {r['title']} - {r['artist']}")
        if r["url"]:
            click.echo(f"     Link: {r['url']}")


@cli.command(name="inspect", help="Ispeziona le tracce di un album dato l'URL di Amazon Music.")
@click.argument("album_url")
@click.option("--visible", is_flag=True, default=False, help="Mostra il browser durante l'esecuzione.")
@click.option("--json", "as_json", is_flag=True, default=False, help="Output in formato JSON.")
def inspect_cmd(album_url: str, visible: bool, as_json: bool):
    from client import inspect_album_tracks
    click.echo(f"Apertura e scansione tracce per: {album_url}")
    tracks = inspect_album_tracks(album_url, headless=not visible)

    if as_json:
        click.echo(json.dumps(tracks, indent=2, ensure_ascii=False))
        return

    click.echo(f"\nTracce estratte ({len(tracks)}):")
    for idx, t in enumerate(tracks, 1):
        click.echo(f"[{idx:2d}] {t['title']} ({t['artist']}) -> {t['url']}")


if __name__ == "__main__":
    cli()

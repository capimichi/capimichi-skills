#!/usr/bin/env python3
"""
Monochrome.tf CLI Entrypoint.
Automazione e download di album musicali da Monochrome.tf tramite CloakBrowser.
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


@click.group(help="CLI per la ricerca e il download di musica da Monochrome.tf.")
def cli():
    pass


@cli.command(name="search", help="Cerca album su Monochrome.tf.")
@click.argument("query")
@click.option("--visible", is_flag=True, default=False, help="Mostra il browser durante la ricerca.")
@click.option("--json", "as_json", is_flag=True, default=False, help="Output in formato JSON.")
def search_cmd(query: str, visible: bool, as_json: bool):
    from client import search_albums
    click.echo(f"Ricerca in corso su Monochrome.tf per '{query}'...")
    results = search_albums(query, headless=not visible)

    if as_json:
        click.echo(json.dumps(results, indent=2, ensure_ascii=False))
        return

    click.echo(f"\n--- Album trovati ({len(results)}) ---")
    for idx, r in enumerate(results, 1):
        click.echo(f"[{idx:2d}] {r['title']} - {r['artist']} (ID: {r['id']})")
        if r["url"]:
            click.echo(f"     Link: {r['url']}")


@cli.command(name="download", help="Scarica un album da Monochrome.tf dato l'ID numerico o l'URL.")
@click.argument("album_url_or_id")
@click.option("--output-dir", "-o", default="~/Downloads", help="Directory locale di salvataggio (default: ~/Downloads).")
@click.option("--visible", is_flag=True, default=False, help="Mostra il browser durante il download.")
@click.option("--timeout", "-t", type=int, default=180, help="Timeout massimo in secondi (default: 180s).")
def download_cmd(album_url_or_id: str, output_dir: str, visible: bool, timeout: int):
    from client import download_album
    click.echo(f"Avvio procedura di download per: {album_url_or_id}...")
    try:
        saved_file = download_album(album_url_or_id, output_dir=output_dir, headless=not visible, timeout_sec=timeout)
        click.echo(f"✅ Download completato con successo: {saved_file}")
    except Exception as e:
        click.echo(f"❌ Errore durante il download: {e}")
        sys.exit(1)


if __name__ == "__main__":
    cli()

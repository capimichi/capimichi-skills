#!/usr/bin/env python3
"""
Spotify Search CLI Helper with Click.
"""

import json
import sys

try:
    import click
except ImportError:
    sys.exit("Errore: modulo 'click' non trovato. Installa le dipendenze richieste eseguendo: pip install click")


@click.group(help="CLI per ricerca pubblica di musica, album e artisti su Spotify.")
def cli():
    pass


@cli.command("search", help="Cerca brani, album e artisti su Spotify via interfaccia pubblica.")
@click.argument("query", nargs=-1, required=True)
@click.option("--headful", is_flag=True, default=False, help="Esegui il browser con interfaccia grafica (non headless).")
@click.option("--json", "as_json", is_flag=True, help="Output in formato JSON.")
def cmd_search(query, headful, as_json):
    q = " ".join(query)
    try:
        from browser import search_spotify
    except ImportError as e:
        sys.exit(f"Errore caricamento modulo browser: {e}")

    results = search_spotify(q, headless=not headful)

    if as_json:
        click.echo(json.dumps(results, indent=2, ensure_ascii=False))
        return

    click.echo("\n=== RISULTATO PIÙ RILEVANTE ===")
    if results.get("top_result"):
        top = results["top_result"]
        click.echo(f"  Testo: {top['text']}")
        click.echo(f"  Link:  {top['url']}")
    else:
        click.echo("  Nessun risultato rilevante in evidenza.")
    click.echo("-" * 50)

    click.echo("\n=== BRANI TROVATI ===")
    tracks = results.get("tracks", [])
    if tracks:
        for idx, t in enumerate(tracks, 1):
            click.echo(f"[{idx}] {t['title']}")
            click.echo(f"    Artisti: {', '.join(t['artists'])}")
            click.echo(f"    Durata:  {t['duration']}")
            click.echo(f"    Link:    {t['url']}")
            click.echo("    " + "." * 30)
    else:
        click.echo("  Nessun brano trovato.")
    click.echo("-" * 50)

    click.echo("\n=== ALBUM TROVATI ===")
    albums = results.get("albums", [])
    if albums:
        for idx, a in enumerate(albums, 1):
            click.echo(f"[{idx}] {a['name']} -> {a['url']}")
    else:
        click.echo("  Nessun album trovato.")
    click.echo("-" * 50)

    click.echo("\n=== ARTISTI TROVATI ===")
    artists = results.get("artists", [])
    if artists:
        for idx, art in enumerate(artists, 1):
            click.echo(f"[{idx}] {art['name']} -> {art['url']}")
    else:
        click.echo("  Nessun artista trovato.")
    click.echo("-" * 50)


if __name__ == "__main__":
    try:
        cli()
    except KeyboardInterrupt:
        sys.exit(130)

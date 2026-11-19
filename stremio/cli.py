#!/usr/bin/env python3
"""
Stremio CLI - Consultazione Libreria e Cronologia con Click.
"""

import csv
import json
import sys

try:
    import click
except ImportError:
    sys.exit("Errore: modulo 'click' non trovato. Installa le dipendenze richieste eseguendo: pip install click")

from client import load_auth_key, fetch_library, parse_item


@click.group(help="CLI per la consultazione della libreria e cronologia visioni su Stremio.")
def cli():
    pass


@cli.command("report", help="Genera il report dei contenuti guardati o salvati in libreria.")
@click.option("--type", "media_type", type=click.Choice(["all", "series", "movie"]), default="all", help="Filtra per tipo (series, movie, all).")
@click.option("--format", "out_format", type=click.Choice(["text", "json", "csv"]), default="text", help="Formato di output.")
@click.option("--all-library", is_flag=True, help="Includi anche contenuti salvati in libreria ma mai avviati.")
def cmd_report(media_type, out_format, all_library):
    auth_key = load_auth_key()
    raw_items = fetch_library(auth_key)
    parsed_items = [parse_item(it) for it in raw_items]

    if media_type != "all":
        parsed_items = [it for it in parsed_items if it["type"] == media_type]

    if not all_library:
        parsed_items = [it for it in parsed_items if it["is_watched"]]

    def sort_key(x):
        lw = x["last_watched"]
        return lw if lw != "N/A" else ""

    parsed_items.sort(key=sort_key, reverse=True)

    if out_format == "json":
        click.echo(json.dumps(parsed_items, indent=2, ensure_ascii=False))
        return

    if out_format == "csv":
        fieldnames = ["id", "title", "type", "season", "episode", "last_watched", "progress_percent", "times_watched", "is_completed"]
        writer = csv.DictWriter(sys.stdout, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        for it in parsed_items:
            writer.writerow(it)
        return

    series_list = [it for it in parsed_items if it["type"] == "series"]
    movies_list = [it for it in parsed_items if it["type"] == "movie"]

    click.echo("=" * 70)
    click.echo(f"📊 REPORT STREMIO - Totale elementi: {len(parsed_items)}")
    click.echo("=" * 70)

    if media_type in ("all", "series"):
        click.echo(f"\n📺 SERIE TV ({len(series_list)} trovate):")
        click.echo("-" * 70)
        if not series_list:
            click.echo("  Nessuna serie TV trovata.")
        for s in series_list:
            ep_info = f"S{s['season']:02d}E{s['episode']:02d}" if s['season'] and s['episode'] else "Episodio sconosciuto"
            click.echo(f"• {s['title']} [{s['id']}]")
            click.echo(f"  - Ultimo episodio visto: {ep_info}")
            click.echo(f"  - Data ultima visione: {s['last_watched']}")
            if s['progress_percent'] > 0:
                click.echo(f"  - Progresso episodio: {s['progress_percent']}%")
            if s['times_watched'] > 0:
                click.echo(f"  - Completata: {s['times_watched']} volta/e")
            click.echo()

    if media_type in ("all", "movie"):
        click.echo(f"\n🎬 FILM ({len(movies_list)} trovati):")
        click.echo("-" * 70)
        if not movies_list:
            click.echo("  Nessun film trovato.")
        for m in movies_list:
            status = "Completato" if m["is_completed"] else f"In corso ({m['progress_percent']}%)"
            click.echo(f"• {m['title']} [{m['id']}]")
            click.echo(f"  - Stato: {status}")
            click.echo(f"  - Data ultima visione: {m['last_watched']}")
            if m['times_watched'] > 0:
                click.echo(f"  - Volte visto: {m['times_watched']}")
            click.echo()


if __name__ == "__main__":
    try:
        cli()
    except KeyboardInterrupt:
        sys.exit(130)

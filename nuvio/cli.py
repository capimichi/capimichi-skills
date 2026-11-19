#!/usr/bin/env python3
"""
Nuvio CLI - Consultazione Cronologia e Visioni con Click.
"""

import csv
import json
import sys

try:
    import click
except ImportError:
    sys.exit("Errore: modulo 'click' non trovato. Installa le dipendenze richieste eseguendo: pip install click")

from client import (
    load_config,
    refresh_token_if_needed,
    fetch_watch_progress,
    parse_progress_item
)


@click.group(help="CLI per la consultazione della cronologia di visione su Nuvio.")
def cli():
    pass


@cli.command("report", help="Genera il report delle serie TV e film guardati su Nuvio.")
@click.option("--type", "media_type", type=click.Choice(["all", "series", "movie"]), default="all", help="Filtra per tipo (series, movie, all).")
@click.option("--format", "out_format", type=click.Choice(["text", "json", "csv"]), default="text", help="Formato di output.")
@click.option("--limit", type=int, default=50, help="Numero massimo di elementi da mostrare (default: 50).")
def cmd_report(media_type, out_format, limit):
    config = load_config()
    base_url = config.get("base_url", "https://api.nuvio.tv").rstrip("/")
    api_key = config.get("api_key", "")
    access_token = refresh_token_if_needed(config)

    raw_items = fetch_watch_progress(base_url, access_token, api_key)
    parsed_items = [parse_progress_item(x) for x in raw_items]

    if media_type != "all":
        parsed_items = [it for it in parsed_items if it["type"] == media_type]

    parsed_items = parsed_items[:limit]

    if out_format == "json":
        click.echo(json.dumps(parsed_items, indent=2, ensure_ascii=False))
        return

    if out_format == "csv":
        fieldnames = ["id", "title", "type", "season", "episode", "last_watched", "progress_percent", "is_completed"]
        writer = csv.DictWriter(sys.stdout, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        for it in parsed_items:
            writer.writerow(it)
        return

    series_list = [it for it in parsed_items if it["type"] == "series"]
    movies_list = [it for it in parsed_items if it["type"] == "movie"]

    click.echo("=" * 70)
    click.echo(f"📊 REPORT NUVIO - Totale elementi: {len(parsed_items)}")
    click.echo("=" * 70)

    if media_type in ("all", "series"):
        click.echo(f"\n📺 SERIE TV ({len(series_list)} elementi):")
        click.echo("-" * 70)
        if not series_list:
            click.echo("  Nessuna serie TV trovata.")
        for s in series_list:
            ep_str = f"S{s['season']:02d}E{s['episode']:02d}" if s.get('season') and s.get('episode') else "N/A"
            status = "Completato" if s["is_completed"] else f"In corso ({s['progress_percent']}%)"
            click.echo(f"• {s['title']} [{s['id']}] - {ep_str}")
            click.echo(f"  - Stato: {status}")
            click.echo(f"  - Data ultima visione: {s['last_watched']}")
            click.echo()

    if media_type in ("all", "movie"):
        click.echo(f"\n🎬 FILM ({len(movies_list)} elementi):")
        click.echo("-" * 70)
        if not movies_list:
            click.echo("  Nessun film trovato.")
        for m in movies_list:
            status = "Completato" if m["is_completed"] else f"In corso ({m['progress_percent']}%)"
            click.echo(f"• {m['title']} [{m['id']}]")
            click.echo(f"  - Stato: {status}")
            click.echo(f"  - Data ultima visione: {m['last_watched']}")
            click.echo()


if __name__ == "__main__":
    try:
        cli()
    except KeyboardInterrupt:
        sys.exit(130)

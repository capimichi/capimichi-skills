#!/usr/bin/env python3
"""
Trakt CLI - Sincronizzazione ed Autenticazione con Click.
"""

import json
import sys
from datetime import datetime, timezone

try:
    import click
except ImportError:
    sys.exit("Errore: modulo 'click' non trovato. Installa le dipendenze richieste eseguendo: pip install click")

from client import (
    CLIENT_ID_DEFAULT,
    CLIENT_SECRET_DEFAULT,
    REDIRECT_URI,
    load_trakt_config,
    exchange_code_for_token,
    fetch_nuvio_history,
    push_to_trakt
)


@click.group(help="CLI per l'autenticazione e la sincronizzazione con Trakt.tv.")
def cli():
    pass


@cli.command("auth", help="Autenticazione OAuth con Trakt.tv tramite PIN.")
@click.option("--pin", help="Codice PIN di autorizzazione fornito da Trakt.")
def cmd_auth(pin):
    if not pin:
        url = f"https://trakt.tv/oauth/authorize?response_type=code&client_id={CLIENT_ID_DEFAULT}&redirect_uri={REDIRECT_URI}"
        click.echo("=" * 60)
        click.echo("🔐 AUTENTICAZIONE TRAKT.TV")
        click.echo("=" * 60)
        click.echo(f"\n1. Apri questo link nel browser:\n   {url}")
        click.echo("\n2. Accedi e autorizza l'applicazione.")
        click.echo("3. Copia il codice PIN mostrato a video.")
        click.echo("4. Esegui: python3 cli.py auth --pin <CODICE>\n")
        return

    tokens = exchange_code_for_token(pin)
    click.echo("\n✅ Autenticazione riuscita! Imposta le seguenti variabili d'ambiente:")
    click.echo(f"export TRAKT_ACCESS_TOKEN=\"{tokens.get('access_token')}\"")
    click.echo(f"export TRAKT_REFRESH_TOKEN=\"{tokens.get('refresh_token')}\"")


@cli.command("sync", help="Sincronizza la cronologia di visione da Nuvio su Trakt.tv.")
@click.option("--days", type=int, default=31, help="Numero di giorni passati da sincronizzare (default: 31).")
@click.option("--dry-run", is_flag=True, help="Simula l'invio senza inviare modifiche a Trakt.")
@click.option("--min-progress", type=float, default=60.0, help="Progresso minimo % per considerare un contenuto visto (default: 60.0).")
def cmd_sync(days, dry_run, min_progress):
    trakt_config = load_trakt_config()
    nuvio_items = fetch_nuvio_history(days)

    click.echo(f"📊 Elementi totali estratti da Nuvio negli ultimi {days} giorni: {len(nuvio_items)}")

    shows_map = {}
    movies_list = []
    skipped_count = 0

    for it in nuvio_items:
        cid = it.get("content_id", "")
        ctype = it.get("content_type", "")
        pos = it.get("position", 0)
        dur = it.get("duration", 0)
        ts = it.get("last_watched", 0)
        season = it.get("season")
        episode = it.get("episode")

        pct = (pos / dur * 100) if dur > 0 else 0
        if 0 < pct < min_progress:
            skipped_count += 1
            continue

        watched_dt = datetime.fromtimestamp(ts / 1000, tz=timezone.utc).isoformat() if ts else datetime.now(timezone.utc).isoformat()

        if ctype in ("series", "tv", "show") and cid and season is not None and episode is not None:
            if cid not in shows_map:
                shows_map[cid] = {}
            if season not in shows_map[cid]:
                shows_map[cid][season] = {}
            shows_map[cid][season][episode] = watched_dt

        elif ctype in ("movie", "film") and cid:
            movies_list.append({
                "watched_at": watched_dt,
                "ids": {"imdb": cid}
            })

    trakt_shows = []
    total_episodes_count = 0
    for show_id, seasons in shows_map.items():
        seasons_payload = []
        for s_num, eps in seasons.items():
            episodes_payload = []
            for ep_num, w_dt in eps.items():
                episodes_payload.append({
                    "number": ep_num,
                    "watched_at": w_dt
                })
                total_episodes_count += 1
            seasons_payload.append({
                "number": s_num,
                "episodes": episodes_payload
            })
        trakt_shows.append({
            "ids": {"imdb": show_id},
            "seasons": seasons_payload
        })

    trakt_payload = {
        "movies": movies_list,
        "shows": trakt_shows
    }

    click.echo(f"\n📦 Elementi pronti per Trakt:")
    click.echo(f"   • Film: {len(movies_list)}")
    click.echo(f"   • Serie TV: {len(trakt_shows)} differenti ({total_episodes_count} episodi totali)")
    click.echo(f"   • Elementi scartati (progresso < {min_progress}%): {skipped_count}")

    if dry_run:
        click.echo("\n🔍 Modalità DRY-RUN attiva. Nessuna modifica inviata a Trakt.")
        click.echo(json.dumps(trakt_payload, indent=2))
        return

    click.echo("\n🚀 Invio dati a Trakt.tv in corso...")
    result = push_to_trakt(trakt_config, trakt_payload)
    if result:
        added = result.get("added", {})
        not_found = result.get("not_found", {})
        click.echo("\n" + "=" * 60)
        click.echo("✅ SINCRONIZZAZIONE COMPLETATA SU TRAKT!")
        click.echo(f"   • Episodi aggiunti: {added.get('episodes', 0)}")
        click.echo(f"   • Film aggiunti: {added.get('movies', 0)}")
        if not_found.get("shows") or not_found.get("movies"):
            click.echo(f"   ⚠️ Elementi non trovati su Trakt: {not_found}")
        click.echo("=" * 60)


if __name__ == "__main__":
    try:
        cli()
    except KeyboardInterrupt:
        sys.exit(130)

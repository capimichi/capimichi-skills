#!/usr/bin/env python3
"""
Lucida.to CLI Entrypoint.
Automazione e download di tracce musicali da Lucida.to tramite CloakBrowser.
"""

import os
import sys
import asyncio
from pathlib import Path

current_dir = Path(__file__).resolve().parent
if str(current_dir) not in sys.path:
    sys.path.insert(0, str(current_dir))

try:
    import click
except ImportError:
    sys.exit("Errore: modulo 'click' non trovato. Installa le dipendenze richieste eseguendo: pip install click")


@click.group(help="CLI per l'automazione del download musicale da Lucida.to.")
def cli():
    pass


@cli.command(name="track", help="Scarica un singolo brano musicale da un URL supportato (es. Spotify, Amazon Music).")
@click.argument("track_url")
@click.option("--output-dir", "-o", default="~/Downloads", help="Cartella di destinazione del download (default: ~/Downloads).")
@click.option("--visible", is_flag=True, default=False, help="Mostra il browser durante il download (default: True per Cloudflare).")
def track_cmd(track_url: str, output_dir: str, visible: bool):
    try:
        from cloakbrowser import launch_persistent_context
    except ImportError:
        sys.exit("Errore: modulo 'cloakbrowser' non trovato. Esegui: pip install cloakbrowser")

    dest_dir = os.path.expanduser(output_dir)
    os.makedirs(dest_dir, exist_ok=True)

    xdg_data = os.environ.get("XDG_DATA_HOME") or os.path.expanduser("~/.local/share")
    profile_dir = os.path.join(xdg_data, "browser-profiles", "lucida")

    click.echo(f"Avvio browser con profilo: {profile_dir}")
    context = launch_persistent_context(profile_dir, headless=not visible)
    page = context.new_page()
    page.set_viewport_size({"width": 1280, "height": 800})

    try:
        click.echo("Navigazione su https://lucida.to/...")
        page.goto("https://lucida.to/")

        click.echo("Attesa del caricamento interfaccia / Cloudflare...")
        page.wait_for_selector("#download", timeout=60000)

        click.echo(f"Inserimento URL: {track_url}")
        search_input = page.locator("#download")
        search_input.fill(track_url)

        go_button = page.locator("#go")
        go_button.click()
        page.wait_for_timeout(3000)

        error_locator = page.locator("text=/An error occur/i")
        download_locator = page.locator(".download-button").or_(page.locator("text=/scarica traccia/i"))
        combined_locator = error_locator.or_(download_locator)

        click.echo("Elaborazione in corso...")
        combined_locator.first.wait_for(state="visible", timeout=90000)

        if error_locator.is_visible():
            click.echo("❌ Errore: il server Lucida ha restituito un errore per questo brano.")
            return

        if download_locator.first.is_visible():
            click.echo("Brano pronto! Avvio del download...")
            downloads = []
            page.on("download", lambda d: downloads.append(d))
            download_locator.first.evaluate("el => el.click()")

            error_appeared = False
            for _ in range(45):
                page.wait_for_timeout(1000)
                if error_locator.is_visible():
                    error_appeared = True
                    break
                if downloads:
                    break

            if error_appeared or not downloads:
                click.echo("❌ Errore o timeout durante l'avvio del download.")
                return

            download = downloads[0]
            dest_file = os.path.join(dest_dir, download.suggested_filename)
            download.save_as(dest_file)
            click.echo(f"✅ Download completato: {dest_file}")
    finally:
        context.close()


@cli.command(name="batch", help="Esegue il download in batch da file CSV (es. wishlist_tracks.csv).")
@click.option("--csv", "csv_path", default="~/Downloads/wishlist_tracks.csv", help="Percorso del file CSV.")
@click.option("--output-dir", "-o", default="~/Downloads", help="Directory base di salvataggio.")
@click.option("--skip", type=int, default=0, help="Numero di brani iniziali da saltare.")
@click.option("--limit", "-l", type=int, default=None, help="Limite di brani da elaborare.")
@click.option("--group-albums", is_flag=True, default=False, help="Salva in cartelle <Artista>/<Album>/.")
@click.option("--album", default=None, help="Filtra per album specifico.")
@click.option("--artist", default=None, help="Filtra per artista specifico.")
@click.option("--no-resume", is_flag=True, default=False, help="Non riprendere dai brani già scaricati.")
def batch_cmd(csv_path: str, output_dir: str, skip: int, limit: int, group_albums: bool, album: str, artist: str, no_resume: bool):
    from batch_downloader import run_pipeline
    resolved_csv = os.path.expanduser(csv_path)
    resolved_out = os.path.expanduser(output_dir)

    asyncio.run(run_pipeline(
        csv_path=resolved_csv,
        output_dir=resolved_out,
        limit=limit,
        skip=skip,
        resume=not no_resume,
        group_albums=group_albums,
        filter_album=album,
        filter_artist=artist,
    ))


if __name__ == "__main__":
    cli()

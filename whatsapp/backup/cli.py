#!/usr/bin/env python3
"""
CLI per il backup e l'archiviazione incrementale delle chat WhatsApp su Cloud Storage via rclone.
"""

import sys
from pathlib import Path

try:
    import click
except ImportError:
    sys.exit("Errore: modulo 'click' non trovato. Installa le dipendenze richieste eseguendo: pip install click")

# Import engine logic
from backup_engine import DEFAULT_REMOTE_BASE, organize_and_upload


@click.group(help="Backup e archiviazione incrementale di chat WhatsApp su Cloud (rclone).")
def cli():
    pass


@cli.command("archive", help="Elabora, categorizza e carica una chat WhatsApp (.zip o cartella).")
@click.argument("source", type=click.Path(exists=True))
@click.option("-n", "--name", "chat_name", default=None, help="Nome personalizzato per la cartella della chat (default: rilevato dal file).")
@click.option("-r", "--remote", default=DEFAULT_REMOTE_BASE, help=f"Destinazione remota rclone base (default: {DEFAULT_REMOTE_BASE}).")
@click.option("--dry-run", is_flag=True, default=False, help="Simula l'operazione senza trasferire file.")
@click.option("--keep-staging", is_flag=True, default=False, help="Mantieni i file temporanei locali per verifica.")
@click.option("--no-media-subfolders", is_flag=True, default=False, help="Non suddividere Media in Foto/Video/Audio, inserisci tutto in Media/.")
def archive(source, chat_name, remote, dry_run, keep_staging, no_media_subfolders):
    ret = organize_and_upload(
        source=source,
        chat_name=chat_name,
        remote_base=remote,
        dry_run=dry_run,
        keep_staging=keep_staging,
        separate_media_subfolders=not no_media_subfolders
    )
    sys.exit(ret)


if __name__ == "__main__":
    cli()

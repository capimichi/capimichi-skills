#!/usr/bin/env python3
"""
CLI per sincronizzare il foglio REGALI NOEMI con Google Drive via rclone.
"""

import os
import sys
import subprocess
from pathlib import Path

try:
    import click
except ImportError:
    sys.exit("Errore: modulo 'click' non trovato. Installa le dipendenze richieste eseguendo: pip install click")

REMOTE_PATH_DEFAULT = "googledrive-capimichi:PERSONALE/REGALI NOEMI"
LOCAL_TMP_DEFAULT = Path("/tmp/REGALI_NOEMI.xlsx")


@click.group(help="Gestione e sincronizzazione del foglio Regali Noemi su Google Drive.")
def cli():
    pass


@cli.command("pull", help="Scarica il foglio REGALI NOEMI da Google Drive su file locale temporaneo.")
@click.option("--remote", default=REMOTE_PATH_DEFAULT, help="Percorso remoto rclone.")
@click.option("--output", "-o", type=click.Path(), default=str(LOCAL_TMP_DEFAULT), help="Percorso di salvataggio locale.")
def pull(remote, output):
    out_path = Path(output)
    click.echo(f"📥 Scaricamento in corso da {remote} a {out_path}...")
    cmd = ["rclone", "copyto", remote, str(out_path)]
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode == 0:
        click.echo(f"✅ File salvato temporaneamente in {out_path}")
    else:
        click.echo(f"❌ Errore durante il download: {res.stderr}", err=True)
        sys.exit(1)


@cli.command("push", help="Carica e sovrascrive il file locale modificato su Google Drive.")
@click.option("--remote", default=REMOTE_PATH_DEFAULT, help="Percorso remoto rclone.")
@click.option("--input", "-i", "input_file", type=click.Path(exists=True), default=str(LOCAL_TMP_DEFAULT), help="Percorso del file locale da caricare.")
def push(remote, input_file):
    in_path = Path(input_file)
    if not in_path.exists():
        click.echo(f"❌ Errore: File {in_path} non trovato.", err=True)
        sys.exit(1)

    click.echo(f"📤 Caricamento e sovrascrittura in-place su {remote}...")
    cmd = [
        "rclone", "copyto", str(in_path), remote,
        "--drive-import-formats", "xlsx",
        "--drive-allow-import-name-change",
        "-v"
    ]
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode == 0:
        click.echo("✅ Aggiornamento completato con successo (ID e link preservati)!")
    else:
        click.echo(f"❌ Errore durante il caricamento: {res.stderr}", err=True)
        sys.exit(1)


if __name__ == "__main__":
    cli()

#!/usr/bin/env python3
"""
Worldfilia CLI Entrypoint.
Suite integrata per l'automazione Worldfilia: API ufficiali (campagne, performance, link) e automazione browser (login, pixel).
"""

import sys
from pathlib import Path

# Assicura import della repository
current_dir = Path(__file__).resolve().parent
repo_root = current_dir.parent
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))

try:
    import click
except ImportError:
    sys.exit("Errore: modulo 'click' non trovato. Installa le dipendenze richieste eseguendo: pip install click")

from worldfilia.commands.campaigns import campaigns_group
from worldfilia.commands.performance import performance_group
from worldfilia.commands.links import links_group
from worldfilia.commands.pixel import pixel_group
from worldfilia.commands.session import session_group


@click.group(help="CLI per l'automazione, consultazione API e gestione campagne di Worldfilia.")
def cli():
    pass


cli.add_command(campaigns_group)
cli.add_command(performance_group)
cli.add_command(links_group)
cli.add_command(pixel_group)
cli.add_command(session_group)


if __name__ == "__main__":
    cli()

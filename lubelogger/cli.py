#!/usr/bin/env python3
"""
LubeLogger CLI - Suite di Gestione Veicoli e Manutenzione.
"""

import sys

try:
    import click
except ImportError:
    sys.exit("Errore: modulo 'click' non trovato. Installa le dipendenze richieste eseguendo: pip install click")

from commands.vehicles import vehicles_group
from commands.odometer import odometer_group
from commands.services import services_group
from commands.gas import gas_group
from commands.reminders import reminders_group
from commands.notes import notes_group


@click.group(help="CLI per la gestione veicoli, tagliandi, chilometri e scadenze su LubeLogger.")
def cli():
    pass


# Registrazione dei gruppi modulari
cli.add_command(vehicles_group, "vehicles")
cli.add_command(odometer_group, "odometer")
cli.add_command(services_group, "services")
cli.add_command(gas_group, "gas")
cli.add_command(reminders_group, "reminders")
cli.add_command(notes_group, "notes")


if __name__ == "__main__":
    try:
        cli()
    except KeyboardInterrupt:
        sys.exit(130)

import json
import click
from client import LubeLoggerClient


@click.group("notes", help="Gestione note e diario di bordo veicolo.")
def notes_group():
    pass


@notes_group.command("list", help="Elenca le note salvate per il veicolo.")
@click.option("--vehicle-id", type=int, required=True, help="ID del veicolo.")
@click.option("--json", "as_json", is_flag=True, help="Output in formato JSON.")
def list_notes(vehicle_id, as_json):
    client = LubeLoggerClient()
    notes = client.get_notes(vehicle_id)
    if as_json:
        click.echo(json.dumps(notes, indent=2, ensure_ascii=False))
        return

    if not notes:
        click.echo(f"ℹ️ Nessuna nota per il veicolo {vehicle_id}.")
        return

    click.echo(f"📝 Note veicolo {vehicle_id} ({len(notes)} note):")
    click.echo("-" * 65)
    for n in notes:
        desc = n.get("description") or n.get("Description", "Nota")
        body = n.get("note") or n.get("Note", "")
        pinned = "📌 " if n.get("pinned") or n.get("Pinned") else ""
        click.echo(f"\n{pinned}### {desc}\n{body}")


@notes_group.command("add", help="Aggiunge una nuova nota per il veicolo.")
@click.option("--vehicle-id", type=int, required=True, help="ID del veicolo.")
@click.option("--title", required=True, help="Titolo o descrizione breve.")
@click.option("--text", required=True, help="Contenuto della nota (Markdown).")
@click.option("--pin", is_flag=True, help="Fissa la nota in cima.")
def add_note(vehicle_id, title, text, pin):
    client = LubeLoggerClient()
    res = client.add_note(vehicle_id=vehicle_id, description=title, note=text, pinned=pin)
    click.echo(f"✅ Nota aggiunta con successo per il veicolo {vehicle_id}: '{title}'.")

import json
import click
from client import LubeLoggerClient


@click.group("reminders", help="Consultazione promemoria e scadenze (revisione, bollo, tagliandi).")
def reminders_group():
    pass


@reminders_group.command("list", help="Visualizza le scadenze e i promemoria per il veicolo.")
@click.option("--vehicle-id", type=int, required=True, help="ID del veicolo.")
@click.option("--json", "as_json", is_flag=True, help="Output in formato JSON.")
def list_reminders(vehicle_id, as_json):
    client = LubeLoggerClient()
    reminders = client.get_reminders(vehicle_id)
    if as_json:
        click.echo(json.dumps(reminders, indent=2, ensure_ascii=False))
        return

    if not reminders:
        click.echo(f"ℹ️ Nessun promemoria/scadenza attivo per il veicolo {vehicle_id}.")
        return

    click.echo(f"⏰ Promemoria e Scadenze veicolo {vehicle_id} ({len(reminders)}):")
    click.echo("-" * 65)
    for rem in reminders:
        desc = rem.get("description") or rem.get("Description")
        urgency = rem.get("urgency") or rem.get("Urgency", "Normal")
        due_date = rem.get("dueDate") or rem.get("DueDate", "-")
        due_mileage = rem.get("dueMileage") or rem.get("DueMileage", "-")
        click.echo(f"• [{urgency.upper()}] {desc} | Scadenza: {due_date} | A km: {due_mileage}")

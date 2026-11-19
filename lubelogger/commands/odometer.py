from datetime import date
import json
import click
from client import LubeLoggerClient


@click.group("odometer", help="Gestione chilometri / contachilometri.")
def odometer_group():
    pass


@odometer_group.command("list", help="Mostra lo storico delle letture contachilometri.")
@click.option("--vehicle-id", type=int, required=True, help="ID del veicolo.")
@click.option("--json", "as_json", is_flag=True, help="Output in formato JSON.")
def list_odometer(vehicle_id, as_json):
    client = LubeLoggerClient()
    records = client.get_odometer_records(vehicle_id)
    if as_json:
        click.echo(json.dumps(records, indent=2, ensure_ascii=False))
        return

    if not records:
        click.echo(f"ℹ️ Nessun record chilometrico per il veicolo ID {vehicle_id}.")
        return

    click.echo(f"📊 Storico chilometri veicolo {vehicle_id} ({len(records)} letture):")
    click.echo("-" * 65)
    for r in records:
        d = r.get("date") or r.get("Date")
        km = r.get("odometer") or r.get("Odometer")
        notes = r.get("notes") or r.get("Notes", "")
        notes_str = f" - {notes}" if notes else ""
        try:
            km_val = float(km)
            click.echo(f"• {d}: {km_val:,.0f} km{notes_str}")
        except (ValueError, TypeError):
            click.echo(f"• {d}: {km} km{notes_str}")


@odometer_group.command("latest", help="Recupera l'ultima lettura contachilometri registrata.")
@click.option("--vehicle-id", type=int, required=True, help="ID del veicolo.")
def latest_odometer(vehicle_id):
    client = LubeLoggerClient()
    rec = client.get_latest_odometer(vehicle_id)
    if rec is None or rec == "":
        click.echo(f"ℹ️ Nessuna lettura disponibile per il veicolo {vehicle_id}.")
        return

    if isinstance(rec, dict):
        d = rec.get("date") or rec.get("Date", "")
        km = rec.get("odometer") or rec.get("Odometer", 0)
        date_str = f" ({d})" if d else ""
    else:
        km = rec
        date_str = ""

    try:
        km_val = float(km)
        click.echo(f"📍 Ultimo chilometraggio registrato per veicolo {vehicle_id}: {km_val:,.0f} km{date_str}")
    except (ValueError, TypeError):
        click.echo(f"📍 Ultimo chilometraggio registrato per veicolo {vehicle_id}: {km} km{date_str}")


@odometer_group.command("add", help="Registra una nuova lettura contachilometri.")
@click.option("--vehicle-id", type=int, required=True, help="ID del veicolo.")
@click.option("--km", type=float, required=True, help="Chilometri attuali.")
@click.option("--date", "entry_date", default=date.today().isoformat(), help="Data lettura YYYY-MM-DD (default: oggi).")
@click.option("--notes", default="", help="Note aggiuntive opzionali.")
def add_odometer(vehicle_id, km, entry_date, notes):
    client = LubeLoggerClient()
    res = client.add_odometer_record(vehicle_id=vehicle_id, date=entry_date, odometer=km, notes=notes)
    click.echo(f"✅ Registrata lettura contachilometri per veicolo {vehicle_id}: {km:,.0f} km in data {entry_date}.")

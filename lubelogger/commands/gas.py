from datetime import date
import json
import click
from client import LubeLoggerClient


@click.group("gas", help="Gestione rifornimenti carburante.")
def gas_group():
    pass


@gas_group.command("list", help="Elenca lo storico rifornimenti carburante.")
@click.option("--vehicle-id", type=int, required=True, help="ID del veicolo.")
@click.option("--json", "as_json", is_flag=True, help="Output in formato JSON.")
def list_gas(vehicle_id, as_json):
    client = LubeLoggerClient()
    records = client.get_gas_records(vehicle_id)
    if as_json:
        click.echo(json.dumps(records, indent=2, ensure_ascii=False))
        return

    if not records:
        click.echo(f"ℹ️ Nessun rifornimento registrato per il veicolo {vehicle_id}.")
        return

    click.echo(f"⛽ Storico rifornimenti veicolo {vehicle_id} ({len(records)} rifornimenti):")
    click.echo("-" * 75)
    for r in records:
        d = r.get("date") or r.get("Date")
        km = r.get("mileage") or r.get("Mileage", "-")
        liters = r.get("gallons") or r.get("Gallons", "-")
        cost = r.get("cost") or r.get("Cost", "-")
        notes = r.get("notes") or r.get("Notes", "")
        notes_str = f" - {notes}" if notes else ""
        click.echo(f"• {d} | {km} km | {liters} L | € {cost}{notes_str}")


@gas_group.command("add", help="Registra un rifornimento di carburante.")
@click.option("--vehicle-id", type=int, required=True, help="ID del veicolo.")
@click.option("--km", type=float, required=True, help="Chilometraggio attuale.")
@click.option("--liters", type=float, required=True, help="Quantità di carburante in litri.")
@click.option("--cost", type=float, required=True, help="Costo totale del rifornimento in Euro.")
@click.option("--date", "entry_date", default=date.today().isoformat(), help="Data rifornimento YYYY-MM-DD (default: oggi).")
@click.option("--partial", is_flag=True, help="Indica che non è stato fatto il pieno completo.")
@click.option("--notes", default="", help="Note (distributore, prezzo/litro).")
def add_gas(vehicle_id, km, liters, cost, entry_date, partial, notes):
    client = LubeLoggerClient()
    res = client.add_gas_record(
        vehicle_id=vehicle_id,
        date=entry_date,
        mileage=km,
        gallons_or_liters=liters,
        cost=cost,
        is_filled=not partial,
        notes=notes,
    )
    click.echo(f"✅ Registrato rifornimento per veicolo {vehicle_id}: {liters} L a {km:,.0f} km (€ {cost:.2f}).")

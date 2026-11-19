from datetime import date
import json
import click
from client import LubeLoggerClient


@click.group("services", help="Gestione tagliandi e interventi di manutenzione.")
def services_group():
    pass


@services_group.command("list", help="Elenca lo storico tagliandi e interventi.")
@click.option("--vehicle-id", type=int, required=True, help="ID del veicolo.")
@click.option("--json", "as_json", is_flag=True, help="Output in formato JSON.")
def list_services(vehicle_id, as_json):
    client = LubeLoggerClient()
    records = client.get_service_records(vehicle_id)
    if as_json:
        click.echo(json.dumps(records, indent=2, ensure_ascii=False))
        return

    if not records:
        click.echo(f"ℹ️ Nessun intervento registrato per il veicolo {vehicle_id}.")
        return

    click.echo(f"🔧 Storico interventi veicolo {vehicle_id} ({len(records)} interventi):")
    click.echo("-" * 75)
    for r in records:
        d = r.get("date") or r.get("Date")
        desc = r.get("description") or r.get("Description")
        cost = r.get("cost") or r.get("Cost", "0")
        km = r.get("mileage") or r.get("Mileage", "-")
        notes = r.get("notes") or r.get("Notes", "")
        tags = r.get("tags") or r.get("Tags", [])
        tags_str = f" [Tag: {', '.join(tags)}]" if tags else ""
        click.echo(f"• {d} | {km} km | {desc} | € {cost}{tags_str}")
        if notes:
            click.echo(f"   Note: {notes}")


@services_group.command("add", help="Registra un nuovo tagliando o intervento.")
@click.option("--vehicle-id", type=int, required=True, help="ID del veicolo.")
@click.option("--km", type=float, required=True, help="Chilometraggio.")
@click.option("--desc", required=True, help="Descrizione intervento (es. 'Tagliando completo').")
@click.option("--cost", type=float, required=True, help="Costo totale in Euro.")
@click.option("--date", "entry_date", default=date.today().isoformat(), help="Data intervento YYYY-MM-DD (default: oggi).")
@click.option("--notes", default="", help="Note aggiuntive, codici ricambi, officina.")
@click.option("--tag", "tags", multiple=True, help="Tag (es. --tag tagliando --tag olio).")
def add_service(vehicle_id, km, desc, cost, entry_date, notes, tags):
    client = LubeLoggerClient()
    res = client.add_service_record(
        vehicle_id=vehicle_id,
        date_str=entry_date,
        mileage=km,
        description=desc,
        cost=cost,
        notes=notes,
        tags=list(tags) if tags else []
    )
    click.echo(f"✅ Registrato intervento per veicolo {vehicle_id}: '{desc}' a {km:,.0f} km (€ {cost:.2f}).")

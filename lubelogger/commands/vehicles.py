import json
import click
from client import LubeLoggerClient


@click.group("vehicles", help="Gestione veicoli nel garage.")
def vehicles_group():
    pass


@vehicles_group.command("list", help="Elenca tutti i veicoli presenti nel garage.")
@click.option("--json", "as_json", is_flag=True, help="Output in formato JSON.")
def list_vehicles(as_json):
    client = LubeLoggerClient()
    vehicles = client.get_vehicles()
    if as_json:
        click.echo(json.dumps(vehicles, indent=2, ensure_ascii=False))
        return

    if not vehicles:
        click.echo("ℹ️ Nessun veicolo presente nel garage.")
        return

    click.echo(f"🚗 Veicoli registrati ({len(vehicles)}):")
    click.echo("-" * 65)
    for v in vehicles:
        v_id = v.get("id") or v.get("Id")
        year = v.get("year") or v.get("Year")
        make = v.get("make") or v.get("Make")
        model = v.get("model") or v.get("Model")
        plate = v.get("licensePlate") or v.get("LicensePlate", "")
        click.echo(f"[{v_id}] {year} {make} {model} (Targa: {plate})")


@vehicles_group.command("info", help="Mostra informazioni dettagliate di un veicolo.")
@click.option("--id", "vehicle_id", type=int, required=True, help="ID del veicolo.")
def info_vehicle(vehicle_id):
    client = LubeLoggerClient()
    info = client.get_vehicle_info(vehicle_id)
    click.echo(json.dumps(info, indent=2, ensure_ascii=False))


@vehicles_group.command("add", help="Aggiunge un nuovo veicolo al garage.")
@click.option("--year", required=True, help="Anno di immatricolazione (es. 2021).")
@click.option("--make", required=True, help="Marca (es. Audi, Fiat, BMW).")
@click.option("--model", required=True, help="Modello (es. A4, Panda, Golf).")
@click.option("--plate", required=True, help="Targa del veicolo.")
@click.option("--fuel", default="Gasoline", help="Tipo carburante: Gasoline, Diesel, Hybrid, Electric.")
def add_vehicle(year, make, model, plate, fuel):
    client = LubeLoggerClient()
    res = client.add_vehicle(year=year, make=make, model=model, license_plate=plate, fuel_type=fuel)
    click.echo(f"✅ Veicolo aggiunto con successo: {year} {make} {model} ({plate})")


@vehicles_group.command("delete", help="Elimina un veicolo tramite ID.")
@click.option("--id", "vehicle_id", type=int, required=True, help="ID del veicolo da eliminare.")
def delete_vehicle(vehicle_id):
    client = LubeLoggerClient()
    client.delete_vehicle(vehicle_id)
    click.echo(f"✅ Veicolo {vehicle_id} eliminato con successo.")

#!/usr/bin/env python3
"""
Gestione veicoli LubeLogger via CLI.
Uso:
  python3 manage_vehicles.py list
  python3 manage_vehicles.py info --id <vehicle_id>
  python3 manage_vehicles.py add --year <year> --make <make> --model <model> --plate <plate> [--fuel <type>]
"""

import sys
import argparse
import json
from pathlib import Path

# Import dinamico del client
sys.path.insert(0, str(Path(__file__).parent))
from client import LubeLoggerClient


def main():
    parser = argparse.ArgumentParser(description="Gestione veicoli su LubeLogger")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Subcommand: list
    subparsers.add_parser("list", help="Elenca tutti i veicoli presenti nel garage")

    # Subcommand: info
    info_p = subparsers.add_parser("info", help="Mostra informazioni dettagliate di un veicolo")
    info_p.add_argument("--id", type=int, required=True, help="ID del veicolo")

    # Subcommand: add
    add_p = subparsers.add_parser("add", help="Aggiunge un nuovo veicolo")
    add_p.add_argument("--year", required=True, help="Anno di immatricolazione (es. 2020)")
    add_p.add_argument("--make", required=True, help="Marca (es. Audi, Fiat, BMW)")
    add_p.add_argument("--model", required=True, help="Modello (es. A4, Panda, Golf)")
    add_p.add_argument("--plate", required=True, help="Targa del veicolo")
    add_p.add_argument("--fuel", default="Gasoline", help="Tipo carburante: Gasoline, Diesel, Hybrid, Electric (default: Gasoline)")

    # Subcommand: delete
    del_p = subparsers.add_parser("delete", help="Elimina un veicolo tramite ID")
    del_p.add_argument("--id", type=int, required=True, help="ID del veicolo da eliminare")

    args = parser.parse_args()

    client = LubeLoggerClient()

    if args.command == "list":
        vehicles = client.get_vehicles()
        if not vehicles:
            print("ℹ️ Nessun veicolo presente nel garage.")
            return
        print(f"🚗 Veicoli registrati ({len(vehicles)}):")
        print("-" * 65)
        for v in vehicles:
            v_id = v.get("id") or v.get("Id")
            year = v.get("year") or v.get("Year")
            make = v.get("make") or v.get("Make")
            model = v.get("model") or v.get("Model")
            plate = v.get("licensePlate") or v.get("LicensePlate", "")
            print(f"[{v_id}] {year} {make} {model} (Targa: {plate})")

    elif args.command == "info":
        info = client.get_vehicle_info(args.id)
        print(json.dumps(info, indent=2, ensure_ascii=False))

    elif args.command == "add":
        res = client.add_vehicle(
            year=args.year,
            make=args.make,
            model=args.model,
            license_plate=args.plate,
            fuel_type=args.fuel,
        )
        print(f"✅ Veicolo aggiunto con successo: {args.make} {args.model} ({args.plate})")
        print(json.dumps(res, indent=2, ensure_ascii=False))

    elif args.command == "delete":
        res = client.delete_vehicle(args.id)
        print(f"🗑️ Veicolo ID {args.id} eliminato.")
        print(json.dumps(res, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()

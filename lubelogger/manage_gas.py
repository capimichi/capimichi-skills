#!/usr/bin/env python3
"""
Gestione rifornimenti carburante su LubeLogger.
Uso:
  python3 manage_gas.py list --vehicle-id <id>
  python3 manage_gas.py add --vehicle-id <id> --km <km> --liters <litri> --cost <costo_totale> [--date YYYY-MM-DD] [--notes "..."]
"""

import sys
import argparse
import json
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from client import LubeLoggerClient


def main():
    parser = argparse.ArgumentParser(description="Gestione rifornimenti carburante su LubeLogger")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # list
    list_p = subparsers.add_parser("list", help="Elenca lo storico rifornimenti carburante")
    list_p.add_argument("--vehicle-id", type=int, required=True, help="ID del veicolo")

    # add
    add_p = subparsers.add_parser("add", help="Registra un rifornimento di carburante")
    add_p.add_argument("--vehicle-id", type=int, required=True, help="ID del veicolo")
    add_p.add_argument("--km", type=float, required=True, help="Chilometraggio attuale")
    add_p.add_argument("--liters", type=float, required=True, help="Quantità di carburante in litri")
    add_p.add_argument("--cost", type=float, required=True, help="Costo totale del rifornimento in Euro")
    add_p.add_argument("--date", default=date.today().isoformat(), help="Data rifornimento YYYY-MM-DD (default: oggi)")
    add_p.add_argument("--partial", action="store_true", help="Se impostato, indica che non è stato fatto il pieno completo")
    add_p.add_argument("--notes", default="", help="Note (es. distributore, prezzo/litro)")

    args = parser.parse_args()
    client = LubeLoggerClient()

    if args.command == "list":
        records = client.get_gas_records(args.vehicle_id)
        if not records:
            print(f"ℹ️ Nessun rifornimento registrato per il veicolo {args.vehicle_id}.")
            return
        print(f"⛽ Storico rifornimenti veicolo {args.vehicle_id} ({len(records)} rifornimenti):")
        print("-" * 75)
        for r in records:
            d = r.get("date") or r.get("Date")
            km = r.get("mileage") or r.get("Mileage", "-")
            liters = r.get("gallons") or r.get("Gallons", "-")
            cost = r.get("cost") or r.get("Cost", "0")
            print(f"• [{d}] {km} km | {liters} L | € {cost}")

    elif args.command == "add":
        is_filled = not args.partial
        res = client.add_gas_record(
            vehicle_id=args.vehicle_id,
            date=args.date,
            mileage=args.km,
            gallons_or_liters=args.liters,
            cost=args.cost,
            is_filled=is_filled,
            notes=args.notes,
        )
        print(f"✅ Rifornimento registrato: {args.liters} L (€ {args.cost}) a {args.km:,.0f} km per veicolo {args.vehicle_id}.")
        print(json.dumps(res, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()

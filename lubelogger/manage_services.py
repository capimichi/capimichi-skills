#!/usr/bin/env python3
"""
Gestione tagliandi e manutenzione veicoli su LubeLogger.
Uso:
  python3 manage_services.py list --vehicle-id <id>
  python3 manage_services.py add --vehicle-id <id> --km <km> --desc "Cambio olio e filtri" --cost <costo> [--date YYYY-MM-DD] [--notes "..."] [--tags "tagliando olio"]
"""

import sys
import argparse
import json
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from client import LubeLoggerClient


def main():
    parser = argparse.ArgumentParser(description="Gestione tagliandi e manutenzioni su LubeLogger")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # list
    list_p = subparsers.add_parser("list", help="Elenca lo storico tagliandi e interventi di manutenzione")
    list_p.add_argument("--vehicle-id", type=int, required=True, help="ID del veicolo")

    # add
    add_p = subparsers.add_parser("add", help="Registra un nuovo tagliando o intervento di manutenzione")
    add_p.add_argument("--vehicle-id", type=int, required=True, help="ID del veicolo")
    add_p.add_argument("--km", type=float, required=True, help="Chilometraggio al momento dell'intervento")
    add_p.add_argument("--desc", required=True, help="Descrizione intervento (es. 'Tagliando completo', 'Cambio pastiglie')")
    add_p.add_argument("--cost", type=float, required=True, help="Costo totale dell'intervento in Euro")
    add_p.add_argument("--date", default=date.today().isoformat(), help="Data intervento YYYY-MM-DD (default: oggi)")
    add_p.add_argument("--notes", default="", help="Note aggiuntive, codici ricambi, officina")
    add_p.add_argument("--tags", nargs="*", default=[], help="Tag opzionali (es. tagliando freni olio)")

    args = parser.parse_args()
    client = LubeLoggerClient()

    if args.command == "list":
        records = client.get_service_records(args.vehicle_id)
        if not records:
            print(f"ℹ️ Nessun intervento registrato per il veicolo {args.vehicle_id}.")
            return
        print(f"🔧 Storico interventi veicolo {args.vehicle_id} ({len(records)} interventi):")
        print("-" * 75)
        for r in records:
            d = r.get("date") or r.get("Date")
            desc = r.get("description") or r.get("Description")
            cost = r.get("cost") or r.get("Cost", "0")
            km = r.get("mileage") or r.get("Mileage") or r.get("odometer") or r.get("Odometer", "-")
            notes = r.get("notes") or r.get("Notes", "")
            notes_str = f"\n   Note: {notes}" if notes else ""
            print(f"• [{d}] {desc} | {km} km | € {cost}{notes_str}")

    elif args.command == "add":
        res = client.add_service_record(
            vehicle_id=args.vehicle_id,
            date=args.date,
            mileage=args.km,
            description=args.desc,
            cost=args.cost,
            notes=args.notes,
            tags=args.tags,
        )
        print(f"✅ Intervento registrato: '{args.desc}' a {args.km:,.0f} km (€ {args.cost}) per veicolo {args.vehicle_id}.")
        print(json.dumps(res, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()

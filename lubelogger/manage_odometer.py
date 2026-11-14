#!/usr/bin/env python3
"""
Gestione chilometri / contachilometri LubeLogger via CLI.
Uso:
  python3 manage_odometer.py list --vehicle-id <id>
  python3 manage_odometer.py latest --vehicle-id <id>
  python3 manage_odometer.py add --vehicle-id <id> --km <valore> [--date YYYY-MM-DD] [--notes "note"]
"""

import sys
import argparse
import json
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from client import LubeLoggerClient


def main():
    parser = argparse.ArgumentParser(description="Gestione chilometri/odometro su LubeLogger")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # list
    list_p = subparsers.add_parser("list", help="Mostra lo storico delle letture contachilometri")
    list_p.add_argument("--vehicle-id", type=int, required=True, help="ID del veicolo")

    # latest
    latest_p = subparsers.add_parser("latest", help="Recupera l'ultima lettura contachilometri registrata")
    latest_p.add_argument("--vehicle-id", type=int, required=True, help="ID del veicolo")

    # add
    add_p = subparsers.add_parser("add", help="Registra una nuova lettura contachilometri")
    add_p.add_argument("--vehicle-id", type=int, required=True, help="ID del veicolo")
    add_p.add_argument("--km", type=float, required=True, help="Chilometri attuali")
    add_p.add_argument("--date", default=date.today().isoformat(), help="Data lettura YYYY-MM-DD (default: oggi)")
    add_p.add_argument("--notes", default="", help="Note aggiuntive opzionali")

    args = parser.parse_args()
    client = LubeLoggerClient()

    if args.command == "list":
        records = client.get_odometer_records(args.vehicle_id)
        if not records:
            print(f"ℹ️ Nessun record chilometrico per il veicolo ID {args.vehicle_id}.")
            return
        print(f"📊 Storico chilometri veicolo {args.vehicle_id} ({len(records)} letture):")
        print("-" * 65)
        for r in records:
            d = r.get("date") or r.get("Date")
            km = r.get("odometer") or r.get("Odometer")
            notes = r.get("notes") or r.get("Notes", "")
            notes_str = f" - {notes}" if notes else ""
            print(f"• {d}: {km:,.0f} km{notes_str}")

    elif args.command == "latest":
        rec = client.get_latest_odometer(args.vehicle_id)
        if not rec or not rec.get("odometer") and not rec.get("Odometer"):
            print(f"ℹ️ Nessuna lettura disponibile per il veicolo {args.vehicle_id}.")
            return
        km = rec.get("odometer") or rec.get("Odometer")
        d = rec.get("date") or rec.get("Date")
        print(f"📍 Ultimo chilometraggio veicolo {args.vehicle_id}: {km} km ({d})")

    elif args.command == "add":
        res = client.add_odometer_record(
            vehicle_id=args.vehicle_id,
            date=args.date,
            odometer=args.km,
            notes=args.notes,
        )
        print(f"✅ Registrati {args.km:,.0f} km per il veicolo {args.vehicle_id} in data {args.date}.")
        print(json.dumps(res, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()

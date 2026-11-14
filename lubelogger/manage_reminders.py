#!/usr/bin/env python3
"""
Consultazione promemoria e scadenze (revisione, bollo, tagliando) su LubeLogger.
Uso:
  python3 manage_reminders.py list --vehicle-id <id>
"""

import sys
import argparse
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from client import LubeLoggerClient


def main():
    parser = argparse.ArgumentParser(description="Consultazione promemoria e scadenze su LubeLogger")
    parser.add_argument("--vehicle-id", type=int, required=True, help="ID del veicolo")
    args = parser.parse_args()

    client = LubeLoggerClient()
    reminders = client.get_reminders(args.vehicle_id)

    if not reminders:
        print(f"ℹ️ Nessun promemoria/scadenza attivo per il veicolo {args.vehicle_id}.")
        return

    print(f"⏰ Promemoria e Scadenze veicolo {args.vehicle_id} ({len(reminders)}):")
    print("-" * 65)
    for rem in reminders:
        desc = rem.get("description") or rem.get("Description")
        urgency = rem.get("urgency") or rem.get("Urgency", "Normal")
        metric = rem.get("metric") or rem.get("Metric", "")
        due_date = rem.get("dueDate") or rem.get("DueDate", "-")
        due_mileage = rem.get("dueMileage") or rem.get("DueMileage", "-")
        print(f"• [{urgency.upper()}] {desc} | Scadenza: {due_date} | A km: {due_mileage}")


if __name__ == "__main__":
    main()

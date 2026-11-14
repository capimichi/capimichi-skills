#!/usr/bin/env python3
"""
Gestione note e diario di bordo veicolo su LubeLogger.
Uso:
  python3 manage_notes.py list --vehicle-id <id>
  python3 manage_notes.py add --vehicle-id <id> --title "Titolo" --text "Testo in markdown" [--pin]
"""

import sys
import argparse
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from client import LubeLoggerClient


def main():
    parser = argparse.ArgumentParser(description="Gestione note veicolo su LubeLogger")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # list
    list_p = subparsers.add_parser("list", help="Elenca le note salvate per il veicolo")
    list_p.add_argument("--vehicle-id", type=int, required=True, help="ID del veicolo")

    # add
    add_p = subparsers.add_parser("add", help="Aggiunge una nuova nota al veicolo")
    add_p.add_argument("--vehicle-id", type=int, required=True, help="ID del veicolo")
    add_p.add_argument("--title", required=True, help="Titolo o descrizione breve della nota")
    add_p.add_argument("--text", required=True, help="Contenuto della nota (supporta Markdown)")
    add_p.add_argument("--pin", action="store_true", help="Fissa la nota in cima")

    args = parser.parse_args()
    client = LubeLoggerClient()

    if args.command == "list":
        notes = client.get_notes(args.vehicle_id)
        if not notes:
            print(f"ℹ️ Nessuna nota per il veicolo {args.vehicle_id}.")
            return
        print(f"📝 Note veicolo {args.vehicle_id} ({len(notes)} note):")
        print("-" * 65)
        for n in notes:
            desc = n.get("description") or n.get("Description", "Nota")
            body = n.get("note") or n.get("Note", "")
            pinned = "📌 " if n.get("pinned") or n.get("Pinned") else ""
            print(f"\n{pinned}### {desc}\n{body}")

    elif args.command == "add":
        res = client.add_note(
            vehicle_id=args.vehicle_id,
            description=args.title,
            note_text=args.text,
            is_pinned=args.pin,
        )
        print(f"✅ Nota '{args.title}' aggiunta al veicolo {args.vehicle_id}.")
        print(json.dumps(res, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Worldfilia CLI - Recupera i link affiliato tracciati dell'utente via API.
Utilizzo:
    python3 api_get_links.py [--limit 20]
"""

import sys
import argparse
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from worldfilia.api_client import WorldfiliaAPI


def main():
    parser = argparse.ArgumentParser(description="Recupera i link affiliato Worldfilia via API.")
    parser.add_argument("--limit", "-l", type=int, default=15, help="Numero di link da recuperare (default: 15)")
    args = parser.parse_args()

    api = WorldfiliaAPI()

    print("=" * 70)
    print("WORLDFILIA - LINK AFFILIATO UTENTE (OFFICIAL API)")
    print("=" * 70)

    links = api.get_links(take=args.limit, order_by={"id": "desc"})

    if not links:
        print("Nessun link affiliato trovato.")
        return

    for l in links:
        lid = l.get("id")
        camp = l.get("Campaign") or {}
        landing = l.get("Landing") or {}
        sub1 = l.get("subid1") or ""
        sub2 = l.get("subid2") or ""
        domains = l.get("publisher_domains") or ""

        print(f"🔗 [Link #{lid}] Campagna: {camp.get('name', 'N/D')} (Landing: {landing.get('name', 'N/D')})")
        if sub1 or sub2:
            print(f"   SubID1: '{sub1}' | SubID2: '{sub2}'")
        if domains:
            print(f"   Domini: {domains}")
        print("-" * 70)


if __name__ == "__main__":
    main()

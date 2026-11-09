#!/usr/bin/env python3
"""
Worldfilia CLI - Recupera e filtra le campagne tramite API ufficiale.
Utilizzo:
    python3 api_get_campaigns.py [--limit 20] [--search "Rikrestin"] [--top]
"""

import sys
import argparse
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from worldfilia.api_client import WorldfiliaAPI


def main():
    parser = argparse.ArgumentParser(description="Recupera le campagne Worldfilia tramite API ufficiale.")
    parser.add_argument("--limit", "-l", type=int, default=15, help="Numero di campagne da recuperare (default: 15)")
    parser.add_argument("--search", "-s", type=str, help="Filtra per nome campagna (contains)")
    parser.add_argument("--top", action="store_true", help="Ordina per ranking descrescente")
    args = parser.parse_args()

    api = WorldfiliaAPI()

    where = None
    if args.search:
        where = {"name": {"contains": args.search}}

    order_by = {"ranking_value": "desc"} if args.top else {"id": "desc"}

    print("=" * 70)
    print("WORLDFILIA - CAMPAGNE DISPONIBILI (OFFICIAL API)")
    print("=" * 70)
    if args.search:
        print(f"Filtro ricerca: '{args.search}'")
    print(f"Ordinamento: {'Ranking decrescente' if args.top else 'ID decrescente'} | Limite: {args.limit}")
    print("-" * 70)

    campaigns = api.get_campaigns(take=args.limit, where=where, order_by=order_by)

    if not campaigns:
        print("Nessuna campagna trovata.")
        return

    for c in campaigns:
        cid = c.get("id")
        name = c.get("name")
        status = c.get("status")
        ranking = c.get("ranking_value", 0.0)
        categories = c.get("categories", "")
        landings = c.get("Landing") or []

        print(f"📦 [#{cid}] {name}")
        print(f"   Stato: {status} | Ranking: {ranking:.2f} | Categorie: {categories} | Landing: {len(landings)}")
        if landings:
            for l in landings[:3]:
                print(f"     - Landing #{l.get('id')}: {l.get('name')} -> {l.get('url')}")
            if len(landings) > 3:
                print(f"     - ... e altre {len(landings) - 3} landing page")
        print("-" * 70)


if __name__ == "__main__":
    main()

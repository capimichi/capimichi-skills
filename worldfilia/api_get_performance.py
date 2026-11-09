#!/usr/bin/env python3
"""
Worldfilia CLI - Recupera metriche e report performance tramite API REST ufficiale.
Utilizzo:
    python3 api_get_performance.py [--today] [--yesterday] [--from YYYY-MM-DD] [--to YYYY-MM-DD] [--campaign-id 3079]
"""

import sys
import argparse
from datetime import date, timedelta
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from worldfilia.api_client import WorldfiliaAPI


def main():
    parser = argparse.ArgumentParser(description="Recupera performance Worldfilia tramite API REST.")
    parser.add_argument("--today", action="store_true", help="Mostra le performance di oggi")
    parser.add_argument("--yesterday", action="store_true", help="Mostra le performance di ieri")
    parser.add_argument("--from-date", type=str, help="Data di inizio (YYYY-MM-DD)")
    parser.add_argument("--to-date", type=str, help="Data di fine (YYYY-MM-DD)")
    parser.add_argument("--campaign-id", type=int, help="Filtra per ID campagna")
    args = parser.parse_args()

    today_str = date.today().isoformat()
    yesterday_str = (date.today() - timedelta(days=1)).isoformat()

    date_from = args.from_date
    date_to = args.to_date

    if args.yesterday:
        date_from = yesterday_str
        date_to = yesterday_str
    elif args.today or (not date_from and not date_to):
        date_from = today_str
        date_to = today_str

    api = WorldfiliaAPI()

    print("=" * 65)
    print("WORLDFILIA - PERFORMANCE & CONVERSIONI (OFFICIAL REST API)")
    print("=" * 65)
    print(f"Periodo: {date_from} -> {date_to}")
    if args.campaign_id:
        print(f"Filtro Campagna ID: #{args.campaign_id}")
    print("-" * 65)

    res = api.get_performance(
        date_from=date_from,
        date_to=date_to,
        campaign_id=args.campaign_id
    )

    unique_clicks = res.get("uniqueClicks", 0)
    raw_clicks = res.get("rawClicks", 0)
    sales = res.get("sales", 0)
    pending_sales = res.get("pendingSales", 0)
    rejected_sales = res.get("rejectedSales", 0)
    invalid_sales = res.get("invalidSales", 0)
    commissions = res.get("commissions", 0.0)
    pending_commissions = res.get("pendingCommissions", 0.0)
    cr = res.get("cr", 0.0)
    epc = res.get("epc", 0.0)

    print(f"🖱️  Click Unici:       {unique_clicks} (Totali: {raw_clicks})")
    print(f"🎯 Vendite Approvate: {sales}")
    print(f"⏳ Vendite In Attesa: {pending_sales}")
    print(f"❌ Vendite Rifiutate: {rejected_sales} (Invalide: {invalid_sales})")
    print(f"📈 CR (Conv. Rate):   {cr:.2f}%")
    print(f"💰 EPC:               €{epc:.2f}")
    print(f"💵 Commissioni:       €{commissions:.2f} (In attesa: €{pending_commissions:.2f})")
    print("=" * 65)


if __name__ == "__main__":
    main()

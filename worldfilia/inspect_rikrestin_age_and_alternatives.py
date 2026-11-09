import sys
import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from worldfilia.get_campaign_detail import fetch_campaign_detail
from worldfilia.get_campaigns import fetch_campaigns

def run():
    print("=" * 60)
    print("1. DETTAGLIO RIKRESTIN (ID: 5540)")
    print("=" * 60)
    res_rik = fetch_campaigns(name_contains="Rikrestin", first=5)
    c_list = res_rik.get("campaigns", [])
    for c in c_list:
        print(f"ID: {c.get('id')}")
        print(f"Nome: {c.get('name')}")
        print(f"Prezzo cliente: {c.get('price')} {c.get('currency')}")
        print(f"Commissione: € {c.get('commission')}")
        print(f"Data Creazione nel DB Worldfilia: {c.get('created')}")
        print(f"Data Ultima Modifica: {c.get('modified')}")
        print(f"Ranking value: {c.get('ranking_value')}")
        print(f"Status: {c.get('status')}")
        print("-" * 40)

    print("\n" + "=" * 60)
    print("2. CAMPAGNE PIÙ RECENTI IN ITALIA (Ultime aggiunte)")
    print("=" * 60)
    recent = fetch_campaigns(
        first=25,
        country_code="IT",
        order_by=[{"created": "desc"}]
    )
    for c in recent.get("campaigns", []):
        print(f"ID {c.get('id'):<5} | Creato: {str(c.get('created'))[:10]} | Comm: €{c.get('commission'):<5} | Prezzo: €{c.get('price'):<5} | {c.get('name')}")

    print("\n" + "=" * 60)
    print("3. TOP PERFORMING IN ITALIA (Più vendute / Ranking più alto)")
    print("=" * 60)
    top = fetch_campaigns(
        first=20,
        country_code="IT",
        order_by=[{"ranking_value": "desc"}]
    )
    for c in top.get("campaigns", []):
        print(f"ID {c.get('id'):<5} | Creato: {str(c.get('created'))[:10]} | Rank: {c.get('ranking_value'):<5} | Comm: €{c.get('commission'):<5} | Prezzo: €{c.get('price'):<5} | {c.get('name')}")

if __name__ == "__main__":
    run()

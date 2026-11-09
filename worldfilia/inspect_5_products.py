import sys
import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from worldfilia.get_campaign_detail import fetch_campaign_detail
from worldfilia.get_campaigns import fetch_campaigns

CAMPAIGN_IDS = [5538, 2331, 2323, 3966, 3866, 5567]

def run():
    print("=" * 60)
    print("DETTAGLIO DEI 5 PRODOTTI")
    print("=" * 60)

    # 1. Fetch campaigns from list query to get ranking_value, tolerance, etc.
    res = fetch_campaigns(first=100, country_code="IT")
    c_map = {c["id"]: c for c in res.get("campaigns", []) if c.get("id") in CAMPAIGN_IDS}

    for cid in CAMPAIGN_IDS:
        print(f"\n--- CAMPAIGN ID: {cid} ---")
        detail = fetch_campaign_detail(campaign_id=cid)
        list_data = c_map.get(cid, {})

        print(f"Nome: {detail.get('name') or list_data.get('name')}")
        print(f"Prezzo: {detail.get('price') or list_data.get('price')} EUR")
        print(f"Commissione (Payout): € {detail.get('commission') or list_data.get('commission')}")
        print(f"Ranking Worldfilia: {list_data.get('ranking_value')}")
        print(f"Tolleranza / Cancellazioni: {detail.get('tolerance') or list_data.get('tolerance')}%")
        print(f"Tempi di pagamento: {detail.get('payment_times')}")
        print(f"Advertiser: {detail.get('Advertiser', {}).get('name') if detail.get('Advertiser') else list_data.get('advertiser')}")
        landings = detail.get("Landing", [])
        print(f"Numero di Landings disponibili: {len(landings) if isinstance(landings, list) else landings}")
        if isinstance(landings, list) and landings:
            for l in landings[:2]:
                print(f"  Landing: {l.get('name')} -> {l.get('url')}")

if __name__ == "__main__":
    run()

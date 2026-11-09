import sys
import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from worldfilia.get_campaigns import fetch_campaigns

ids = [5538, 2331, 2323, 3966, 3866, 5567]
res = fetch_campaigns(first=200, country_code="IT", order_by=[{"ranking_value": "desc"}])
camps = [c for c in res.get("campaigns", []) if c.get("id") in ids]
for c in camps:
    cid = c.get("id")
    rank = c.get("ranking_value")
    comm = c.get("commission")
    price = c.get("price")
    tol = c.get("tolerance")
    adv = c.get("advertiser")
    name = c.get("name")
    print(f"ID {cid:<5} | Rank: {rank:<8} | Comm: €{comm:<5} | Prezzo: €{price:<5} | Tolleranza: {tol}% | Adv: {adv} | {name}")

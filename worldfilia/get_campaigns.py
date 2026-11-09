import sys
import json
from pathlib import Path
from typing import Optional, Dict, Any, List

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from worldfilia.browser import launch_worldfilia_browser

CAMPAIGNS_QUERY = """
query campaigns($filter: CampaignWhereInput!, $first: Int, $last: Int, $after: CampaignWhereUniqueInput, $before: CampaignWhereUniqueInput, $orderBy: [CampaignOrderByWithRelationInput!]) {
  campaigns(
    where: $filter
    first: $first
    last: $last
    after: $after
    before: $before
    orderBy: $orderBy
  ) {
    id
    name
    logoUrl
    ranking_value
    price
    currency
    tolerance
    commission
    status
    created
    modified
    expiration
    ctype
    wf_commission
    advertiser
    Country {
      id
      name
      alpha2
    }
  }
}
"""

CAMPAIGNS_COUNT_QUERY = """
query campaignsCount($filter: CampaignWhereInput!) {
  campaignsCount(where: $filter)
}
"""

def fetch_campaigns(
    first: int = 10,
    after_id: Optional[int] = None,
    country_code: Optional[str] = None,
    name_contains: Optional[str] = None,
    min_commission: Optional[float] = None,
    max_commission: Optional[float] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    order_by: Optional[Dict[str, str]] = None
) -> Dict[str, Any]:
    """
    Esegue la query GraphQL per recuperare le campagne di Worldfilia utilizzando la sessione autenticata.
    Supporta filtri per nazione, nome, commissioni e range di prezzo.
    """
    if order_by is None:
        order_by = {"created": "desc"}

    filter_dict: Dict[str, Any] = {
        "status": {"not": {"equals": "S"}}
    }
    if country_code:
        filter_dict["Country"] = {"alpha2": {"equals": country_code.upper()}}
    if name_contains:
        filter_dict["name"] = {"contains": name_contains}
    if min_commission is not None or max_commission is not None:
        comm_filter = {}
        if min_commission is not None:
            comm_filter["gte"] = min_commission
        if max_commission is not None:
            comm_filter["lte"] = max_commission
        filter_dict["commission"] = comm_filter
    if min_price is not None or max_price is not None:
        price_filter = {}
        if min_price is not None:
            price_filter["gte"] = min_price
        if max_price is not None:
            price_filter["lte"] = max_price
        filter_dict["price"] = price_filter

    variables: Dict[str, Any] = {
        "filter": filter_dict,
        "first": first,
        "orderBy": order_by
    }
    if after_id is not None:
        variables["after"] = {"id": after_id}

    context = launch_worldfilia_browser(headless=True)
    page = context.pages[0] if context.pages else context.new_page()

    try:
        # Apri il portale per sincronizzare il contesto cookie/CORS
        page.goto("https://portal.worldfilia.net/publisher/campaigns", wait_until="domcontentloaded")

        result = page.evaluate("""async ({ query, countQuery, variables }) => {
            const countResp = await fetch('https://portal-api.worldfilia.net/graphql', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                credentials: 'include',
                body: JSON.stringify({
                    operationName: 'campaignsCount',
                    query: countQuery,
                    variables: { filter: variables.filter }
                })
            });
            const countData = await countResp.json();

            const campResp = await fetch('https://portal-api.worldfilia.net/graphql', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                credentials: 'include',
                body: JSON.stringify({
                    operationName: 'campaigns',
                    query: query,
                    variables: variables
                })
            });
            const campData = await campResp.json();

            return {
                totalCount: countData?.data?.campaignsCount || 0,
                campaigns: campData?.data?.campaigns || [],
                errors: campData?.errors || null
            };
        }""", {"query": CAMPAIGNS_QUERY, "countQuery": CAMPAIGNS_COUNT_QUERY, "variables": variables})

        return result
    finally:
        context.close()

def main():
    print("Recupero campagne da Worldfilia GraphQL API...")
    res = fetch_campaigns(first=10)
    print(f"Totale campagne disponibili: {res['totalCount']}")
    print(f"Campagne recuperate nel batch: {len(res['campaigns'])}")
    print("-" * 60)
    for c in res['campaigns']:
        country = c.get('Country') or {}
        country_str = f"[{country.get('alpha2', '??')}] {country.get('name', 'N/D')}"
        print(f"ID {c['id']:<5} | Comm: €{c['commission']:<5} | Prezzo: {c['price']} {c['currency']} | {country_str} | {c['name']}")

if __name__ == "__main__":
    main()

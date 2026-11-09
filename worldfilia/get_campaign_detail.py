import sys
import json
from pathlib import Path
from typing import Optional, Dict, Any

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from worldfilia.browser import launch_worldfilia_browser

CAMPAIGN_DETAIL_QUERY = """
query campaign($filter: CampaignWhereUniqueInput!) {
  campaign(where: $filter) {
    id
    name
    description
    price
    currency
    commission
    status
    restricted
    requested
    payment_times
    tolerance
    Landing
    extra
    Country {
      id
      name
      alpha2
    }
    CampaignCategory {
      Category {
        id
        name
      }
    }
    Advertiser {
      id
      name
    }
    CampaignVideo {
      id
      url
    }
    CampaignDocument {
      id
      name
      url
    }
  }
}
"""

PUB_ID_QUERY = """
mutation login {
  login {
    pubId
    username
  }
}
"""

def fetch_campaign_detail(campaign_id: int) -> Dict[str, Any]:
    """
    Recupera tutti i dettagli di una singola campagna Worldfilia, incluse le Landing page
    e i link affiliato generati con il pubId dell'utente.
    """
    context = launch_worldfilia_browser(headless=True)
    page = context.pages[0] if context.pages else context.new_page()

    try:
        page.goto("https://portal.worldfilia.net/publisher/campaigns", wait_until="domcontentloaded")

        res = page.evaluate("""async ({ detailQuery, pubQuery, campaignId }) => {
            // 1. Recupera publisher ID
            const pubResp = await fetch('https://portal-api.worldfilia.net/graphql', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                credentials: 'include',
                body: JSON.stringify({
                    operationName: 'login',
                    query: pubQuery
                })
            });
            const pubData = await pubResp.json();
            const pubId = pubData?.data?.login?.pubId || '';

            // 2. Recupera dettagli campagna
            const campResp = await fetch('https://portal-api.worldfilia.net/graphql', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                credentials: 'include',
                body: JSON.stringify({
                    operationName: 'campaign',
                    query: detailQuery,
                    variables: { filter: { id: campaignId } }
                })
            });
            const campData = await campResp.json();

            return {
                pubId: pubId,
                campaign: campData?.data?.campaign || null,
                errors: campData?.errors || null
            };
        }""", {
            "detailQuery": CAMPAIGN_DETAIL_QUERY,
            "pubQuery": PUB_ID_QUERY,
            "campaignId": campaign_id
        })

        if res.get("campaign") and res.get("pubId"):
            pub_id = res["pubId"]
            landings = res["campaign"].get("Landing") or []
            for landing in landings:
                raw_url = landing.get("url", "")
                landing["tracking_url"] = raw_url.replace("[[pubid]]", pub_id)

        return res
    finally:
        context.close()

def main():
    if len(sys.argv) > 1:
        campaign_id = int(sys.argv[1])
    else:
        campaign_id = 5598  # ID di esempio

    print(f"Recupero dettagli per la campagna #{campaign_id}...")
    data = fetch_campaign_detail(campaign_id)
    camp = data.get("campaign")

    if not camp:
        print("Campagna non trovata o errore:", data.get("errors"))
        return

    print("=" * 60)
    print(f"Nome: {camp['name']} (ID: {camp['id']})")
    print(f"Stato: {camp['status']} | Accesso Ristretto: {camp['restricted']} | Richiesto: {camp['requested']}")
    print(f"Prezzo: {camp['price']} {camp['currency']} | Commissione CPA: €{camp['commission']}")
    print(f"Tempi di pagamento: {camp.get('payment_times')} giorni | Nazione: {camp.get('Country', {}).get('name')}")
    
    cats = [c.get("Category", {}).get("name") for c in camp.get("CampaignCategory", []) if c.get("Category")]
    print(f"Categorie: {', '.join(cats)}")
    if camp.get("description"):
        print(f"Descrizione/Regole: {camp['description']}")

    print("\n--- LANDING PAGE & LINK AFFILIATO ---")
    for l in camp.get("Landing", []):
        print(f"• [{l.get('id')}] {l.get('name')}:")
        print(f"  Preview: {l.get('preview_url')}")
        print(f"  Link Tracciamento: {l.get('tracking_url')}")
    print("=" * 60)

if __name__ == "__main__":
    main()

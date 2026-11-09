import sys
import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from worldfilia.browser import launch_worldfilia_browser

def search_variants():
    context = launch_worldfilia_browser(headless=True)
    page = context.pages[0] if context.pages else context.new_page()

    page.goto("https://portal.worldfilia.net/publisher/campaigns", wait_until="domcontentloaded")

    # Let's search all active campaigns with krestin, rikrestin, rina
    res = page.evaluate("""async () => {
        const query = `
        query campaigns($filter: CampaignWhereInput) {
          campaigns(where: $filter) {
            id
            name
            price
            currency
            commission
            status
            ranking_value
            tolerance
            Country { alpha2 }
          }
        }`;
        const terms = ['rikrestin', 'krestin', 'rinaskin', 'rina'];
        const results = {};
        for (const term of terms) {
            const resp = await fetch('https://portal-api.worldfilia.net/graphql', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                credentials: 'include',
                body: JSON.stringify({
                    operationName: 'campaigns',
                    query: query,
                    variables: {
                        filter: {
                            name: { contains: term },
                            status: { equals: 'A' }
                        }
                    }
                })
            });
            const data = await resp.json();
            results[term] = data?.data?.campaigns || [];
        }
        return results;
    }""")

    print("=" * 60)
    print("CONFRONTO VARIANTI SU WORLDFILIA")
    print("=" * 60)

    seen_ids = set()
    for term, campaigns in res.items():
        print(f"\n--- Risultati per termine: '{term}' ({len(campaigns)} trovate) ---")
        for c in campaigns:
            if c['id'] in seen_ids:
                continue
            seen_ids.add(c['id'])
            stars = c.get('ranking_value')
            print(f"ID: {c['id']}")
            print(f"Nome: {c['name']}")
            print(f"Prezzo cliente: {c.get('price')} {c.get('currency', 'EUR')}")
            print(f"Commissione affiliato: {c.get('commission')} €")
            print(f"Ranking Worldfilia: {stars} / 5 stelle")
            print(f"Tolleranza: {c.get('tolerance')}%")
            print("-" * 40)

    context.close()

if __name__ == "__main__":
    search_variants()

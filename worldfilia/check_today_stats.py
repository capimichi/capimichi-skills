import sys
import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from worldfilia.browser import launch_worldfilia_browser

def check_stats():
    context = launch_worldfilia_browser(headless=True)
    page = context.pages[0] if context.pages else context.new_page()

    page.goto("https://portal.worldfilia.net/publisher", wait_until="networkidle")

    res = page.evaluate("""async () => {
        const query = `
        query dashboardData {
          dashboardData
        }`;
        const resp = await fetch('https://portal-api.worldfilia.net/graphql', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            credentials: 'include',
            body: JSON.stringify({
                operationName: 'dashboard',
                query: query
            })
        });
        return await resp.json();
    }""")

    print("=" * 60)
    print("STATISTICHE WORLDFILIA ATTUALI")
    print("=" * 60)
    print(json.dumps(res, indent=2))

    context.close()

if __name__ == "__main__":
    check_stats()

import sys
import json
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from worldfilia.paths import get_cache_dir
from worldfilia.browser import launch_worldfilia_browser

CAMPAIGN_ID = 5601
DETAIL_URL = f"https://portal.worldfilia.net/publisher/campaigns/{CAMPAIGN_ID}"

def main():
    cache_dir = get_cache_dir()
    print("=" * 60)
    print(f"WORLDFILIA - ISPEZIONE DETTAGLIO CAMPAGNA #{CAMPAIGN_ID}")
    print("=" * 60)

    context = launch_worldfilia_browser(headless=True)
    page = context.pages[0] if context.pages else context.new_page()

    ajax_calls = []

    def handle_request(req):
        if "graphql" in req.url:
            try:
                payload = json.loads(req.post_data)
                ajax_calls.append({
                    "type": "request",
                    "operationName": payload.get("operationName"),
                    "variables": payload.get("variables"),
                    "query": payload.get("query")
                })
            except Exception:
                pass

    def handle_response(res):
        if "graphql" in res.url:
            try:
                data = res.json()
                ajax_calls.append({
                    "type": "response",
                    "url": res.url,
                    "data": data
                })
            except Exception:
                pass

    page.on("request", handle_request)
    page.on("response", handle_response)

    print(f"Navigazione a: {DETAIL_URL}...")
    page.goto(DETAIL_URL, wait_until="networkidle")
    time.sleep(3)

    screenshot_path = cache_dir / "campaign_detail.png"
    html_path = cache_dir / "campaign_detail.html"
    page.screenshot(path=str(screenshot_path))
    html_path.write_text(page.content(), encoding="utf-8")

    json_path = cache_dir / "campaign_detail_ajax.json"
    json_path.write_text(json.dumps(ajax_calls, indent=2, ensure_ascii=False), encoding="utf-8")

    print(f"Screenshot salvato in: {screenshot_path}")
    print(f"Dump HTML salvato in: {html_path}")
    print(f"Tracciamento chiamate salvato in: {json_path}")

    # Estrai operazioni GraphQL uniche
    ops = set(item.get("operationName") for item in ajax_calls if item.get("operationName"))
    print(f"\nOperazioni GraphQL intercettate: {ops}")

    context.close()

if __name__ == "__main__":
    main()

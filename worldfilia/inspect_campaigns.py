import sys
import json
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from worldfilia.paths import get_cache_dir
from worldfilia.browser import launch_worldfilia_browser

CAMPAIGNS_URL = "https://portal.worldfilia.net/publisher/campaigns"

def main():
    cache_dir = get_cache_dir()
    print("=" * 60)
    print("WORLDFILIA - ISPEZIONE SEZIONE CAMPAGNE & CHIAMATE AJAX")
    print("=" * 60)

    context = launch_worldfilia_browser(headless=True)
    page = context.pages[0] if context.pages else context.new_page()

    ajax_calls = []

    def handle_response(response):
        # Filtra chiamate di interesse (es. json, api, publisher, ajax)
        url = response.url
        content_type = response.headers.get("content-type", "")
        if "json" in content_type or "api" in url or "campaign" in url:
            try:
                data = response.json()
                ajax_calls.append({
                    "url": url,
                    "status": response.status,
                    "method": response.request.method,
                    "data": data
                })
            except Exception:
                pass

    page.on("response", handle_response)

    print(f"Navigazione a: {CAMPAIGNS_URL}...")
    page.goto(CAMPAIGNS_URL, wait_until="networkidle")
    time.sleep(3)  # Attesa per renderizzare eventuali componenti vue/react

    # Salva screenshot e HTML
    screenshot_path = cache_dir / "campaigns_explore.png"
    html_path = cache_dir / "campaigns_explore.html"
    page.screenshot(path=str(screenshot_path))
    html_path.write_text(page.content(), encoding="utf-8")

    print(f"\nScreenshot salvato in: {screenshot_path}")
    print(f"Dump HTML salvato in: {html_path}")

    # Salva le chiamate AJAX intercettate
    ajax_log_path = cache_dir / "campaigns_ajax.json"
    ajax_log_path.write_text(json.dumps(ajax_calls, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Chiamate AJAX salvate in: {ajax_log_path}")

    print(f"\n[RIASSUNTO CHIAMATE AJAX INTERCETTATE: {len(ajax_calls)}]")
    for i, call in enumerate(ajax_calls, 1):
        print(f"\n--- Chiamata #{i} ---")
        print(f"Metodo: {call['method']}")
        print(f"URL: {call['url']}")
        print(f"Status: {call['status']}")
        sample_keys = list(call['data'].keys()) if isinstance(call['data'], dict) else f"List[{len(call['data'])}]"
        print(f"Campi risposta: {sample_keys}")

    context.close()

if __name__ == "__main__":
    main()

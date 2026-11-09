import sys
import time
import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from worldfilia.browser import launch_worldfilia_browser

def run():
    context = launch_worldfilia_browser(headless=True, args=["--window-size=1800,1000"])
    page = context.pages[0] if context.pages else context.new_page()

    try:
        responses = []
        def handle_response(response):
            if "graphql" in response.url or "conversion" in response.url or "api" in response.url:
                try:
                    data = response.json()
                    responses.append({"url": response.url, "data": data})
                except Exception:
                    pass

        page.on("response", handle_response)

        page.goto("https://portal.worldfilia.net/publisher", wait_until="networkidle")
        time.sleep(3)

        # Clicca Vedi tutte
        see_all = page.locator('text="Vedi tutte"').first
        if see_all.count() > 0:
            see_all.click()
            time.sleep(3)

        # Clicca Dettagli
        dettagli = page.locator('text="Dettagli"').first
        if dettagli.count() > 0:
            print("Clicco su Dettagli...")
            dettagli.click()
            time.sleep(3)
            page.screenshot(path="worldfilia/dettagli_modal_open.png")

        # Dump visible text
        txt = page.locator('#app, body').inner_text()
        print("\n--- TESTO VISIBILE DOPO CLICK DETTAGLI ---")
        print(txt)

        with open("worldfilia/api_responses.json", "w", encoding="utf-8") as f:
            json.dump(responses, f, indent=2)

    finally:
        context.close()

if __name__ == "__main__":
    run()

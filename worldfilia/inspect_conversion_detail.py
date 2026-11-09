import sys
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from worldfilia.paths import get_cache_dir
from worldfilia.browser import launch_worldfilia_browser

def run():
    cache_dir = get_cache_dir()
    context = launch_worldfilia_browser(headless=True)
    page = context.pages[0] if context.pages else context.new_page()

    try:
        # Naviga a Rapporti -> Conversioni
        page.goto("https://portal.worldfilia.net/publisher/reports/conversions", wait_until="networkidle")
        time.sleep(4)

        shot = cache_dir / "worldfilia_conversions.png"
        page.screenshot(path=str(shot), full_page=True)
        print("Conversion screenshot saved:", shot)

        # Stampa testo conversioni
        body = page.locator('main, #app, body').first
        print("\n--- TESTO CONVERSIONI ---")
        print(body.inner_text())

        # Controlliamo anche ieri e oggi in Rapporti generali
        page.goto("https://portal.worldfilia.net/publisher/reports", wait_until="networkidle")
        time.sleep(3)
        page.screenshot(path=str(cache_dir / "worldfilia_reports_general.png"), full_page=True)

        body2 = page.locator('main, #app, body').first
        print("\n--- TESTO REPORT GENERALE ---")
        print(body2.inner_text())

    finally:
        context.close()

if __name__ == "__main__":
    run()

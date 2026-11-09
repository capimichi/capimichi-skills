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
        page.goto("https://portal.worldfilia.net/publisher", wait_until="networkidle")
        time.sleep(3)

        # Clicca su 'Vedi tutte' vicino a conversioni o su Rapporti nel menu
        conv_section = page.locator('text="Ultime conversioni"').first
        if conv_section.count() > 0:
            see_all = page.locator('text="Vedi tutte"').first
            if see_all.count() > 0:
                print("Click su Vedi tutte...")
                see_all.click()
                time.sleep(4)
                print("URL attuale:", page.url)
                shot = cache_dir / "worldfilia_all_conversions.png"
                page.screenshot(path=str(shot), full_page=True)
                print("Screenshot salvato:", shot)

                body = page.locator('main, #app, body').first
                print("\n--- TESTO DETTAGLIO CONVERSIONI ---")
                print(body.inner_text())

    finally:
        context.close()

if __name__ == "__main__":
    run()

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

        # Clicca su Vedi tutte
        see_all = page.locator('text="Vedi tutte"').first
        if see_all.count() > 0:
            see_all.click()
            time.sleep(3)

        # Clicca sul filtro Data
        date_pill = page.locator('button:has-text("Oggi"), div:has-text("Data: Oggi"), span:has-text("Oggi")').first
        if date_pill.count() > 0:
            print("Clicco su Data: Oggi...")
            date_pill.click()
            time.sleep(2)
            page.screenshot(path=str(cache_dir / "wf_date_filter_open.png"))

            # Clicca su Ieri o Ultimi 7 giorni
            opt = page.locator('text="Ieri", text="Ultimi 7 giorni"').first
            if opt.count() > 0:
                print("Seleziono intervallo...")
                opt.click()
                time.sleep(1)
            
            # Clicca Applica o Fatto
            fatto = page.locator('button:has-text("Applica"), button:has-text("FATTO"), text="FATTO"').first
            if fatto.count() > 0:
                fatto.click()
                time.sleep(3)

        shot = cache_dir / "worldfilia_yesterday_conversions.png"
        page.screenshot(path=str(shot), full_page=True)
        print("Screenshot salvato:", shot)

        body = page.locator('main, #app, body').first
        print("\n--- TESTO CONVERSIONI IERI/SETTIMANA ---")
        print(body.inner_text())

    finally:
        context.close()

if __name__ == "__main__":
    run()

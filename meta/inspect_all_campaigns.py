import sys
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from meta.paths import get_cache_dir
from meta.browser import launch_meta_browser

AD_ACCOUNT_ID = "1116925509636183"

def run():
    cache_dir = get_cache_dir()
    context = launch_meta_browser(headless=True)
    page = context.pages[0] if context.pages else context.new_page()

    try:
        url = f"https://adsmanager.facebook.com/adsmanager/manage/campaigns?act={AD_ACCOUNT_ID}"
        page.goto(url, wait_until="networkidle")
        time.sleep(5)

        # Clicca sulla tab "Tutte le inserzioni"
        tab = page.locator('text="Tutte le inserzioni"').first
        if tab.count() > 0:
            print("Click Tutte le inserzioni...")
            tab.click()
            time.sleep(3)

        # Clicca sulla data e metti "Durata complessiva" (Lifetime) o "Oggi"
        date_picker = page.locator('button:has-text("17 set"), button:has-text("Ultimi"), button:has-text("Oggi"), div[role="button"]:has-text("Oggi")').first
        if date_picker.count() > 0:
            date_picker.click()
            time.sleep(1)
            # Cerca "Oggi" o "Durata complessiva"
            lifetime = page.locator('text="Durata massima", text="Durata complessiva", text="Oggi"').all()
            for opt in lifetime:
                print("Date option:", opt.inner_text())
            oggi = page.locator('text="Oggi"').first
            if oggi.count() > 0:
                oggi.click()
                time.sleep(3)

        # Controlliamo la tabella
        shot = cache_dir / "all_campaigns_today.png"
        page.screenshot(path=str(shot), full_page=True)
        print("Full page screenshot saved.")

        # Cerca tutti i link che portano a campagne
        links = page.locator('a[href*="campaign_id"], a[href*="manage/campaigns"]').all()
        print(f"Campaign links found: {len(links)}")
        for l in links:
            print("Link:", l.inner_text(), "->", l.get_attribute("href"))

        # Estrai tutti i testi visibili nel container della tabella
        table_container = page.locator('div[role="grid"]').first
        if table_container.count() > 0:
            rows = table_container.locator('[role="row"]').all()
            print(f"Table rows in grid: {len(rows)}")
            for idx, r in enumerate(rows):
                print(f"R[{idx}]: {r.inner_text().strip().replace(chr(10), ' | ')}")

    finally:
        context.close()

if __name__ == "__main__":
    run()

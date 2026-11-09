import sys
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from meta.browser import launch_meta_browser

AD_ACCOUNT_ID = "1116925509636183"

def run():
    context = launch_meta_browser(headless=False)
    page = context.pages[0] if context.pages else context.new_page()

    try:
        url = f"https://adsmanager.facebook.com/adsmanager/manage/campaigns?act={AD_ACCOUNT_ID}"
        page.goto(url, wait_until="networkidle")
        time.sleep(5)

        # Clicca sulla riga Rikrestin
        camp = page.locator('text="Rikrestin 2x49 - Test Vendite"').first
        if camp.count() > 0:
            camp.click()
            time.sleep(3)
            print("URL dopo click campagna:", page.url)

        # Tab Inserzioni
        page.get_by_role("tab", name="Inserzioni per 1 Campagna", exact=True).click()
        time.sleep(3)
        print("URL dopo click tab Inserzioni:", page.url)

        # Cerca link o ID dell'inserzione
        links = page.locator('a[href*="ad_id"], a[href*="selected_ad_ids"]').all()
        for l in links:
            print("Ad link:", l.inner_text(), "->", l.get_attribute("href"))

        # Cerca bottone Modifica inline (hover sulla cella dell'inserzione)
        name_cell = page.locator('div[role="gridcell"]:has-text("Nuova inserzione Vendite")').first
        if name_cell.count() > 0:
            print("Cella trovata, hover...")
            name_cell.hover()
            time.sleep(1)
            # Stampa tutti i link/bottoni visibili sotto il nome
            action_links = page.locator('a:has-text("Modifica"), div[role="button"]:has-text("Modifica"), button:has-text("Modifica")').all()
            for al in action_links:
                print("Action button:", al.inner_text(), al.bounding_box())
                if al.bounding_box() and al.bounding_box()['y'] > 400:
                    print("Clicco azione Modifica inline!")
                    al.click()
                    time.sleep(5)
                    break

        page.screenshot(path="meta/direct_ad_edit_screen.png")
        print("URL attuale:", page.url)

    finally:
        context.close()

if __name__ == "__main__":
    run()

import sys
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from meta.browser import launch_meta_browser

AD_ACCOUNT_ID = "1116925509636183"
CAMPAIGN_ID = "120251426951480676"

def run():
    context = launch_meta_browser(
        headless=True,
        args=["--window-size=2000,1080"],
        viewport={"width": 2000, "height": 1080}
    )
    page = context.pages[0] if context.pages else context.new_page()

    try:
        url = f"https://adsmanager.facebook.com/adsmanager/manage/ads?act={AD_ACCOUNT_ID}&selected_campaign_ids={CAMPAIGN_ID}"
        print(f"Navigo a: {url}")
        page.goto(url, wait_until="domcontentloaded")
        time.sleep(8)
        page.keyboard.press("Escape")
        time.sleep(2)

        # Clicca target bozza
        target = page.locator(':text("Inserzione B - Offerta COD"), :text("Inserzione senza nome"), :text("In bozza")').first
        target.click()
        time.sleep(2)

        # Clicca Modifica nella toolbar
        page.mouse.click(490, 233)
        time.sleep(6)

        # Scrolla e trova 'Aggiungi contenuto multimediale'
        btn = page.locator('div[role="button"]:has-text("Aggiungi contenuto multimediale")').first
        print("Trovato bottone multimediale:", btn.count() > 0)
        if btn.count() > 0:
            print("Eseguo scroll_into_view_if_needed...")
            btn.scroll_into_view_if_needed()
            time.sleep(2)
            print("Eseguo click con force=True...")
            btn.click(force=True)
            time.sleep(3)

        page.screenshot(path=str(PROJECT_ROOT / "meta" / "test_media_clicked.png"))
        print("Screenshot salvato in meta/test_media_clicked.png")

        # Verifica menu a tendina aperto
        menu_items = page.locator('div[role="menuitem"], div[role="menu"] div[role="button"]').all()
        print(f"Voci di menu trovate: {len(menu_items)}")
        for mi in menu_items:
            print("Menu item:", mi.inner_text().strip())

    finally:
        context.close()

if __name__ == "__main__":
    run()

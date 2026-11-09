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

        # Clicca bozza
        target = page.locator(':text("Inserzione B - Offerta COD"), :text("Inserzione senza nome"), :text("In bozza")').first
        target.click()
        time.sleep(2)

        # Clicca Modifica nella toolbar
        page.mouse.click(490, 233)
        time.sleep(6)

        # Clicca su "Controlla impostazioni predefinite"
        pref_btn = page.locator('button:has-text("Controlla impostazioni predefinite"), div[role="button"]:has-text("Controlla impostazioni predefinite")').first
        print(f"Pulsante predefinite trovato: {pref_btn.count() > 0}")
        if pref_btn.count() > 0:
            pref_btn.click()
            time.sleep(4)

        page.screenshot(path=str(PROJECT_ROOT / "meta" / "predefinite_modal.png"))
        print("Screenshot salvato in meta/predefinite_modal.png")

        # Stampa testo visibile
        dialog = page.locator('div[role="dialog"]').first
        if dialog.count() > 0:
            print("\n--- TESTO MODAL PREDEFINITE ---")
            print(dialog.inner_text())

    finally:
        context.close()

if __name__ == "__main__":
    run()

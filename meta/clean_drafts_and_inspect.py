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
    context = launch_meta_browser(headless=False)
    page = context.pages[0] if context.pages else context.new_page()

    try:
        url = f"https://adsmanager.facebook.com/adsmanager/manage/campaigns?act={AD_ACCOUNT_ID}"
        print(f"Navigazione a: {url}")
        page.goto(url, wait_until="networkidle")
        time.sleep(5)

        # Se c'è il pulsante cestino per scartare le bozze:
        # Il pulsante cestino si trova accanto al pulsante di aggiornamento e "Controlla e pubblica"
        # Cerchiamo pulsanti con aria-label="Elimina bozze" o simili
        discard_btn = page.locator('button[aria-label*="bozz"], button[title*="bozz"], div[role="button"][aria-label*="bozz"]').first
        if discard_btn.count() > 0:
            print("Pulsante bozza trovato:", discard_btn.get_attribute("aria-label"))
            discard_btn.click()
            time.sleep(2)
            # Conferma eventuale dialog
            confirm_discard = page.locator('button:has-text("Elimina"), button:has-text("Scarta"), button:has-text("Conferma")').first
            if confirm_discard.count() > 0:
                print("Conferma eliminazione bozze:", confirm_discard.inner_text())
                confirm_discard.click()
                time.sleep(3)

        shot = cache_dir / "after_drafts_clean.png"
        page.screenshot(path=str(shot))
        print(f"Screenshot salvato in {shot}")

    finally:
        context.close()

if __name__ == "__main__":
    run()

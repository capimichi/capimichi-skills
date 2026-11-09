import sys
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from meta.browser import launch_meta_browser

AD_ACCOUNT_ID = "1116925509636183"

def run():
    print("=" * 60)
    print("GENERAZIONE ANTEPRIMA INSERZIONE META ADS")
    print("=" * 60)

    context = launch_meta_browser(headless=True)
    page = context.pages[0] if context.pages else context.new_page()

    try:
        url = f"https://adsmanager.facebook.com/adsmanager/manage/ads?act={AD_ACCOUNT_ID}"
        print(f"Navigazione a: {url}")
        page.goto(url, wait_until="networkidle")
        time.sleep(5)

        # Seleziona la riga dell'inserzione
        chk = page.locator('div[role="row"]').nth(1).locator('input[type="checkbox"]').first
        if chk.count() > 0:
            chk.click(force=True)
            time.sleep(1)

        # Cerca il pulsante Anteprima nella toolbar (icona occhio o testo Anteprima)
        preview_btn = page.locator('button:has-text("Anteprima"), div[role="button"]:has-text("Anteprima")').first
        if preview_btn.count() > 0:
            print("Click pulsante Anteprima...")
            preview_btn.click()
            time.sleep(4)

            # Salva screenshot dell'anteprima
            shot_preview = PROJECT_ROOT / "meta" / "ad_preview_full.png"
            page.screenshot(path=str(shot_preview))
            print(f"Screenshot anteprima salvato in: {shot_preview}")

            # Cerchiamo se c'è il menu Condividi per generare un link
            share_btn = page.locator('button:has-text("Condividi"), div[role="button"]:has-text("Condividi"), [aria-label*="Condividi"]').first
            if share_btn.count() > 0:
                print("Trovato pulsante Condividi, clicco...")
                share_btn.click()
                time.sleep(2)
                # Opzioni nel menu condividi
                options = page.locator('div[role="menuitem"], div[role="option"], a[href*="facebook.com"]').all()
                for o in options:
                    print("Share option:", o.inner_text(), o.get_attribute("href"))

    finally:
        context.close()

if __name__ == "__main__":
    run()

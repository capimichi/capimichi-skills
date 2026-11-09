import sys
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from meta.browser import launch_meta_browser

AD_ACCOUNT_ID = "1116925509636183"

def run():
    context = launch_meta_browser(headless=True)
    page = context.pages[0] if context.pages else context.new_page()

    try:
        url = f"https://adsmanager.facebook.com/adsmanager/manage/campaigns?act={AD_ACCOUNT_ID}"
        page.goto(url, wait_until="domcontentloaded")
        time.sleep(6)

        # Seleziona Intervallo massimo
        d_btn = page.locator('button:has-text("ott"), div[role="button"]:has-text("ott"), button:has-text("Ultimi"), div[role="button"]:has-text("Ultimi")').first
        if d_btn.count() > 0:
            d_btn.click()
            time.sleep(1)
            opt = page.locator('text="Intervallo massimo"').first
            if opt.count() > 0:
                opt.click()
                time.sleep(1)
                agg = page.locator('button:has-text("Aggiorna")').first
                if agg.count() > 0:
                    agg.click()
                    time.sleep(5)

        # Dump text of the table
        body = page.locator('body').inner_text()
        print("\n--- TESTO TABELLA CON INTERVALLO MASSIMO ---")
        lines = [l.strip() for l in body.splitlines() if l.strip()]
        for l in lines[:60]:
            print(l)

    finally:
        context.close()

if __name__ == "__main__":
    run()

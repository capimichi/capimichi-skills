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
    print("APPLICAZIONE DATA INTERVALLO MASSIMO / OGGI E IERI")
    print("=" * 60)

    context = launch_meta_browser(headless=True)
    page = context.pages[0] if context.pages else context.new_page()

    try:
        url = f"https://adsmanager.facebook.com/adsmanager/manage/ads?act={AD_ACCOUNT_ID}"
        page.goto(url, wait_until="domcontentloaded")
        time.sleep(6)

        # 1. Apri il date picker
        date_btn = page.locator('button:has-text("17 ott"), button:has-text("Ultimi"), div[role="button"]:has-text("17 ott"), div[role="button"]:has-text("Ultimi")').first
        if date_btn.count() > 0:
            print("Apro date picker...")
            date_btn.click()
            time.sleep(2)

            # Clicca 'Intervallo massimo' o 'Oggi e ieri'
            opt = page.locator('text="Intervallo massimo"').first
            if opt.count() == 0:
                opt = page.locator('text="Oggi e ieri"').first
            if opt.count() == 0:
                opt = page.locator('text="Oggi"').first

            print(f"Clicco opzione: {opt.inner_text()}")
            opt.click()
            time.sleep(1)

            # Clicca 'Aggiorna'
            aggiorna_btn = page.locator('button:has-text("Aggiorna")').first
            if aggiorna_btn.count() > 0:
                print("Clicco Aggiorna...")
                aggiorna_btn.click()
                time.sleep(5)

        # Screenshot dopo l'aggiornamento della data
        shot = PROJECT_ROOT / "meta" / "real_live_metrics_today.png"
        page.screenshot(path=str(shot))
        print("Screenshot salvato in:", shot)

        print("\n=== METRICHE INSERZIONE AGGIORNATE ===")
        rows = page.locator('div[role="row"]').all()
        for idx, r in enumerate(rows):
            txt = r.inner_text().strip().replace('\n', ' | ')
            print(f"Row [{idx}]: {txt}")

    finally:
        context.close()

if __name__ == "__main__":
    run()

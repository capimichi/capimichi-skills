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
    print("LETTURA STATISTICHE LIVE OGGI")
    print("=" * 60)

    context = launch_meta_browser(
        headless=True,
        args=["--window-size=1600,1000"],
        viewport={"width": 1600, "height": 1000}
    )
    page = context.pages[0] if context.pages else context.new_page()

    try:
        url = f"https://adsmanager.facebook.com/adsmanager/manage/campaigns?act={AD_ACCOUNT_ID}"
        page.goto(url, wait_until="domcontentloaded")
        time.sleep(5)
        page.keyboard.press("Escape")
        time.sleep(1)

        # 1. Clicca sul selettore della data
        date_btn = page.locator('button[aria-label*="Data"], div[role="button"]:has-text("ott"), button:has-text("ott"), button:has-text("Ultimi")').first
        if date_btn.count() > 0:
            print("Apro date picker...")
            date_btn.click()
            time.sleep(2)

            # Clicca sulla prima opzione 'Oggi'
            oggi_label = page.locator('label:has-text("Oggi"), :text-is("Oggi")').first
            if oggi_label.count() > 0:
                print("Clicco su 'Oggi'...")
                oggi_label.click()
                time.sleep(1)

            # Clicca sul bottone blu 'Aggiorna'
            agg_btn = page.locator('button:has-text("Aggiorna")').last
            if agg_btn.count() > 0:
                print("Clicco su 'Aggiorna'...")
                agg_btn.click()
                time.sleep(6)

        # 2. Clicca sull'icona di refresh della tabella se presente
        ref = page.locator('[aria-label="Aggiorna dati tabella"]').first
        if ref.count() > 0:
            ref.click()
            time.sleep(5)

        page.screenshot(path=str(PROJECT_ROOT / "meta" / "live_today_campaigns.png"))
        print("Screenshot salvato in meta/live_today_campaigns.png")

        # Clicca sulla tab Inserzioni
        ads_tab = page.locator('button:has-text("Inserzioni"), div[role="tab"]:has-text("Inserzioni")').first
        if ads_tab.count() > 0:
            ads_tab.click()
            time.sleep(5)
            page.screenshot(path=str(PROJECT_ROOT / "meta" / "live_today_ads.png"))
            print("Screenshot salvato in meta/live_today_ads.png")

        # Dump di tutto il testo della tabella
        text = page.locator('body').inner_text()
        with open(PROJECT_ROOT / "meta" / "live_today_text.txt", "w", encoding="utf-8") as f:
            f.write(text)

        print("\n--- TESTO ESTRATTO DALLE RIGHE ---")
        rows = page.locator('div[role="row"]').all()
        for idx, r in enumerate(rows):
            print(f"Row [{idx}]: {r.inner_text().strip().replace(chr(10), ' | ')}")

    finally:
        context.close()

if __name__ == "__main__":
    run()

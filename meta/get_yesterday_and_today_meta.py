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
    print("LETTURA COMPLETA IERI E OGGI SU META ADS (2400px)")
    print("=" * 60)

    context = launch_meta_browser(
        headless=True,
        args=["--window-size=2400,1080"],
        viewport={"width": 2400, "height": 1080}
    )
    page = context.pages[0] if context.pages else context.new_page()

    try:
        url = f"https://adsmanager.facebook.com/adsmanager/manage/campaigns?act={AD_ACCOUNT_ID}"
        page.goto(url, wait_until="domcontentloaded")
        time.sleep(5)
        page.keyboard.press("Escape")
        time.sleep(1)

        # 1. Imposta data su 'Ieri' (18 Ottobre 2026)
        d_btn = page.locator('button[aria-label*="Data"], div[role="button"]:has-text("ott"), button:has-text("ott"), button:has-text("Oggi"), div[role="button"]:has-text("Oggi"), button:has-text("Ultimi")').first
        if d_btn.count() > 0:
            print("Apro date picker per Ieri...")
            d_btn.click()
            time.sleep(2)
            ieri_label = page.locator('label:has-text("Ieri"), :text-is("Ieri")').first
            if ieri_label.count() > 0:
                print("Seleziono Ieri...")
                ieri_label.click()
                time.sleep(1)
            agg_btn = page.locator('button:has-text("Aggiorna")').last
            if agg_btn.count() > 0:
                agg_btn.click()
                time.sleep(5)

        # Refresh
        ref = page.locator('[aria-label="Aggiorna dati tabella"]').first
        if ref.count() > 0:
            ref.click()
            time.sleep(5)

        page.screenshot(path=str(PROJECT_ROOT / "meta" / "meta_yesterday_2400.png"))
        print("Screenshot Ieri salvato in meta/meta_yesterday_2400.png")

        # 2. Ora imposta su 'Oggi' (19 Ottobre 2026)
        d_btn = page.locator('button[aria-label*="Data"], div[role="button"]:has-text("Ieri"), button:has-text("Ieri")').first
        if d_btn.count() > 0:
            print("Apro date picker per Oggi...")
            d_btn.click()
            time.sleep(2)
            oggi_label = page.locator('label:has-text("Oggi"), :text-is("Oggi")').first
            if oggi_label.count() > 0:
                oggi_label.click()
                time.sleep(1)
            agg_btn = page.locator('button:has-text("Aggiorna")').last
            if agg_btn.count() > 0:
                agg_btn.click()
                time.sleep(5)

        ref = page.locator('[aria-label="Aggiorna dati tabella"]').first
        if ref.count() > 0:
            ref.click()
            time.sleep(5)

        page.screenshot(path=str(PROJECT_ROOT / "meta" / "meta_today_2400.png"))
        print("Screenshot Oggi salvato in meta/meta_today_2400.png")

        # 3. Ora imposta su 'Intervallo massimo'
        d_btn = page.locator('button[aria-label*="Data"], div[role="button"]:has-text("Oggi"), button:has-text("Oggi")').first
        if d_btn.count() > 0:
            print("Apro date picker per Intervallo massimo...")
            d_btn.click()
            time.sleep(2)
            max_label = page.locator('label:has-text("Intervallo massimo"), :text-is("Intervallo massimo")').first
            if max_label.count() > 0:
                max_label.click()
                time.sleep(1)
            agg_btn = page.locator('button:has-text("Aggiorna")').last
            if agg_btn.count() > 0:
                agg_btn.click()
                time.sleep(5)

        ref = page.locator('[aria-label="Aggiorna dati tabella"]').first
        if ref.count() > 0:
            ref.click()
            time.sleep(5)

        page.screenshot(path=str(PROJECT_ROOT / "meta" / "meta_lifetime_2400.png"))
        print("Screenshot Lifetime salvato in meta/meta_lifetime_2400.png")

    finally:
        context.close()

if __name__ == "__main__":
    run()

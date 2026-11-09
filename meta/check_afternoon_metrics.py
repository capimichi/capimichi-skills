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
    print("REPORT POMERIGGIO: METRICHE META ADS IN TEMPO REALE")
    print("=" * 60)

    context = launch_meta_browser(headless=True)
    page = context.pages[0] if context.pages else context.new_page()

    try:
        url = f"https://adsmanager.facebook.com/adsmanager/manage/campaigns?act={AD_ACCOUNT_ID}"
        print(f"1. Apertura: {url}")
        page.goto(url, wait_until="domcontentloaded")
        time.sleep(6)

        # 1. Imposta data su Oggi
        d_btn = page.locator('button:has-text("ott"), div[role="button"]:has-text("ott"), button:has-text("Ultimi"), div[role="button"]:has-text("Ultimi")').first
        if d_btn.count() > 0:
            print(f"Apro date picker (attualmente: '{d_btn.inner_text().strip()}')...")
            d_btn.click()
            time.sleep(2)
            oggi_opt = page.locator(':text-is("Oggi"), div[role="option"]:has-text("Oggi")').first
            if oggi_opt.count() > 0:
                print("Seleziono 'Oggi'...")
                oggi_opt.click()
                time.sleep(1)
                agg = page.locator('button:has-text("Aggiorna")').first
                if agg.count() > 0:
                    print("Clicco Aggiorna...")
                    agg.click()
                    time.sleep(4)

        # 2. Clicca sul pulsante rinfresca tabella di Meta (icona refresh)
        refresh_btn = page.locator('[aria-label="Aggiorna dati tabella"], [aria-label*="Aggiorna dati"]').first
        if refresh_btn.count() > 0:
            print("Clicco su 'Aggiorna dati tabella'...")
            refresh_btn.click()
            time.sleep(5)

        page.screenshot(path=str(PROJECT_ROOT / "meta" / "afternoon_campaign_view.png"))

        # 3. Clicca sull'icona grafici (narrow bar a destra)
        chart_icon = page.locator('div[role="toolbar"] [aria-label*="Grafic"], [aria-label*="Visualizza grafici"], div[class*="sideRail"] div[role="button"]').first
        if chart_icon.count() > 0:
            chart_icon.click()
            time.sleep(4)

            # Clicca Visualizza se presente
            vis_btn = page.locator('button:has-text("Visualizza"), div[role="button"]:has-text("Visualizza")').first
            if vis_btn.count() > 0:
                vis_btn.click()
                time.sleep(2)

            page.screenshot(path=str(PROJECT_ROOT / "meta" / "afternoon_charts_panel.png"))

            print("\n--- TESTO PANNELLO GRAFICI POMERIGGIO ---")
            lines = [l.strip() for l in page.locator("body").inner_text().splitlines() if l.strip()]
            for l in lines[:60]:
                print(l)

        # 4. Spostati sul livello Inserzioni
        url_ads = f"https://adsmanager.facebook.com/adsmanager/manage/ads?act={AD_ACCOUNT_ID}"
        print(f"\n4. Controllo livello Inserzione: {url_ads}")
        page.goto(url_ads, wait_until="domcontentloaded")
        time.sleep(6)

        d_btn_ads = page.locator('button:has-text("ott"), div[role="button"]:has-text("ott"), button:has-text("Ultimi"), div[role="button"]:has-text("Ultimi")').first
        if d_btn_ads.count() > 0 and "Oggi" not in d_btn_ads.inner_text():
            d_btn_ads.click()
            time.sleep(1)
            oggi_opt = page.locator(':text-is("Oggi"), div[role="option"]:has-text("Oggi")').first
            if oggi_opt.count() > 0:
                oggi_opt.click()
                time.sleep(1)
                agg = page.locator('button:has-text("Aggiorna")').first
                if agg.count() > 0:
                    agg.click()
                    time.sleep(4)

        page.screenshot(path=str(PROJECT_ROOT / "meta" / "afternoon_ad_view.png"))

    finally:
        context.close()

if __name__ == "__main__":
    run()

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

        # Clicca sull'icona grafici (narrow bar a destra)
        chart_icon = page.locator('div[role="toolbar"] [aria-label*="Grafic"], [aria-label*="Visualizza grafici"], div[class*="sideRail"] div[role="button"]').first
        if chart_icon.count() > 0:
            chart_icon.click()
            time.sleep(4)

        # Ora cambia la data nel date picker in alto a destra
        date_btn = page.locator('button:has-text("17 ott"), button:has-text("Ultimi"), div[role="button"]:has-text("17 ott"), div[role="button"]:has-text("Ultimi")').first
        if date_btn.count() > 0:
            print("Apro date picker nei grafici...")
            date_btn.click()
            time.sleep(1)

            opt = page.locator('text="Intervallo massimo"').first
            if opt.count() == 0:
                opt = page.locator('text="Oggi"').first
            print(f"Clicco: {opt.inner_text()}")
            opt.click()
            time.sleep(1)

            agg = page.locator('button:has-text("Aggiorna")').first
            if agg.count() > 0:
                print("Clicco Aggiorna...")
                agg.click()
                time.sleep(5)

        page.screenshot(path=str(PROJECT_ROOT / "meta" / "charts_today_live.png"))

        # Stampa testo prestazioni
        print("\n--- TESTO GRAFICI PRESTAZIONI ---")
        lines = [l.strip() for l in page.locator("body").inner_text().splitlines() if l.strip()]
        for l in lines[:60]:
            print(l)

        # Clicca su tab 'Piattaforma'
        plat_tab = page.locator('button:has-text("Piattaforma"), div[role="tab"]:has-text("Piattaforma"), text="Piattaforma"').first
        if plat_tab.count() > 0:
            plat_tab.click()
            time.sleep(3)
            page.screenshot(path=str(PROJECT_ROOT / "meta" / "charts_platform_breakdown.png"))
            print("\n--- BREAKDOWN PIATTAFORMA ---")
            lines_plat = [l.strip() for l in page.locator("body").inner_text().splitlines() if l.strip()]
            for l in lines_plat[:40]:
                print(l)

    finally:
        context.close()

if __name__ == "__main__":
    run()

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

        # Clicca sull'icona grafici
        chart_icon = page.locator('div[role="toolbar"] [aria-label*="Grafic"], [aria-label*="Visualizza grafici"], div[class*="sideRail"] div[role="button"]').first
        if chart_icon.count() > 0:
            chart_icon.click()
            time.sleep(3)

        # Clicca pulsante Visualizza
        vis_btn = page.locator('button:has-text("Visualizza"), div[role="button"]:has-text("Visualizza")').first
        if vis_btn.count() > 0:
            print("Clicco su Visualizza...")
            vis_btn.click()
            time.sleep(3)
            page.screenshot(path=str(PROJECT_ROOT / "meta" / "chart_visualizza_clicked.png"))

        # Cambia metrica attiva da 'Risultati' a 'Importo speso' o 'Impression'
        metric_dd = page.locator('div[role="combobox"]:has-text("Risultati"), button:has-text("Risultati")').first
        if metric_dd.count() > 0:
            print("Apro dropdown metrica...")
            metric_dd.click()
            time.sleep(1)
            page.screenshot(path=str(PROJECT_ROOT / "meta" / "metric_dropdown_open.png"))
            opts = page.locator('div[role="option"], li[role="option"]').all()
            for o in opts:
                print("Metrica opzione:", o.inner_text().strip())

        # Stampa tutto il testo dentro il pannello dei grafici
        print("\n--- TESTO DETTAGLIATO PANNELLO PRESTAZIONI ---")
        lines = [l.strip() for l in page.locator("body").inner_text().splitlines() if l.strip()]
        for l in lines[:60]:
            print(l)

    finally:
        context.close()

if __name__ == "__main__":
    run()

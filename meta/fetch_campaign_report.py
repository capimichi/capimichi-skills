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

        # Clicca sull'icona dei grafici nella colonna stretta nera a destra (ha un grafico a barre)
        chart_icon = page.locator('div[role="toolbar"] [aria-label*="Grafic"], [aria-label*="Visualizza grafici"], div[class*="sideRail"] div[role="button"]').first
        print(f"Chart icon: {chart_icon.count()}")
        if chart_icon.count() > 0:
            chart_icon.click()
            time.sleep(5)
            page.screenshot(path=str(PROJECT_ROOT / "meta" / "charts_view.png"))

        # Ora naviga su Ads Reporting
        url_rep = f"https://adsmanager.facebook.com/adsreporting/?act={AD_ACCOUNT_ID}"
        print("Navigazione su Ads Reporting:", url_rep)
        page.goto(url_rep, wait_until="domcontentloaded")
        time.sleep(8)
        page.screenshot(path=str(PROJECT_ROOT / "meta" / "ads_reporting_page.png"))

        txt = page.locator("body").inner_text()
        print("\n--- TESTO ADS REPORTING ---")
        lines = [l.strip() for l in txt.splitlines() if l.strip()]
        for l in lines[:50]:
            print(l)

    finally:
        context.close()

if __name__ == "__main__":
    run()

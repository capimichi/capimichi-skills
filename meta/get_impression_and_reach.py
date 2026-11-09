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

        # Clicca Visualizza
        vis_btn = page.locator('button:has-text("Visualizza"), div[role="button"]:has-text("Visualizza")').first
        if vis_btn.count() > 0:
            vis_btn.click()
            time.sleep(2)

        # Clicca sul dropdown metrica e seleziona 'Impression'
        metric_dd = page.locator('div[role="combobox"]:has-text("Risultati"), button:has-text("Risultati")').first
        if metric_dd.count() > 0:
            metric_dd.click()
            time.sleep(1)
            imp_opt = page.locator('div[role="option"]:has-text("Impression"), li[role="option"]:has-text("Impression")').first
            if imp_opt.count() > 0:
                imp_opt.click()
                time.sleep(2)

        page.screenshot(path=str(PROJECT_ROOT / "meta" / "chart_impressions.png"))

        # Clicca sulla scheda Piattaforma
        plat_tab = page.locator('div[role="tab"]:has-text("Piattaforma"), button:has-text("Piattaforma")').first
        if plat_tab.count() > 0:
            plat_tab.click()
            time.sleep(2)
            page.screenshot(path=str(PROJECT_ROOT / "meta" / "chart_platform.png"))

        # Estrai testo grafico
        chart_box = page.locator('div[class*="chart"], div[class*="graph"], div[role="region"]').all()
        print("\n--- TESTO GRAFICI IMPRESSION E PIATTAFORMA ---")
        for b in chart_box:
            t = b.inner_text().strip()
            if t:
                print(t)

    finally:
        context.close()

if __name__ == "__main__":
    run()

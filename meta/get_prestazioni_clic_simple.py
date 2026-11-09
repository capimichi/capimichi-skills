import sys
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from meta.browser import launch_meta_browser

AD_ACCOUNT_ID = "1116925509636183"

def run():
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

        # Clicca sul dropdown 'Colonne'
        cols_btn = page.locator('div[role="button"]:has-text("Colonne"), button:has-text("Colonne")').first
        if cols_btn.count() > 0:
            print("Apro menu Colonne...")
            cols_btn.click()
            time.sleep(2)
            perf_opt = page.locator('text="Prestazioni e clic"').first
            if perf_opt.count() > 0:
                print("Seleziono 'Prestazioni e clic'...")
                perf_opt.click()
                time.sleep(4)

        page.screenshot(path=str(PROJECT_ROOT / "meta" / "exact_performance_and_clicks.png"))
        print("Screenshot salvato in meta/exact_performance_and_clicks.png")

        # Clicca anche sulla tab Gruppi di inserzioni e poi Inserzioni
        ads_tab = page.locator('div[role="tab"]:has-text("Inserzioni"), button:has-text("Inserzioni")').first
        if ads_tab.count() > 0:
            ads_tab.click()
            time.sleep(4)
            page.screenshot(path=str(PROJECT_ROOT / "meta" / "exact_ads_performance_and_clicks.png"))

    finally:
        context.close()

if __name__ == "__main__":
    run()

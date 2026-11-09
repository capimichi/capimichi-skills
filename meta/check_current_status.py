import sys
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from meta.browser import launch_meta_browser

AD_ACCOUNT_ID = "1116925509636183"
CAMPAIGN_ID = "120251426951480676"

def run():
    context = launch_meta_browser(headless=True, args=["--window-size=2000,1080"], viewport={"width": 2000, "height": 1080})
    page = context.pages[0] if context.pages else context.new_page()

    try:
        url = f"https://adsmanager.facebook.com/adsmanager/manage/ads?act={AD_ACCOUNT_ID}&selected_campaign_ids={CAMPAIGN_ID}"
        page.goto(url, wait_until="domcontentloaded")
        time.sleep(8)
        page.keyboard.press("Escape")
        time.sleep(1)

        # Tab Inserzioni
        page.locator('[role="tab"]:has-text("Inserz")').last.click()
        time.sleep(3)

        # Date picker -> Oggi
        date_btn = page.locator('button[aria-label*="Data"], div[role="button"]:has-text("ott"), button:has-text("ott"), button:has-text("Ultimi"), button:has-text("Intervallo")').first
        if date_btn.count() > 0:
            date_btn.click()
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
            time.sleep(3)

        page.screenshot(path="meta/check_1641_today.png")

        rows = page.locator('div[role="row"]').all()
        print("META ROWS TODAY:")
        for r in rows:
            txt = r.inner_text().strip().replace("\n", " | ")
            if any(k in txt for k in ["Nuova inserzione", "Inserzione B", "Risultati di"]):
                print(txt)

    finally:
        context.close()

if __name__ == "__main__":
    run()

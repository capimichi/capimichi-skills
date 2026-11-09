import sys
import time
import json
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
        date_btn = page.locator('button[aria-label*="Data"], div[role="button"]:has-text("ott"), button:has-text("ott"), button:has-text("Ultimi")').first
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

        # Seleziona Colonne -> Prestazioni e clic
        col_btn = page.locator('button:has-text("Colonne"), div[role="button"]:has-text("Colonne")').first
        if col_btn.count() > 0:
            col_btn.click()
            time.sleep(2)
            perf_opt = page.locator(':text("Prestazioni e clic")').first
            if perf_opt.count() > 0:
                perf_opt.click()
                time.sleep(4)

        page.screenshot(path="meta/perf_clicks_today.png")

        # Dump text
        raw_text = page.locator('body').inner_text()
        with open("meta/perf_today_dump.txt", "w", encoding="utf-8") as f:
            f.write(raw_text)

        # Date picker -> Dall'inizio (Lifetime)
        date_btn = page.locator('button[aria-label*="Data"], div[role="button"]:has-text("Oggi"), button:has-text("Oggi")').first
        if date_btn.count() > 0:
            date_btn.click()
            time.sleep(2)
            max_label = page.locator('label:has-text("Dall\'inizio"), :text("Dall\'inizio"), label:has-text("Massimo")').first
            if max_label.count() > 0:
                max_label.click()
                time.sleep(1)
            agg_btn = page.locator('button:has-text("Aggiorna")').last
            if agg_btn.count() > 0:
                agg_btn.click()
                time.sleep(5)

        page.screenshot(path="meta/perf_clicks_lifetime.png")
        raw_text_life = page.locator('body').inner_text()
        with open("meta/perf_lifetime_dump.txt", "w", encoding="utf-8") as f:
            f.write(raw_text_life)

    finally:
        context.close()

if __name__ == "__main__":
    run()

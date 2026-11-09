import sys
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from meta.browser import launch_meta_browser
from worldfilia.browser import launch_worldfilia_browser

AD_ACCOUNT_ID = "1116925509636183"
CAMPAIGN_ID = "120251426951480676"

def get_meta_stats():
    print("=== META ADS CHECK ===")
    context = launch_meta_browser(headless=True, args=["--window-size=2000,1080"], viewport={"width": 2000, "height": 1080})
    page = context.pages[0] if context.pages else context.new_page()

    try:
        url = f"https://adsmanager.facebook.com/adsmanager/manage/ads?act={AD_ACCOUNT_ID}&selected_campaign_ids={CAMPAIGN_ID}"
        page.goto(url, wait_until="domcontentloaded")
        time.sleep(8)
        page.keyboard.press("Escape")
        time.sleep(1)

        # Go to Inserzioni tab
        tab = page.locator('[role="tab"]:has-text("Inserz")').last
        if tab.count() > 0:
            tab.click()
            time.sleep(3)

        # Set preset to Prestazioni e clic if possible
        col_btn = page.locator('button:has-text("Colonne"), div[role="button"]:has-text("Colonne")').first
        if col_btn.count() > 0:
            col_btn.click()
            time.sleep(2)
            perf_opt = page.locator(':text("Prestazioni e clic")').first
            if perf_opt.count() > 0:
                perf_opt.click()
                time.sleep(3)

        # 1. OGGI
        date_btn = page.locator('button[aria-label*="Data"], div[role="button"]:has-text("ott"), button:has-text("ott"), button:has-text("Ultimi"), button:has-text("Intervallo"), button:has-text("Oggi")').first
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

        page.screenshot(path="meta/now_today.png")
        body_today = page.locator('body').inner_text()
        with open("meta/now_today.txt", "w", encoding="utf-8") as f:
            f.write(body_today)
        print("Captured Today stats and saved meta/now_today.png")

        # 2. LIFETIME (Dall'inizio)
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

        ref = page.locator('[aria-label="Aggiorna dati tabella"]').first
        if ref.count() > 0:
            ref.click()
            time.sleep(3)

        page.screenshot(path="meta/now_lifetime.png")
        body_lifetime = page.locator('body').inner_text()
        with open("meta/now_lifetime.txt", "w", encoding="utf-8") as f:
            f.write(body_lifetime)
        print("Captured Lifetime stats and saved meta/now_lifetime.png")

    except Exception as e:
        print("Error in meta check:", e)
    finally:
        context.close()

def get_worldfilia_stats():
    print("\n=== WORLDFILIA CHECK ===")
    context = launch_worldfilia_browser(headless=True)
    page = context.pages[0] if context.pages else context.new_page()

    try:
        page.goto("https://portal.worldfilia.net/publisher", wait_until="networkidle")
        time.sleep(4)
        page.screenshot(path="worldfilia/now_dashboard.png")
        wf_text = page.locator("body").inner_text()
        with open("worldfilia/now_dashboard.txt", "w", encoding="utf-8") as f:
            f.write(wf_text)
        print("Captured Worldfilia dashboard")
    except Exception as e:
        print("Error in worldfilia check:", e)
    finally:
        context.close()

if __name__ == "__main__":
    get_meta_stats()
    get_worldfilia_stats()

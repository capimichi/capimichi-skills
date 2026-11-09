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

def check_meta():
    print("=" * 60)
    print("1. CONTROLLO META ADS (20 OTTOBRE)")
    print("=" * 60)
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

        # A) OGGI (20 Ottobre)
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

        page.screenshot(path="meta/morning_20oct_today.png")
        print("Screenshot Oggi salvato in meta/morning_20oct_today.png")

        # B) IERI (19 Ottobre)
        if date_btn.count() > 0:
            date_btn.click()
            time.sleep(2)
            ieri_label = page.locator('label:has-text("Ieri"), :text-is("Ieri")').first
            if ieri_label.count() > 0:
                ieri_label.click()
                time.sleep(1)
            agg_btn = page.locator('button:has-text("Aggiorna")').last
            if agg_btn.count() > 0:
                agg_btn.click()
                time.sleep(5)

        page.screenshot(path="meta/morning_19oct_yesterday.png")
        print("Screenshot Ieri salvato in meta/morning_19oct_yesterday.png")

        # C) DALL'INIZIO (Lifetime)
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

        page.screenshot(path="meta/morning_lifetime.png")
        print("Screenshot Lifetime salvato in meta/morning_lifetime.png")

    finally:
        context.close()

def check_worldfilia():
    print("\n" + "=" * 60)
    print("2. CONTROLLO WORLDFILIA")
    print("=" * 60)
    context = launch_worldfilia_browser(headless=True)
    page = context.pages[0] if context.pages else context.new_page()

    try:
        page.goto("https://portal.worldfilia.net/publisher", wait_until="networkidle")
        time.sleep(3)
        page.screenshot(path="worldfilia/morning_20oct_dashboard.png")
        text = page.locator("main, #app, body").first.inner_text()
        print("WORLDFILIA DASHBOARD SNIPPET:")
        print(text[:1200])
    finally:
        context.close()

def main():
    check_meta()
    check_worldfilia()

if __name__ == "__main__":
    main()

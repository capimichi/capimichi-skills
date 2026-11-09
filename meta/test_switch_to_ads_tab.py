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
    context = launch_meta_browser(
        headless=True,
        args=["--window-size=2000,1080"],
        viewport={"width": 2000, "height": 1080}
    )
    page = context.pages[0] if context.pages else context.new_page()

    try:
        url = f"https://adsmanager.facebook.com/adsmanager/manage/ads?act={AD_ACCOUNT_ID}&selected_campaign_ids={CAMPAIGN_ID}"
        print(f"Navigo a: {url}")
        page.goto(url, wait_until="domcontentloaded")
        time.sleep(6)
        page.keyboard.press("Escape")
        time.sleep(1)

        # Clicca tab Inserzioni
        ads_tab = page.locator('[role="tab"]:has-text("Inserz")').last
        print("Clicco su tab Inserzioni...")
        ads_tab.click()
        time.sleep(4)

        page.screenshot(path=str(PROJECT_ROOT / "meta" / "verified_ads_tab.png"))
        print("Screenshot salvato in meta/verified_ads_tab.png")

        # Cerca la bozza Ad B
        draft_row = page.locator('div[role="row"]:has-text("In bozza")').first
        print("Riga in bozza trovata:", draft_row.count() > 0)
        if draft_row.count() > 0:
            print("Hover sulla riga in bozza...")
            draft_row.hover()
            time.sleep(1)
            # Clicca la checkbox della bozza
            chk = draft_row.locator('input[type="checkbox"]').first
            if chk.count() > 0:
                print("Seleziono checkbox riga...")
                chk.click(force=True)
                time.sleep(1)

            # Clicca Modifica nella toolbar
            mod_btn = page.locator('div[role="toolbar"] button:has-text("Modifica"), div[role="toolbar"] div[role="button"]:has-text("Modifica")').first
            print("Modifica toolbar enabled:", mod_btn.is_enabled())
            if mod_btn.count() > 0:
                mod_btn.click()
                time.sleep(6)

        page.screenshot(path=str(PROJECT_ROOT / "meta" / "verified_editor_open.png"))
        print("Screenshot salvato in meta/verified_editor_open.png")

    finally:
        context.close()

if __name__ == "__main__":
    run()

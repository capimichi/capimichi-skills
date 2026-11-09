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
        page.goto(url, wait_until="domcontentloaded")
        time.sleep(8)
        page.keyboard.press("Escape")
        time.sleep(2)

        page.locator('[role="tab"]:has-text("Inserz")').last.click()
        time.sleep(2)

        page.locator(':text("Inserzione B - Offerta COD"), :text("Inserzione senza nome"), :text("In bozza")').first.click()
        time.sleep(2)

        page.locator('div[role="toolbar"] button:has-text("Modifica"), div[role="toolbar"] div[role="button"]:has-text("Modifica")').first.click()
        time.sleep(6)

        # Scroll con JS
        add_btn = page.locator('div[role="button"]:has-text("Aggiungi contenuto multimediale")').first
        print("Trovato add_btn:", add_btn.count() > 0)
        if add_btn.count() > 0:
            add_btn.evaluate('el => el.scrollIntoView({behavior: "instant", block: "center"})')
            time.sleep(2)
            page.screenshot(path=str(PROJECT_ROOT / "meta" / "scrolled_into_center.png"))
            print("Screenshot in meta/scrolled_into_center.png")
            add_btn.click()
            time.sleep(2)
            page.screenshot(path=str(PROJECT_ROOT / "meta" / "menu_open_success.png"))
            print("Menu aperto!")

    finally:
        context.close()

if __name__ == "__main__":
    run()

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
        args=["--window-size=1600,1000"],
        viewport={"width": 1600, "height": 1000}
    )
    page = context.pages[0] if context.pages else context.new_page()

    try:
        url = f"https://adsmanager.facebook.com/adsmanager/manage/ads?act={AD_ACCOUNT_ID}&selected_campaign_ids=120251426951480676"
        page.goto(url, wait_until="domcontentloaded")
        time.sleep(5)
        page.keyboard.press("Escape")
        time.sleep(1)

        # Cerca bottone Dettagli
        dettagli_btn = page.locator('button:has-text("Dettagli"), div[role="button"]:has-text("Dettagli")').first
        if dettagli_btn.count() > 0:
            dettagli_btn.click()
            time.sleep(2)
            page.screenshot(path=str(PROJECT_ROOT / "meta" / "dettagli_dropdown_menu.png"))
            print("Screenshot salvato in meta/dettagli_dropdown_menu.png")

            menu_text = page.locator('div[role="menu"]').inner_text()
            print("--- MENU DETTAGLI ---")
            print(menu_text)
        else:
            print("Bottone Dettagli non trovato")

    finally:
        context.close()

if __name__ == "__main__":
    run()

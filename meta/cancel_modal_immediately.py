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
        time.sleep(5)
        page.keyboard.press("Escape")
        time.sleep(1)

        # Se c'è il dialog elimina, clicca Annulla
        annulla = page.locator('button:has-text("Annulla")').first
        if annulla.count() > 0 and annulla.is_visible():
            print("Clicco Annulla sul dialog...")
            annulla.click()
            time.sleep(2)

        page.screenshot(path=str(PROJECT_ROOT / "meta" / "safe_table_state.png"))
        print("Screenshot salvato in meta/safe_table_state.png")

    finally:
        context.close()

if __name__ == "__main__":
    run()

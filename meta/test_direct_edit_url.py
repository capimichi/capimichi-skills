import sys
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from meta.browser import launch_meta_browser

AD_ACCOUNT_ID = "1116925509636183"
CAMPAIGN_ID = "120251426951480676"
AD_ID = "120235333037980341"

DIRECT_EDIT_URL = f"https://adsmanager.facebook.com/adsmanager/manage/ads/edit?act={AD_ACCOUNT_ID}&selected_campaign_ids={CAMPAIGN_ID}&selected_ad_ids={AD_ID}"

def run():
    context = launch_meta_browser(headless=False)
    page = context.pages[0] if context.pages else context.new_page()

    try:
        print(f"Navigazione diretta a: {DIRECT_EDIT_URL}")
        page.goto(DIRECT_EDIT_URL, wait_until="networkidle")
        time.sleep(6)

        page.screenshot(path=str(PROJECT_ROOT / "meta" / "direct_editor_loaded.png"))
        print("Screenshot salvato in meta/direct_editor_loaded.png")

        # Stampa tutti i combobox presenti
        combos = page.locator('div[role="combobox"]').all()
        print(f"Combobox trovati: {len(combos)}")
        for idx, c in enumerate(combos):
            print(f"Combobox {idx}: {c.inner_text().strip().replace(chr(10), ' ')}")

    finally:
        context.close()

if __name__ == "__main__":
    run()

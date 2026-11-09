import sys
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from meta.paths import get_cache_dir
from meta.browser import launch_meta_browser

AD_ACCOUNT_ID = "1116925509636183"

def run():
    cache_dir = get_cache_dir()
    context = launch_meta_browser(headless=True)
    page = context.pages[0] if context.pages else context.new_page()

    try:
        url = f"https://adsmanager.facebook.com/adsmanager/manage/ads?act={AD_ACCOUNT_ID}"
        page.goto(url, wait_until="networkidle")
        time.sleep(5)

        # Assicurati data "Oggi"
        date_picker = page.locator('button:has-text("17 set"), button:has-text("Ultimi"), button:has-text("Oggi"), div[role="button"]:has-text("Oggi")').first
        if date_picker.count() > 0:
            date_picker.click()
            time.sleep(1)
            oggi = page.locator('text="Oggi"').first
            if oggi.count() > 0:
                oggi.click()
                time.sleep(3)

        table_container = page.locator('div[role="grid"]').first
        if table_container.count() > 0:
            rows = table_container.locator('[role="row"]').all()
            print(f"Table rows in ads grid: {len(rows)}")
            for idx, r in enumerate(rows):
                print(f"Ad R[{idx}]: {r.inner_text().strip().replace(chr(10), ' | ')}")

    finally:
        context.close()

if __name__ == "__main__":
    run()

import sys
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from meta.browser import launch_meta_browser

AD_ACCOUNT_ID = "1116925509636183"

def run():
    context = launch_meta_browser(headless=True)
    page = context.pages[0] if context.pages else context.new_page()

    try:
        url = f"https://adsmanager.facebook.com/adsmanager/billing_hub/payment_activity?asset_id={AD_ACCOUNT_ID}"
        page.goto(url, wait_until="domcontentloaded")
        time.sleep(6)

        page.mouse.wheel(0, 500)
        time.sleep(3)

        page.screenshot(path=str(PROJECT_ROOT / "meta" / "transactions_scrolled.png"))

        rows = page.locator('div[role="row"], table tr').all()
        print(f"Righe transazione trovate: {len(rows)}")
        for idx, r in enumerate(rows):
            print(f"[{idx}]: {r.inner_text().strip().replace('\n', ' | ')}")

    finally:
        context.close()

if __name__ == "__main__":
    run()

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
        url = f"https://adsmanager.facebook.com/adsmanager/billing_hub/payment_settings?asset_id={AD_ACCOUNT_ID}"
        page.goto(url, wait_until="domcontentloaded")
        time.sleep(6)

        page.screenshot(path=str(PROJECT_ROOT / "meta" / "billing_error_detail.png"))

        txt = page.locator("body").inner_text()
        print("\n--- DETTAGLI FATTURAZIONE E PAGAMENTO ---")
        lines = [l.strip() for l in txt.splitlines() if l.strip()]
        for l in lines[:50]:
            print(l)

    finally:
        context.close()

if __name__ == "__main__":
    run()

import sys
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from meta.paths import get_cache_dir
from meta.browser import launch_meta_browser

AD_ACCOUNT_ID = "1116925509636183"

def inspect():
    cache_dir = get_cache_dir()
    context = launch_meta_browser(headless=True)
    page = context.pages[0] if context.pages else context.new_page()

    try:
        url = f"https://adsmanager.facebook.com/adsmanager/manage/campaigns?act={AD_ACCOUNT_ID}"
        page.goto(url, wait_until="networkidle")
        time.sleep(5)

        # Print all text in the table
        print("=== CAMPAGNE ===")
        rows = page.locator('div[role="row"]').all()
        for i, r in enumerate(rows):
            print(f"Row {i}: {r.inner_text().strip().replace(chr(10), ' | ')}")

        # Click on "Controlla e pubblica (3)" or hover on "Errore dell'inserzione" to see what it is
        error_badge = page.locator('text="Errore dell\'inserzione"').first
        if error_badge.count() > 0:
            print("Found error badge, hovering...")
            error_badge.hover()
            time.sleep(2)
            shot_err = cache_dir / "error_hover.png"
            page.screenshot(path=str(shot_err))
            print(f"Error hover screenshot: {shot_err}")

        # Let's check what Controlla e pubblica has
        review_btn = page.locator('button:has-text("Controlla e pubblica")').first
        if review_btn.count() > 0:
            print(f"Review button text: {review_btn.inner_text()}")
            review_btn.click()
            time.sleep(3)
            shot_review = cache_dir / "review_dialog.png"
            page.screenshot(path=str(shot_review))
            print(f"Review dialog screenshot: {shot_review}")
            dialog_text = page.locator('div[role="dialog"]').inner_text()
            print("Dialog text:\n", dialog_text)

    finally:
        context.close()

if __name__ == "__main__":
    inspect()

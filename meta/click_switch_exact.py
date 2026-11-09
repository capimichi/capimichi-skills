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
        url = f"https://adsmanager.facebook.com/adsmanager/manage/campaigns?act={AD_ACCOUNT_ID}"
        page.goto(url, wait_until="networkidle")
        time.sleep(5)

        # Cerca il testo Rikrestin
        cell = page.locator('text="Rikrestin 2x49 - Test Vendite"').first
        box = cell.bounding_box()
        print(f"Rikrestin text box: {box}")

        # The toggle switch is horizontally centered around x = 145, y = box['y'] + 9
        target_x = 145.0
        target_y = box['y'] + (box['height'] / 2)
        print(f"Clicking toggle switch at ({target_x}, {target_y})...")

        page.mouse.click(target_x, target_y)
        time.sleep(4)

        shot = cache_dir / "campaign_switch_clicked.png"
        page.screenshot(path=str(shot))
        print(f"Screenshot saved to {shot}")

        # Controlla testo riga
        row = page.locator('div[role="row"]:has-text("Rikrestin")').first
        print("Testo riga dopo il click:", row.inner_text().replace('\n', ' | '))

    finally:
        context.close()

if __name__ == "__main__":
    run()

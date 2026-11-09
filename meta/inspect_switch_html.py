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

        # The toggle switch is to the left of the text (in column 'No/Sì')
        # Let's inspect all elements near that Y coordinate
        # The switch has x coordinate around 145, y coordinate matching the row (~680)
        # Let's find all input/role=checkbox/role=switch
        switches = page.locator('input[type="checkbox"]').all()
        print(f"Total checkboxes/switches: {len(switches)}")
        for idx, s in enumerate(switches):
            sbox = s.bounding_box()
            print(f"Switch {idx}: box={sbox}, aria-label={s.get_attribute('aria-label')}, aria-checked={s.get_attribute('aria-checked')}")

        # Also let's find elements with class or role switch
        all_roles = page.locator('[role="switch"], [data-testid*="switch"], [data-testid*="toggle"]').all()
        print(f"Elements with role=switch: {len(all_roles)}")
        for idx, r in enumerate(all_roles):
            print(f"Role {idx}: box={r.bounding_box()}, checked={r.get_attribute('aria-checked')}")

    finally:
        context.close()

if __name__ == "__main__":
    run()

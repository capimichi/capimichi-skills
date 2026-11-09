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
        time.sleep(6)

        # Let's see what links or text are in the table body
        # Specifically search for "Rikrestin"
        rik = page.locator('text="Rikrestin"').all()
        print(f"Elements matching 'Rikrestin': {len(rik)}")
        for r in rik:
            print("Rikrestin elem:", r.inner_text())

        # Let's inspect all grid cells or row elements
        grid = page.locator('[role="grid"], [role="table"]').first
        if grid.count() > 0:
            print("Grid found!")
            print(grid.inner_text()[:1500])

        # Let's check the draft:
        # What is "Nuova campagna Vendite"?
        print("\nChecking drafts/errors...")
        err = page.locator('text="Errore dell\'inserzione"').all()
        print(f"Error badges: {len(err)}")

        # Check button Controlla e pubblica
        btn = page.locator('button:has-text("Controlla e pubblica")').first
        if btn.count() > 0:
            print(f"Controlla e pubblica button: {btn.inner_text()}")

    finally:
        context.close()

if __name__ == "__main__":
    run()

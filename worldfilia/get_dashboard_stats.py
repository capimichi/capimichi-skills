import sys
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from worldfilia.paths import get_cache_dir
from worldfilia.browser import launch_worldfilia_browser

def run():
    cache_dir = get_cache_dir()
    context = launch_worldfilia_browser(headless=True)
    page = context.pages[0] if context.pages else context.new_page()

    try:
        page.goto("https://portal.worldfilia.net/publisher", wait_until="networkidle")
        time.sleep(3)

        shot = cache_dir / "worldfilia_today_dashboard.png"
        page.screenshot(path=str(shot), full_page=True)
        print("Worldfilia dashboard screenshot saved:", shot)

        # Print all visible text on dashboard
        body = page.locator('main, #app, body').first
        print(body.inner_text()[:2000])

    finally:
        context.close()

if __name__ == "__main__":
    run()

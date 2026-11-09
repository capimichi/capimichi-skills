import sys
import time
from pathlib import Path
from bs4 import BeautifulSoup

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from meta.paths import get_cache_dir
from meta.browser import launch_meta_browser

AD_ACCOUNT_ID = "1116925509636183"
EVENTS_MANAGER_URL = f"https://business.facebook.com/events_manager2/list/dataset?act={AD_ACCOUNT_ID}"

def inspect_pixels(headless: bool = True):
    cache_dir = get_cache_dir()
    print("=" * 60)
    print("ISPEZIONE PIXEL / DATASET META EVENTS MANAGER")
    print(f"Ad Account ID: {AD_ACCOUNT_ID}")
    print("=" * 60)

    context = launch_meta_browser(headless=headless)
    page = context.pages[0] if context.pages else context.new_page()

    try:
        print(f"Navigazione a: {EVENTS_MANAGER_URL}")
        page.goto(EVENTS_MANAGER_URL, wait_until="domcontentloaded")
        print("Attendo caricamento Events Manager...")
        time.sleep(8)

        print(f"URL Corrente: {page.url}")
        screenshot_path = cache_dir / "meta_events_manager.png"
        page.screenshot(path=str(screenshot_path))
        print(f"Screenshot salvato: {screenshot_path}")

        html_path = cache_dir / "meta_events_manager.html"
        html_path.write_text(page.content(), encoding="utf-8")

        body_text = page.inner_text("body")
        print("\n--- ANALISI TESTUALE EVENTS MANAGER ---")
        lines = [line.strip() for line in body_text.splitlines() if line.strip()]
        
        keywords = ["dataset", "pixel", "id", "collega", "origini", "dati", "crea", "nessun", "evento"]
        relevant_lines = []
        for line in lines:
            if any(kw in line.lower() for kw in keywords):
                if line not in relevant_lines:
                    relevant_lines.append(line)

        for line in relevant_lines[:30]:
            print(f"- {line}")

    except Exception as e:
        print(f"Errore durante l'ispezione pixel: {e}")
    finally:
        context.close()

if __name__ == "__main__":
    is_headless = "--no-headless" not in sys.argv
    inspect_pixels(headless=is_headless)

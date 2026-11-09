import sys
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from meta.paths import get_browser_session_dir, get_cache_dir
from meta.browser import launch_meta_browser

BM_URL = "https://business.facebook.com/latest/home"

def explore(headless: bool = False):
    cache_dir = get_cache_dir()
    print("=" * 60)
    print("META BUSINESS SUITE - ESPLORAZIONE SESSIONE")
    print("=" * 60)
    print(f"Sessione da: {get_browser_session_dir()}")
    print(f"Cache/Debug in: {cache_dir}")
    print(f"Navigazione verso: {BM_URL}")

    context = launch_meta_browser(headless=headless)
    page = context.pages[0] if context.pages else context.new_page()

    try:
        page.goto(BM_URL, wait_until="domcontentloaded")
        time.sleep(5)  # Meta Business Suite è una SPA pesante

        current_url = page.url
        title = page.title()
        print(f"\n[INFO PAGINA]")
        print(f"URL Corrente: {current_url}")
        print(f"Titolo: {title}")

        # Salva screenshot e HTML di debug
        screenshot_path = cache_dir / "meta_explore.png"
        html_path = cache_dir / "meta_explore.html"
        page.screenshot(path=str(screenshot_path))
        html_path.write_text(page.content(), encoding="utf-8")
        print(f"Screenshot salvato in: {screenshot_path}")
        print(f"Sorgente HTML salvato in: {html_path}")

        if not headless:
            print("\nBrowser aperto. Premi [INVIO] per chiudere...")
            try:
                input()
            except (KeyboardInterrupt, EOFError):
                pass
    finally:
        context.close()
        print("Browser chiuso.")

if __name__ == "__main__":
    is_headless = "--headless" in sys.argv
    explore(headless=is_headless)

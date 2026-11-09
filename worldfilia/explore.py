import sys
import time
from pathlib import Path

# Assicura che la root del progetto sia nel sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from worldfilia.paths import get_browser_session_dir, get_cache_dir
from worldfilia.browser import launch_worldfilia_browser

DASHBOARD_URL = "https://portal.worldfilia.net/"

def explore(headless: bool = False):
    cache_dir = get_cache_dir()
    print("=" * 60)
    print("WORLDFILIA - ESPLORAZIONE SESSIONE & DASHBOARD")
    print("=" * 60)
    print(f"Sessione da: {get_browser_session_dir()}")
    print(f"Cache/Debug in: {cache_dir}")
    print(f"Navigazione verso: {DASHBOARD_URL}")

    context = launch_worldfilia_browser(headless=headless)
    page = context.pages[0] if context.pages else context.new_page()

    try:
        page.goto(DASHBOARD_URL, wait_until="domcontentloaded")
        time.sleep(3)  # Attesa assestamento SPA/interfaccia

        current_url = page.url
        title = page.title()
        print(f"\n[INFO PAGINA]")
        print(f"URL Corrente: {current_url}")
        print(f"Titolo: {title}")

        # Screenshot di debug salvato nella cache XDG
        screenshot_path = cache_dir / "dashboard_explore.png"
        page.screenshot(path=str(screenshot_path))
        print(f"Screenshot salvato in: {screenshot_path}")

        # Dump HTML per analisi selettori
        html_path = cache_dir / "dashboard_explore.html"
        html_path.write_text(page.content(), encoding="utf-8")
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

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

        # 1. Clicca sulla riga della conversione 18/10 21:47
        conv_row = page.locator('text="18/10 21:47"').first
        if conv_row.count() > 0:
            print("Clicco su conversione 18/10 21:47...")
            conv_row.click()
            time.sleep(3)
            page.screenshot(path=str(cache_dir / "conversion_modal_detail.png"))
            print("Modal conversione salvato:", cache_dir / "conversion_modal_detail.png")
            modal_text = page.locator('div[role="dialog"], .modal, body').inner_text()
            print("\n--- DETTAGLIO LEAD ---")
            print(modal_text[:1500])

        # Chiudi modal
        page.keyboard.press("Escape")
        time.sleep(1)

        # 2. Cambia data su Ieri nel dropdown
        date_dd = page.locator('button:has-text("Oggi"), div:has-text("Oggi")').first
        # Sulla dashboard, 'Oggi' con la freccetta
        oggi_btn = page.locator(':text-is("Oggi")').first
        if oggi_btn.count() > 0:
            print("Apro dropdown data dashboard...")
            oggi_btn.click()
            time.sleep(1)
            ieri = page.locator(':text-is("Ieri")').first
            if ieri.count() > 0:
                print("Seleziono Ieri...")
                ieri.click()
                time.sleep(3)
                page.screenshot(path=str(cache_dir / "worldfilia_yesterday_dashboard.png"))
                print("Dashboard Ieri salvata")
                txt_ieri = page.locator('main, #app, body').first.inner_text()
                print("\n--- STATISTICHE IERI WORLDFILIA ---")
                print(txt_ieri[:1500])

    finally:
        context.close()

if __name__ == "__main__":
    run()

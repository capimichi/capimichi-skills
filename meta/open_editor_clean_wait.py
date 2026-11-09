import sys
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from meta.browser import launch_meta_browser

AD_ACCOUNT_ID = "1116925509636183"
CAMPAIGN_ID = "120251426951480676"

def run():
    context = launch_meta_browser(
        headless=True,
        args=["--window-size=2000,1080"],
        viewport={"width": 2000, "height": 1080}
    )
    page = context.pages[0] if context.pages else context.new_page()

    try:
        url = f"https://adsmanager.facebook.com/adsmanager/manage/ads?act={AD_ACCOUNT_ID}&selected_campaign_ids={CAMPAIGN_ID}"
        print(f"Navigo a: {url}")
        page.goto(url, wait_until="domcontentloaded")

        print("Attendo sparizione del caricamento...")
        try:
            page.locator('text="Caricamento in corso..."').wait_for(state="detached", timeout=25000)
            print("Caricamento terminato!")
        except Exception as e:
            print("Timeout attesa caricamento:", e)

        time.sleep(3)
        page.keyboard.press("Escape")
        time.sleep(1)

        # Cerca la riga della bozza
        cell = page.locator(':has-text("Copia")').first
        print(f"Cella Copia trovata: {cell.count() > 0}")
        if cell.count() > 0:
            print("Hovering su riga Copia...")
            cell.hover()
            time.sleep(1)
            page.screenshot(path=str(PROJECT_ROOT / "meta" / "row_hovered.png"))

            # Trova bottoni dentro o vicino alla riga
            row = cell.locator('xpath=ancestor::div[@role="row"]')
            mod_btn = row.locator('text="Modifica"').first
            if mod_btn.count() > 0:
                print("Trovato Modifica nella riga! Clicco...")
                mod_btn.click()
            else:
                print("Modifica nella riga non trovato, clicco direttamente sulla cella...")
                cell.click()

            time.sleep(6)
            page.screenshot(path=str(PROJECT_ROOT / "meta" / "editor_opened_result.png"))
            print("Screenshot salvato in meta/editor_opened_result.png")

    finally:
        context.close()

if __name__ == "__main__":
    run()

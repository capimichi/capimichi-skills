import sys
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from meta.browser import launch_meta_browser

AD_ACCOUNT_ID = "1116925509636183"

def run():
    context = launch_meta_browser(headless=False)
    page = context.pages[0] if context.pages else context.new_page()

    try:
        url = f"https://adsmanager.facebook.com/adsmanager/manage/campaigns?act={AD_ACCOUNT_ID}"
        page.goto(url, wait_until="networkidle")
        time.sleep(5)

        # 1. Chiudi Crea visualizzazione se c'è
        page.mouse.click(908, 423)
        time.sleep(1)

        # 2. Clicca sulla tab Inserzioni: Elementi selezionati o tab Inserzioni
        ads_tab = page.locator('[role="tab"]:has-text("Inserz")').last
        if ads_tab.count() > 0:
            ads_tab.click()
            time.sleep(3)

        # 3. Clicca sull'icona della matita (Modifica) a x=244, y=424
        print("Clicco icona matita Modifica a (244, 424)...")
        page.mouse.click(244, 424)
        time.sleep(5)

        page.screenshot(path=str(PROJECT_ROOT / "meta" / "pencil_edit_result.png"))
        print("Screenshot salvato in meta/pencil_edit_result.png")

        # Stampa testi degli elementi principali
        txts = page.locator('text="Usa post esistente", text="Crea inserzione", text="Configurazione dell\'inserzione"').all()
        print(f"Match trovati: {len(txts)}")
        for t in txts:
            print("Found:", t.inner_text())

    finally:
        context.close()

if __name__ == "__main__":
    run()

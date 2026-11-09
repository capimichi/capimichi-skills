import sys
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from meta.browser import launch_meta_browser

AD_ACCOUNT_ID = "1116925509636183"

def run():
    context = launch_meta_browser(headless=True)
    page = context.pages[0] if context.pages else context.new_page()

    try:
        url = f"https://adsmanager.facebook.com/adsmanager/manage/campaigns?act={AD_ACCOUNT_ID}"
        print(f"Navigazione a: {url}")
        page.goto(url, wait_until="domcontentloaded")
        time.sleep(5)

        # Clicca sulla campagna Rikrestin
        print("Click campagna...")
        page.locator('text="Rikrestin 2x49 - Test Vendite"').first.click()
        time.sleep(3)

        # Clicca esattamente sul testo 'Inserzioni per 1 Campagna'
        print("Click Inserzioni per 1 Campagna...")
        page.locator('text="Inserzioni per 1 Campagna"').first.click()
        time.sleep(4)

        page.screenshot(path=str(PROJECT_ROOT / "meta" / "ad_tab_clicked.png"))
        print("Screenshot tab inserzioni salvato")

        # Clicca su Modifica della riga
        edit_pencil_btn = page.locator('button:has-text("Modifica")').first
        if edit_pencil_btn.count() > 0:
            print("Click Modifica...")
            edit_pencil_btn.click()
            time.sleep(6)
        else:
            # Alternativa: clicca sull'icona a matita a destra (pannello laterale di modifica)
            print("Cerco icona matita nella barra laterale destra...")
            # La matita nella barra nera a destra
            pencil = page.locator('div[role="button"][aria-label*="Modifica"]').first
            if pencil.count() > 0:
                pencil.click()
                time.sleep(6)

        page.screenshot(path=str(PROJECT_ROOT / "meta" / "ad_editor_content.png"))
        print("Screenshot editor salvato")

        # Leggiamo tutto il testo della pagina
        text = page.locator('body').inner_text()
        with open(PROJECT_ROOT / "meta" / "editor_page_text.txt", "w", encoding="utf-8") as f:
            f.write(text)

        print(f"Testo salvato in meta/editor_page_text.txt ({len(text)} caratteri)")

    finally:
        context.close()

if __name__ == "__main__":
    run()

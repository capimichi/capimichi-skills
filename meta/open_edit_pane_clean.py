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
        url = f"https://adsmanager.facebook.com/adsmanager/manage/ads?act={AD_ACCOUNT_ID}"
        page.goto(url, wait_until="networkidle")
        time.sleep(5)

        # 1. Chiudi 'Crea visualizzazione' se aperto
        close_x = page.locator('div:has-text("Crea visualizzazione") button[aria-label="Chiudi"]').first
        if close_x.count() > 0:
            print("Chiudo drawer 'Crea visualizzazione'...")
            close_x.click()
            time.sleep(2)

        # 2. Seleziona la riga inserzione
        chk = page.locator('div[role="row"] input[type="checkbox"]').all()
        print(f"Checkboxes trovate: {len(chk)}")
        if len(chk) >= 2:
            chk[1].click(force=True)
            time.sleep(1)

        # 3. Clicca Modifica
        mod = page.locator('button:has-text("Modifica"), div[role="button"]:has-text("Modifica")').filter(has_text="Modifica").first
        if mod.count() > 0:
            print("Click su Modifica...")
            mod.click()
            time.sleep(5)

        page.screenshot(path="meta/edit_pane_verified.png")
        print("Screenshot salvato in meta/edit_pane_verified.png")

        # Stampa tutti i testi visibili nel pannello di destra
        editor = page.locator('div[role="region"], form, div[data-testid*="editor"]').all()
        print(f"Regioni editor: {len(editor)}")

    finally:
        context.close()

if __name__ == "__main__":
    run()

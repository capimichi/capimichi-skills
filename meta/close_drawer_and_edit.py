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
        url = f"https://adsmanager.facebook.com/adsmanager/manage/ads?act={AD_ACCOUNT_ID}&selected_campaign_ids=120251426951480676&treenav=true"
        print(f"Navigazione a: {url}")
        page.goto(url, wait_until="networkidle")
        time.sleep(5)

        # Clicca sulla X di Crea visualizzazione esattamente alle sue coordinate
        print("Chiudo drawer con click su (908, 423)...")
        page.mouse.click(908, 423)
        time.sleep(2)

        # Se ancora c'è 'Crea visualizzazione', premi Escape
        page.keyboard.press("Escape")
        time.sleep(1)

        # Ora seleziona la checkbox della riga inserzione
        # La checkbox è a x=80, y=630
        print("Seleziono riga inserzione...")
        chk = page.locator('div[role="row"]').nth(1).locator('input[type="checkbox"]').first
        if chk.count() > 0:
            chk.click(force=True)
            time.sleep(1)

        # Clicca Modifica nella toolbar in alto
        mod_btn = page.locator('button:has-text("Modifica")').first
        print("Clicco Modifica...")
        mod_btn.click()
        time.sleep(5)

        page.screenshot(path="meta/real_editor_unlocked.png")
        print("Screenshot salvato in meta/real_editor_unlocked.png")

        # Stampa campi di testo o combobox trovati
        combos = page.locator('div[role="combobox"]').all()
        for idx, c in enumerate(combos):
            print(f"Combobox {idx}: {c.inner_text().strip().replace(chr(10), ' ')}")

    finally:
        context.close()

if __name__ == "__main__":
    run()

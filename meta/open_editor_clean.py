import sys
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from meta.paths import get_cache_dir
from meta.browser import launch_meta_browser

AD_ACCOUNT_ID = "1116925509636183"

def run():
    cache_dir = get_cache_dir()
    context = launch_meta_browser(headless=False)
    page = context.pages[0] if context.pages else context.new_page()

    try:
        url = f"https://adsmanager.facebook.com/adsmanager/manage/ads?act={AD_ACCOUNT_ID}"
        page.goto(url, wait_until="networkidle")
        time.sleep(5)

        # 1. Chiudi 'Crea visualizzazione' premendo Escape o cliccando X
        page.keyboard.press("Escape")
        time.sleep(1)

        # 2. Clicca sul cestino delle bozze in alto (accanto a Controlla e pubblica)
        trash = page.locator('button[aria-label="Elimina bozze"], [aria-label*="Scarta"], [aria-label*="bozz"]').first
        if trash.count() == 0:
            # Trova il bottone con svg cestino vicino a 'Controlla e pubblica'
            rev = page.locator('button:has-text("Controlla e pubblica")').first
            if rev.count() > 0:
                box = rev.bounding_box()
                # Il cestino è a sinistra di 'Controlla e pubblica' (circa x - 40)
                trash_x = box['x'] - 35
                trash_y = box['y'] + (box['height'] / 2)
                print(f"Click cestino a ({trash_x}, {trash_y})...")
                page.mouse.click(trash_x, trash_y)
                time.sleep(2)
        else:
            trash.click()
            time.sleep(2)

        # Se compare il dialog di conferma eliminazione bozza:
        del_confirm = page.locator('button:has-text("Elimina"), button:has-text("Scarta"), button:has-text("Elimina bozza")').first
        if del_confirm.count() > 0:
            print("Conferma eliminazione bozza:", del_confirm.inner_text())
            del_confirm.click()
            time.sleep(4)

        # 3. Ora guarda l'inserzione con la thumbnail
        # Clicca sul testo del nome dell'inserzione o sul pulsante Modifica
        thumb = page.locator('img[src*="scontent"], img[alt*="Nuova inserzione"], div[role="gridcell"]:has-text("Campagna non attiva")').first
        if thumb.count() > 0:
            print("Trovata cella inserzione reale! Clicco...")
            # Clicchiamo su Modifica
            row = thumb.locator('xpath=ancestor::div[@role="row"]')
            row.hover()
            time.sleep(1)
            # Cerca il pulsante Modifica
            mod = page.locator('button:has-text("Modifica")').first
            if mod.count() > 0:
                mod.click()
                time.sleep(5)

        shot = cache_dir / "editor_clean_step1.png"
        page.screenshot(path=str(shot))
        print("Screenshot salvato:", shot)

        time.sleep(10)

    finally:
        context.close()

if __name__ == "__main__":
    run()

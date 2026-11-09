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
    context = launch_meta_browser(headless=True)
    page = context.pages[0] if context.pages else context.new_page()

    try:
        url = f"https://adsmanager.facebook.com/adsmanager/manage/campaigns?act={AD_ACCOUNT_ID}"
        page.goto(url, wait_until="networkidle")
        time.sleep(5)

        # Cerca la riga di Rikrestin
        print("Cerca switch di Rikrestin...")
        # Chiudi pannelli laterali o popup se ci sono
        close_x = page.locator('button[aria-label="Chiudi"]').all()
        for x in close_x:
            try:
                x.click()
                time.sleep(1)
            except Exception:
                pass

        # Trova la cella contenente 'Rikrestin'
        rik_cell = page.locator('text="Rikrestin 2x49 - Test Vendite"').first
        if rik_cell.count() > 0:
            print("Cella Rikrestin trovata. Cerco la riga genitore...")
            # Risali al container di riga
            row = rik_cell.locator('xpath=ancestor::div[@role="row"]')
            if row.count() > 0:
                print("Container riga trovato!")
                # Cerca lo switch all'interno di questa specifica riga
                switch = row.locator('div[role="switch"], input[role="switch"], [role="switch"]').first
                if switch.count() > 0:
                    checked = switch.get_attribute('aria-checked')
                    print(f"Stato switch prima del click: {checked}")
                    if checked == "true" or checked is None:
                        switch.click()
                        time.sleep(3)
                        print("Switch cliccato!")
                    else:
                        print("Lo switch risulta già disattivo!")

        # Ora scartiamo anche le bozze inutili (pulsante cestino in alto)
        trash_btn = page.locator('button[aria-label="Elimina bozza"], button:has-text("Elimina bozza")').first
        # oppure icona cestino accanto a Controlla e pubblica
        top_trash = page.locator('button:has-text("Controlla e pubblica")').locator('xpath=preceding-sibling::button').first
        
        time.sleep(3)
        shot = cache_dir / "rikrestin_off_verified.png"
        page.screenshot(path=str(shot))
        print("Screenshot salvato in:", shot)

        # Verifica stato finale
        rows = page.locator('div[role="row"]').all()
        for i, r in enumerate(rows):
            t = r.inner_text().strip().replace('\n', ' | ')
            if 'Rikrestin' in t:
                print(f"RIGA RIKRESTIN DOPO L'AZIONE: {t}")

    finally:
        context.close()

if __name__ == "__main__":
    run()

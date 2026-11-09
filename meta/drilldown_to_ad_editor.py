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
    context = launch_meta_browser(headless=False)
    page = context.pages[0] if context.pages else context.new_page()

    try:
        url = f"https://adsmanager.facebook.com/adsmanager/manage/campaigns?act={AD_ACCOUNT_ID}"
        print(f"1. Navigazione a Campagne: {url}")
        page.goto(url, wait_until="networkidle")
        time.sleep(5)

        # Chiudi pannelli laterali 'Crea visualizzazione' se aperti
        close_btn = page.locator('button[aria-label="Chiudi"]').all()
        for b in close_btn:
            try:
                b.click()
                time.sleep(1)
            except Exception:
                pass

        # Se c'è bozza residua, eliminiamola col cestino in alto
        trash_icon = page.locator('button').filter(has=page.locator('svg')).filter(has_not=page.locator('text')).all()
        # Clicca sul cestino vicino a 'Controlla e pubblica'
        rev = page.locator('button:has-text("Controlla e pubblica")').first
        if rev.count() > 0:
            rbox = rev.bounding_box()
            if rbox:
                page.mouse.click(rbox['x'] - 35, rbox['y'] + (rbox['height'] / 2))
                time.sleep(2)
                del_btn = page.locator('button:has-text("Elimina"), button:has-text("Scarta")').first
                if del_btn.count() > 0:
                    print("Eliminazione bozze...")
                    del_btn.click()
                    time.sleep(3)

        # 2. Clicca sulla campagna Rikrestin
        print("2. Apertura campagna 'Rikrestin 2x49 - Test Vendite'...")
        camp_link = page.locator('text="Rikrestin 2x49 - Test Vendite"').first
        if camp_link.count() > 0:
            camp_link.click()
            time.sleep(4)
        else:
            print("Link campagna non trovato!")

        # Ora siamo a livello Gruppi di inserzioni
        print("3. Navigazione a livello Inserzioni...")
        ads_tab = page.locator('button:has-text("Inserzioni"), div[role="tab"]:has-text("Inserzioni")').first
        if ads_tab.count() > 0:
            ads_tab.click()
            time.sleep(4)

        # Ora clicca su Modifica
        print("4. Clicco su Modifica inserzione...")
        # Seleziona la riga dell'inserzione
        chk = page.locator('div[role="row"] input[type="checkbox"]').all()
        if len(chk) >= 2:
            chk[1].click(force=True)
            time.sleep(1)

        mod_btn = page.locator('button:has-text("Modifica")').first
        if mod_btn.count() > 0:
            mod_btn.click()
            time.sleep(5)
            print("Pannello Modifica aperto con successo!")

        print("Attendo 15 secondi per ispezione...")
        time.sleep(15)

    finally:
        context.close()

if __name__ == "__main__":
    run()

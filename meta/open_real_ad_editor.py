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
        print(f"Navigazione a: {url}")
        page.goto(url, wait_until="networkidle")
        time.sleep(5)

        # 1. Elimina bozze se presente
        del_drafts = page.locator('button:has-text("Elimina bozze")').first
        if del_drafts.count() > 0:
            print("Clicco su 'Elimina bozze'...")
            del_drafts.click()
            time.sleep(2)
            confirm_del = page.locator('button:has-text("Elimina"), button:has-text("Scarta"), button:has-text("Conferma")').first
            if confirm_del.count() > 0:
                print("Confermo eliminazione bozze:", confirm_del.inner_text())
                confirm_del.click()
                time.sleep(3)

        # 2. Chiudi il pannello laterale 'Crea visualizzazione' se c'è
        close_drawer = page.locator('div:has-text("Crea visualizzazione") button[aria-label="Chiudi"], div[aria-label="Chiudi"]').first
        if close_drawer.count() > 0:
            print("Chiudo drawer laterale...")
            try:
                close_drawer.click()
                time.sleep(2)
            except Exception:
                pass

        # 3. Ora abbiamo solo la vera inserzione di Rikrestin
        print("Cerco la riga inserzione...")
        rows = page.locator('div[role="row"]').all()
        target_row = None
        for r in rows:
            txt = r.inner_text()
            if 'Campagna non attiv' in txt or 'Rikrestin' in txt:
                target_row = r
                break

        if target_row:
            print("Riga inserzione target trovata!")
            # Hover e click su Modifica
            target_row.hover()
            time.sleep(1)
            # Clicca sulla checkbox della riga per selezionarla
            chk = target_row.locator('input[type="checkbox"]').first
            if chk.count() > 0:
                chk.click(force=True)
                time.sleep(1)

            # Clicca sul pulsante Modifica della toolbar o della riga
            mod_btn = page.locator('button:has-text("Modifica"), div[role="button"]:has-text("Modifica")').filter(has_text="Modifica").first
            if mod_btn.count() > 0:
                print("Clicco sul pulsante Modifica...")
                mod_btn.click()
                time.sleep(5)

        shot = cache_dir / "real_ad_editor_opened.png"
        page.screenshot(path=str(shot))
        print("Screenshot salvato:", shot)

        time.sleep(5)

    finally:
        context.close()

if __name__ == "__main__":
    run()

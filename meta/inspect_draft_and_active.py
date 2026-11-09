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

        # 1. Imposta la data su "Oggi"
        date_picker = page.locator('button:has-text("16 ott"), button:has-text("Ultimi"), div[role="button"]:has-text("16 ott"), div[role="button"]:has-text("Ultimi")').first
        if date_picker.count() > 0:
            print("Click date picker...")
            date_picker.click()
            time.sleep(1)
            oggi_btn = page.locator('text="Oggi"').first
            if oggi_btn.count() > 0:
                print("Click Oggi...")
                oggi_btn.click()
                time.sleep(3)

        # 2. Check draft review dialog
        rev_btn = page.locator('button:has-text("Controlla e pubblica")').first
        if rev_btn.count() > 0:
            print("Click Controlla e pubblica...")
            rev_btn.click()
            time.sleep(3)
            shot_rev = cache_dir / "draft_review_items.png"
            page.screenshot(path=str(shot_rev))
            print("Screenshot review items saved.")
            dialog = page.locator('div[role="dialog"]').first
            if dialog.count() > 0:
                print("=== CONTENUTO DIALOG REVISIONE ===")
                print(dialog.inner_text())
                
                # Chiudi dialog cliccando Annulla o la X se c'è
                close_btn = dialog.locator('button:has-text("Annulla"), button[aria-label="Chiudi"]').first
                if close_btn.count() > 0:
                    close_btn.click()
                    time.sleep(2)

        # 3. Ora guarda la lista campagne (con Oggi o Totale)
        time.sleep(3)
        shot_all = cache_dir / "campaigns_full_view.png"
        page.screenshot(path=str(shot_all))
        print("Screenshot campaigns full saved.")

        # Estrai tutti i testi delle righe
        print("\n=== TUTTE LE RIGHE TABELLA ===")
        rows = page.locator('div[role="row"]').all()
        for i, r in enumerate(rows):
            t = r.inner_text().strip().replace('\n', ' | ')
            if t:
                print(f"Row {i}: {t}")

    finally:
        context.close()

if __name__ == "__main__":
    run()

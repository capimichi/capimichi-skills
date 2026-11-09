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

        for i in range(20):
            loading = page.locator('div[role="dialog"]:has-text("Caricamento in corso")')
            if loading.count() > 0 and loading.first.is_visible():
                print(f"[{i}] Caricamento ancora visibile, attendo 1s...")
                time.sleep(1)
            else:
                print(f"[{i}] Caricamento non più visibile!")
                break
        
        time.sleep(2)
        page.keyboard.press("Escape")
        time.sleep(1)

        page.screenshot(path=str(PROJECT_ROOT / "meta" / "table_ready.png"))
        print("Screenshot salvato in meta/table_ready.png")

        # Cerca link o testo con 'Copia'
        copia_target = page.locator(':text("Nuova inserzione Vendite - Copia"), :text("Errore dell\'inserzione")').first
        if copia_target.count() > 0:
            print("Target trovato! Clicco su target...")
            copia_target.click()
            time.sleep(6)
        else:
            print("Nessun target Copia/Errore trovato!")

        page.screenshot(path=str(PROJECT_ROOT / "meta" / "after_target_click.png"))
        print("Screenshot salvato in meta/after_target_click.png")

    finally:
        context.close()

if __name__ == "__main__":
    run()

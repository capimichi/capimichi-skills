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
        page.goto(url, wait_until="domcontentloaded")
        time.sleep(6)
        page.keyboard.press("Escape")
        time.sleep(1)

        page.screenshot(path=str(PROJECT_ROOT / "meta" / "ads_list_with_draft.png"))
        print("Screenshot salvato in meta/ads_list_with_draft.png")

        # Cerca la bozza 'Copia'
        copy_cell = page.locator('text*="Copia"').first
        if copy_cell.count() > 0:
            print("Trovata riga Copia! Clicco su Modifica...")
            # Hover sulla riga
            row = copy_cell.locator('xpath=ancestor::div[@role="row"]')
            row.hover()
            time.sleep(1)
            # Clicca Modifica
            mod = row.locator(':text("Modifica")').first
            if mod.count() > 0:
                mod.click()
                time.sleep(6)
            else:
                copy_cell.click()
                time.sleep(6)
        else:
            print("Riga Copia non trovata con text*=Copia")

        page.screenshot(path=str(PROJECT_ROOT / "meta" / "editor_draft_opened.png"))
        print("Screenshot salvato in meta/editor_draft_opened.png")

    finally:
        context.close()

if __name__ == "__main__":
    run()

import sys
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from meta.browser import launch_meta_browser

AD_ACCOUNT_ID = "1116925509636183"
CAMPAIGN_ID = "120251426951480676"
IMAGE_PATH = PROJECT_ROOT / "meta" / "assets" / "rikrestin_ad_b_graphic.jpeg"

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
        time.sleep(6)
        page.keyboard.press("Escape")
        time.sleep(1)

        copia_target = page.locator(':text("Nuova inserzione Vendite - Copia")').first
        if copia_target.count() > 0:
            copia_target.click()
            time.sleep(2)

        mod_btn = page.locator(':text("Modifica")').first
        mod_btn.click()
        time.sleep(6)

        # Clicca Seleziona immagine nel box errore
        sel_img = page.locator('button:has-text("Seleziona immagine"), div[role="button"]:has-text("Seleziona immagine")').first
        if sel_img.count() > 0:
            print("Clicco su 'Seleziona immagine'...")
            sel_img.click()
            time.sleep(4)
        else:
            print("Cerco 'Aggiungi contenuto multimediale'...")
            add_media = page.locator(':text("Aggiungi contenuto multimediale")').first
            add_media.click()
            time.sleep(2)
            page.locator('text="Aggiungi immagine"').first.click()
            time.sleep(3)

        page.screenshot(path=str(PROJECT_ROOT / "meta" / "media_picker_dialog.png"))
        print("Screenshot salvato in meta/media_picker_dialog.png")

        # Cerca file input per caricamento
        file_input = page.locator('input[type="file"]').first
        print(f"File input trovato: {file_input.count() > 0}")
        if file_input.count() > 0:
            print("Carico file immagine:", IMAGE_PATH)
            file_input.set_input_files(str(IMAGE_PATH))
            time.sleep(8)

        page.screenshot(path=str(PROJECT_ROOT / "meta" / "media_picker_after_upload.png"))
        print("Screenshot salvato in meta/media_picker_after_upload.png")

        # Stampa bottoni visibili nel modal
        buttons = page.locator('div[role="dialog"] button, div[role="dialog"] div[role="button"]').all()
        print(f"Bottoni nel dialog: {len(buttons)}")
        for b in buttons:
            txt = b.inner_text().strip()
            if txt:
                print("Dialog button:", txt)

    finally:
        context.close()

if __name__ == "__main__":
    run()

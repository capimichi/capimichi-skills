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
        time.sleep(8)
        page.keyboard.press("Escape")
        time.sleep(2)

        # Clicca bozza
        target = page.locator(':text("Inserzione B - Offerta COD"), :text("Inserzione senza nome"), :text("In bozza")').first
        target.click()
        time.sleep(2)

        # Clicca Modifica nella toolbar
        page.mouse.click(490, 233)
        time.sleep(6)

        # Trova e clicca Aggiungi contenuto multimediale
        btn = page.locator('div[role="button"]:has-text("Aggiungi contenuto multimediale")').first
        btn.scroll_into_view_if_needed()
        time.sleep(1)
        btn.click(force=True)
        time.sleep(2)

        # Clicca Aggiungi un'immagine
        add_img = page.locator(':text("Aggiungi un\'immagine")').first
        print("Clicco Aggiungi un'immagine...")
        add_img.click()
        time.sleep(5)

        page.screenshot(path=str(PROJECT_ROOT / "meta" / "picker_modal_open.png"))
        print("Screenshot salvato in meta/picker_modal_open.png")

        # Cerca file input
        file_input = page.locator('input[type="file"]').first
        print("File input trovato:", file_input.count() > 0)
        if file_input.count() > 0:
            print("Carico immagine:", IMAGE_PATH)
            file_input.set_input_files(str(IMAGE_PATH))
            time.sleep(8)

        page.screenshot(path=str(PROJECT_ROOT / "meta" / "after_upload_image.png"))
        print("Screenshot salvato in meta/after_upload_image.png")

        # Esamina elementi e bottoni nel modal
        dialog = page.locator('div[role="dialog"]').first
        if dialog.count() > 0:
            btns = dialog.locator('button, div[role="button"]').all()
            for b in btns:
                txt = b.inner_text().strip()
                if txt:
                    print("Dialog btn:", txt)

    finally:
        context.close()

if __name__ == "__main__":
    run()

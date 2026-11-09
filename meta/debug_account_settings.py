import sys
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from meta.browser import launch_meta_browser

AD_ACCOUNT_ID = "1116925509636183"

def run():
    context = launch_meta_browser(headless=True)
    page = context.pages[0] if context.pages else context.new_page()

    try:
        url = f"https://adsmanager.facebook.com/adsmanager/manage/account_settings?act={AD_ACCOUNT_ID}"
        print("Navigazione a:", url)
        page.goto(url, wait_until="domcontentloaded")
        time.sleep(8)

        print("Current URL:", page.url)
        page.screenshot(path=str(PROJECT_ROOT / "meta" / "debug_account_settings.png"))

        # Cerca testo e pulsanti
        buttons = page.locator('button, div[role="button"]').all()
        print(f"Totale bottoni trovati: {len(buttons)}")
        for b in buttons:
            txt = b.inner_text().strip()
            if txt:
                print(f"Button: '{txt}'")

        # Cerca frames
        print(f"Totale frames: {len(page.frames)}")
        for f in page.frames:
            print("Frame:", f.url)
            btn_in_frame = f.locator('button:has-text("Aggiungi persone"), div[role="button"]:has-text("Aggiungi persone")').all()
            if btn_in_frame:
                print(f" -> Trovato 'Aggiungi persone' nel frame {f.url}!")

    finally:
        context.close()

if __name__ == "__main__":
    run()

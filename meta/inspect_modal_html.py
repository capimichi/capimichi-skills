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
        url = f"https://adsmanager.facebook.com/adsmanager/manage/ad_account_settings?act={AD_ACCOUNT_ID}"
        page.goto(url, wait_until="domcontentloaded")
        time.sleep(6)

        add_btn = page.locator('[role="button"]:has-text("Aggiungi persone")').first
        add_btn.click()
        time.sleep(3)

        dialog = page.locator('[role="dialog"]:has-text("Aggiungi persone a questo account pubblicitario")').first
        inp = dialog.locator('input:not([type="hidden"])').first
        print(f"Input trovato: {inp.get_attribute('placeholder')}")
        inp.click()
        time.sleep(1)

        # Type using keyboard
        page.keyboard.type("Michele Capicchioni", delay=120)
        time.sleep(4)

        page.screenshot(path=str(PROJECT_ROOT / "meta" / "keyboard_typed_result.png"))

        # Cerca elementi popover o listbox nel body
        popovers = page.locator('div[role="listbox"], ul[role="listbox"], div[class*="uiContextualLayer"], div[class*="popover"], div[role="menu"]').all()
        print(f"\nPopovers/Listboxes nel body: {len(popovers)}")
        for p in popovers:
            t = p.inner_text().strip()
            if t:
                print("Popover text:\n", t)

    finally:
        context.close()

if __name__ == "__main__":
    run()

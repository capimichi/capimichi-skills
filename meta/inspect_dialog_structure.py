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
        inp.click()
        page.keyboard.type("Michele Capicchioni", delay=120)
        time.sleep(3)

        friend_item = page.locator('div:has-text("Michele Capicchioni"):has-text("Città di San Marino")').last
        friend_item.click()
        time.sleep(2)

        page.screenshot(path=str(PROJECT_ROOT / "meta" / "debug_dialog_elements.png"))

        # Trova tutti i discendenti con testo o ruolo
        print("\n--- ELEMENTI NEL DIALOG ---")
        elements = dialog.locator('button, [role="button"], [role="combobox"], select, a, input, div[class*="ui"]').all()
        for i, el in enumerate(elements):
            tag = el.evaluate("e => e.tagName")
            role = el.get_attribute("role") or ""
            cls = el.get_attribute("class") or ""
            txt = el.inner_text().strip().replace("\n", " ")
            print(f"[{i}] <{tag} role='{role}' class='{cls[:30]}'> Text: '{txt}'")

    finally:
        context.close()

if __name__ == "__main__":
    run()

import sys
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from meta.browser import launch_meta_browser

AD_ACCOUNT_ID = "1116925509636183"

def run():
    context = launch_meta_browser(
        headless=True,
        args=["--window-size=1600,1000"],
        viewport={"width": 1600, "height": 1000}
    )
    page = context.pages[0] if context.pages else context.new_page()

    try:
        url = f"https://adsmanager.facebook.com/adsmanager/manage/ads?act={AD_ACCOUNT_ID}&selected_campaign_ids=120251426951480676"
        page.goto(url, wait_until="domcontentloaded")
        time.sleep(5)
        page.keyboard.press("Escape")
        time.sleep(1)

        dettagli_btn = page.locator('button:has-text("Dettagli"), div[role="button"]:has-text("Dettagli")').first
        if dettagli_btn.count() > 0:
            dettagli_btn.click()
            time.sleep(2)

            # Hover o click su 'Elemento della creatività dinamica'
            item1 = page.locator('text="Elemento della creatività dinamica"').first
            if item1.count() > 0:
                item1.hover()
                time.sleep(1)
                item1.click()
                time.sleep(2)
                page.screenshot(path=str(PROJECT_ROOT / "meta" / "dettagli_sub_elemento.png"))
                print("Submenu elemento salvato")

            # Cerca anche Creatività
            item2 = page.locator('text="Creatività"').first
            if item2.count() > 0:
                item2.hover()
                time.sleep(1)
                item2.click()
                time.sleep(2)
                page.screenshot(path=str(PROJECT_ROOT / "meta" / "dettagli_sub_creativita.png"))
                print("Submenu creativita salvato")

            body_text = page.locator('body').inner_text()
            with open(PROJECT_ROOT / "meta" / "dettagli_all_text.txt", "w", encoding="utf-8") as f:
                f.write(body_text)

    finally:
        context.close()

if __name__ == "__main__":
    run()

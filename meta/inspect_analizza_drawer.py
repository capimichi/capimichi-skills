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

        # Seleziona riga inserzione
        boxes = page.locator('input[type="checkbox"]').all()
        if len(boxes) > 1:
            boxes[1].click(force=True)
            time.sleep(1)

        # Clicca sul pulsante Analizza in alto
        analizza_btn = page.locator('button:has-text("Analizza"), div[role="button"]:has-text("Analizza")').first
        if analizza_btn.count() > 0:
            print("Click su Analizza...")
            analizza_btn.click()
            time.sleep(5)
            page.screenshot(path=str(PROJECT_ROOT / "meta" / "analizza_panel.png"))
            print("Screenshot analizza salvato")

            panel_text = page.locator('body').inner_text()
            with open(PROJECT_ROOT / "meta" / "analizza_panel_text.txt", "w", encoding="utf-8") as f:
                f.write(panel_text)

    finally:
        context.close()

if __name__ == "__main__":
    run()

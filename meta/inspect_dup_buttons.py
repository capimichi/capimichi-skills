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
        time.sleep(5)
        page.keyboard.press("Escape")
        time.sleep(1)

        boxes = page.locator('input[type="checkbox"]').all()
        if len(boxes) > 1:
            boxes[1].click(force=True)
            time.sleep(1)

        # Clicca Duplica nella toolbar
        dup_btn = page.locator('div[role="toolbar"] button:has-text("Duplica"), div[role="button"]:has-text("Duplica"), button:has-text("Duplica")').first
        dup_btn.click()
        time.sleep(3)

        # Ispezione del dialog
        dialog = page.locator('div[role="dialog"]').first
        print("Testo Dialog:")
        print(dialog.inner_text())

        # Trova tutti i bottoni/clickable dentro il dialog
        buttons = dialog.locator('button, div[role="button"], span, div').all()
        print(f"Elementi totali nel dialog: {len(buttons)}")
        for b in buttons:
            txt = b.inner_text().strip()
            if txt in ["Duplica", "Annulla", "Visualizza anteprima delle modifiche"]:
                tag = b.evaluate("el => el.tagName")
                role = b.get_attribute("role") or ""
                bbox = b.bounding_box()
                print(f"Match: tag={tag}, role={role}, text='{txt}', bbox={bbox}")
                if txt == "Duplica" and bbox and bbox['width'] > 20:
                    print("Clicco su Duplica...")
                    b.click()
                    time.sleep(6)
                    break

        page.screenshot(path=str(PROJECT_ROOT / "meta" / "editor_duplicated_success.png"))
        print("Screenshot salvato in meta/editor_duplicated_success.png")

    finally:
        context.close()

if __name__ == "__main__":
    run()

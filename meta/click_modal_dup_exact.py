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

        # Trova il modal esatto
        modal = page.locator('div[role="dialog"]').filter(has_text="Duplica la tua inserzione").first
        if modal.count() > 0:
            print("Modal 'Duplica la tua inserzione' trovato!")
            # Uncheck video
            chk = modal.locator('input[type="checkbox"]').first
            if chk.count() > 0 and chk.is_checked():
                print("Deseleziono Aggiungi un video...")
                chk.click()
                time.sleep(1)

            # Clicca Duplica
            d_btn = modal.locator('button:has-text("Duplica"), div[role="button"]:has-text("Duplica")').last
            print("Clicco su Duplica...")
            d_btn.click()
            time.sleep(8)
        else:
            print("Modal non trovato per testo, provo click coordinate (1218, 448)...")
            page.mouse.click(1218, 448)
            time.sleep(8)

        page.screenshot(path=str(PROJECT_ROOT / "meta" / "editor_after_duplicate_real.png"))
        print("Screenshot salvato in meta/editor_after_duplicate_real.png")

        # Stampa primi 60 righe di testo
        txt = page.locator('body').inner_text()
        with open(PROJECT_ROOT / "meta" / "editor_after_duplicate_text.txt", "w", encoding="utf-8") as f:
            f.write(txt)

        print("\n--- TESTO EDITOR DUPLICATO ---")
        for l in txt.splitlines()[:40]:
            if l.strip():
                print("->", l.strip())

    finally:
        context.close()

if __name__ == "__main__":
    run()

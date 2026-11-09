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

        # Scroll to bottom of middle panel
        page.mouse.move(500, 500)
        for _ in range(5):
            page.mouse.wheel(0, 800)
            time.sleep(1)

        page.screenshot(path=str(PROJECT_ROOT / "meta" / "editor_bottom.png"))
        print("Screenshot salvato in meta/editor_bottom.png")

        # Esamina tutti i testi visibili dal bottom
        body_text = page.locator('body').inner_text()
        with open(PROJECT_ROOT / "meta" / "editor_full_text.txt", "w", encoding="utf-8") as f:
            f.write(body_text)

        lines = [l.strip() for l in body_text.split('\n') if l.strip()]
        for l in lines:
            if any(w in l.lower() for w in ["whatsapp", "invito all'azione", "destinazione", "pixel", "tracciamento", "messagg"]):
                print("Line:", l)

    finally:
        context.close()

if __name__ == "__main__":
    run()

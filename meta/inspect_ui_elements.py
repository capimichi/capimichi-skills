import sys
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from meta.browser import launch_meta_browser

AD_ACCOUNT_ID = "1116925509636183"

def run():
    context = launch_meta_browser(headless=False)
    page = context.pages[0] if context.pages else context.new_page()

    try:
        url = f"https://adsmanager.facebook.com/adsmanager/manage/ads?act={AD_ACCOUNT_ID}"
        page.goto(url, wait_until="networkidle")
        time.sleep(5)

        # 1. Trova tutti gli elementi con aria-label Chiudi
        close_elements = page.locator('[aria-label*="Chiudi"], [aria-label*="chiudi"]').all()
        print(f"Chiudi elements: {len(close_elements)}")
        for idx, el in enumerate(close_elements):
            print(f"El {idx}: tag={el.evaluate('e => e.tagName')}, box={el.bounding_box()}, label={el.get_attribute('aria-label')}")

        # 2. Trova il pulsante 'Crea visualizzazione' container
        drawer = page.locator('div:has-text("Crea visualizzazione")').first
        if drawer.count() > 0:
            print("Drawer text:", drawer.inner_text()[:100])
            # Cerchiamo tutti i button o svg dentro il drawer
            btns = drawer.locator('button, [role="button"]').all()
            print(f"Buttons inside drawer: {len(btns)}")
            for idx, b in enumerate(btns):
                print(f"Drawer btn {idx}: text={b.inner_text()}, box={b.bounding_box()}, label={b.get_attribute('aria-label')}")
                # Clicchiamo sul primo che sembra la X (box height < 30)
                bbox = b.bounding_box()
                if bbox and bbox['width'] < 30 and bbox['height'] < 30:
                    print(f"Clicco la X del drawer a {bbox}!")
                    b.click()
                    time.sleep(2)
                    break

        page.screenshot(path=str(PROJECT_ROOT / "meta" / "after_drawer_x_clicked.png"))
        print("Screenshot salvato.")

    finally:
        context.close()

if __name__ == "__main__":
    run()

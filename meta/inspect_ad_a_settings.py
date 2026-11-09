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

        # Clicca sulla cella della bozza per selezionarla
        copia_target = page.locator(':text("Nuova inserzione Vendite - Copia")').first
        copia_target.click()
        time.sleep(2)

        # Clicca Modifica nella toolbar a (490, 233)
        page.mouse.click(490, 233)
        time.sleep(6)

        # Clicca sull'inserzione originale Ad A nella sidebar sinistra
        ad_a_nav = page.locator('div[role="treeitem"]:has-text("Nuova inserzione Vendite"), div[role="listitem"]:has-text("Nuova inserzione Vendite"), :text("Nuova inserzione Vendite")').last
        print("Clicco su Ad A nella sidebar sinistra...")
        ad_a_nav.click()
        time.sleep(6)

        page.screenshot(path=str(PROJECT_ROOT / "meta" / "ad_a_editor_view.png"))
        print("Screenshot salvato in meta/ad_a_editor_view.png")

        # Dump testi di Ad A
        text_a = page.locator('body').inner_text()
        with open(PROJECT_ROOT / "meta" / "ad_a_editor_text.txt", "w", encoding="utf-8") as f:
            f.write(text_a)

    finally:
        context.close()

if __name__ == "__main__":
    run()

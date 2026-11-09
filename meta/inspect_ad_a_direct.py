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
        time.sleep(8)
        page.keyboard.press("Escape")
        time.sleep(2)

        # Clicca bozza
        target = page.locator(':text("Inserzione B - Offerta COD"), :text("Inserzione senza nome"), :text("In bozza")').first
        target.click()
        time.sleep(2)

        # Clicca Modifica nella toolbar
        page.mouse.click(490, 233)
        time.sleep(6)

        # Clicca su Ad A nella sidebar sinistra a x=120, y=205
        print("Clicco su Nuova inserzione Vendite (Ad A) nella sidebar...")
        page.mouse.click(120, 205)
        time.sleep(6)

        page.screenshot(path=str(PROJECT_ROOT / "meta" / "ad_a_editor_comparison.png"))
        print("Screenshot salvato in meta/ad_a_editor_comparison.png")

        # Clicca su Controlla impostazioni predefinite a x=740, y=315
        print("Clicco su impostazioni predefinite...")
        page.mouse.click(740, 315)
        time.sleep(4)

        page.screenshot(path=str(PROJECT_ROOT / "meta" / "ad_a_predefinite_modal.png"))
        print("Screenshot salvato in meta/ad_a_predefinite_modal.png")

    finally:
        context.close()

if __name__ == "__main__":
    run()

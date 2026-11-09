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
        url = f"https://adsmanager.facebook.com/adsmanager/manage/campaigns?act={AD_ACCOUNT_ID}"
        page.goto(url, wait_until="domcontentloaded")
        time.sleep(5)

        # Clicca sull'icona ingranaggio a sinistra
        gear = page.locator('a[href*="settings"], [aria-label*="Impostazioni"]').first
        if gear.count() == 0:
            gear = page.locator('nav a, div[role="navigation"] a').last
        print(f"Click su ingranaggio: {gear.get_attribute('aria-label') or gear.get_attribute('href')}")
        gear.click()
        time.sleep(6)

        page.screenshot(path=str(PROJECT_ROOT / "meta" / "real_account_settings.png"))
        print("URL impostazioni:", page.url)

        # Cerca testo e pulsanti
        txt = page.locator('body').inner_text()
        print("\n--- TESTO IMPOSTAZIONI ACCOUNT ---")
        for line in txt.splitlines()[:30]:
            if line.strip():
                print(line.strip())

    finally:
        context.close()

if __name__ == "__main__":
    run()

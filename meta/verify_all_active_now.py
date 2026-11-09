import sys
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from meta.browser import launch_meta_browser

AD_ACCOUNT_ID = "1116925509636183"

def run():
    print("=" * 60)
    print("VERIFICA FINALE STATO TUTTI I LIVELLI DOPO SBLOCCO")
    print("=" * 60)

    context = launch_meta_browser(headless=True)
    page = context.pages[0] if context.pages else context.new_page()

    try:
        # 1. Campagne
        url_c = f"https://adsmanager.facebook.com/adsmanager/manage/campaigns?act={AD_ACCOUNT_ID}"
        page.goto(url_c, wait_until="domcontentloaded")
        time.sleep(5)
        page.screenshot(path=str(PROJECT_ROOT / "meta" / "verified_active_campaign.png"))
        print("Campagna:", page.locator('div[role="row"]:has-text("Rikrestin")').inner_text().replace("\n", " | "))

        # 2. Gruppi di inserzioni
        url_adsets = f"https://adsmanager.facebook.com/adsmanager/manage/adsets?act={AD_ACCOUNT_ID}"
        page.goto(url_adsets, wait_until="domcontentloaded")
        time.sleep(5)
        page.screenshot(path=str(PROJECT_ROOT / "meta" / "verified_active_adset.png"))
        print("AdSet:", page.locator('div[role="row"]:has-text("Vendite")').inner_text().replace("\n", " | "))

        # 3. Inserzioni
        url_ads = f"https://adsmanager.facebook.com/adsmanager/manage/ads?act={AD_ACCOUNT_ID}"
        page.goto(url_ads, wait_until="domcontentloaded")
        time.sleep(5)
        page.screenshot(path=str(PROJECT_ROOT / "meta" / "verified_active_ad.png"))
        print("Inserzione:", page.locator('div[role="row"]:has-text("Vendite")').inner_text().replace("\n", " | "))

    finally:
        context.close()

if __name__ == "__main__":
    run()

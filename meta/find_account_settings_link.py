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
        url = f"https://adsmanager.facebook.com/adsmanager/billing_hub/payment_settings?asset_id={AD_ACCOUNT_ID}"
        print("Navigazione a:", url)
        page.goto(url, wait_until="domcontentloaded")
        time.sleep(6)

        # Clicca sul dropdown 'Altre risorse'
        altre = page.locator('button:has-text("Altre risorse"), div[role="button"]:has-text("Altre risorse")').first
        print(f"Pulsante 'Altre risorse': {altre.count()}")
        if altre.count() > 0:
            altre.click()
            time.sleep(2)
            page.screenshot(path=str(PROJECT_ROOT / "meta" / "altre_risorse_menu.png"))

            items = page.locator('div[role="menu"] a, div[role="menuitem"], ul li a').all()
            print(f"Elementi in Altre risorse: {len(items)}")
            for it in items:
                print(" -> Menu item:", it.inner_text().strip(), "| href:", it.get_attribute("href"))

        # Cerca link o elementi con 'Impostazioni dell\'account pubblicitario'
        ad_acc_settings = page.locator('a:has-text("Impostazioni dell\'account pubblicitario"), div[role="button"]:has-text("Impostazioni dell\'account pubblicitario")').all()
        print(f"Link 'Impostazioni dell\'account pubblicitario': {len(ad_acc_settings)}")
        for l in ad_acc_settings:
            print(" -> Link:", l.get_attribute("href"), l.inner_text())

    finally:
        context.close()

if __name__ == "__main__":
    run()

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
    context = launch_meta_browser(headless=True, args=["--window-size=2000,1080"], viewport={"width": 2000, "height": 1080})
    page = context.pages[0] if context.pages else context.new_page()

    try:
        page.goto(f"https://adsmanager.facebook.com/adsmanager/manage/ads?act={AD_ACCOUNT_ID}&selected_campaign_ids={CAMPAIGN_ID}", wait_until="domcontentloaded")
        time.sleep(8)
        page.keyboard.press("Escape")
        time.sleep(1)

        page.locator('[role="tab"]:has-text("Inserz")').last.click()
        time.sleep(3)

        page.locator(':text("Inserzione B - Offerta COD"), :text("Inserzione senza nome"), :text("In bozza")').first.click()
        time.sleep(2)

        page.locator('div[role="toolbar"] button:has-text("Modifica"), div[role="toolbar"] div[role="button"]:has-text("Modifica")').first.click()
        time.sleep(6)

        page.evaluate("""() => {
            const container = Array.from(document.querySelectorAll('div')).find(el => el.scrollHeight > 3000 && el.clientHeight < 1000);
            if (container) container.scrollTop = 1500;
        }""")
        time.sleep(2)

        page.locator('div[role="button"]:has-text("Aggiungi contenuto multimediale"), button:has-text("Aggiungi contenuto multimediale")').first.click()
        time.sleep(2)

        for b in page.locator('div[role="menuitem"], div[role="button"]').all():
            if "immagine" in b.inner_text().lower() and "video" not in b.inner_text().lower():
                b.click()
                break
        time.sleep(5)

        # Test selecting with Playwright locator on the div[role="button"]
        card = page.locator('div[role="dialog"]').last.locator('div[role="button"]:has-text("rikrestin_ad_b_graphic.jpeg")').first
        print("Card found count:", card.count())
        
        # Click it
        card.click()
        time.sleep(2)

        page.screenshot(path="meta/test_card_clicked.png")

        # Check Avanti button
        avanti = page.locator('div[role="dialog"]').last.locator('div[role="button"]:has-text("Avanti"), button:has-text("Avanti")').last
        print("Avanti disabled:", avanti.get_attribute("aria-disabled"))

        if avanti.get_attribute("aria-disabled") == "true":
            print("Trying Space key on focused card...")
            card.focus()
            page.keyboard.press("Space")
            time.sleep(2)
            print("Avanti disabled after Space:", avanti.get_attribute("aria-disabled"))

        if avanti.get_attribute("aria-disabled") == "true":
            print("Trying Enter key on focused card...")
            card.focus()
            page.keyboard.press("Enter")
            time.sleep(2)
            print("Avanti disabled after Enter:", avanti.get_attribute("aria-disabled"))

        page.screenshot(path="meta/test_card_final.png")

    finally:
        context.close()

if __name__ == "__main__":
    run()

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

        # Clicca sulla riga in bozza
        target = page.locator(':text("Inserzione senza nome"), :text("In bozza")').first
        if target.count() > 0:
            print("Clicco su target bozza...")
            target.click()
            time.sleep(2)

        # Clicca Modifica nella toolbar
        print("Clicco Modifica toolbar...")
        page.mouse.click(490, 233)
        time.sleep(6)

        page.screenshot(path=str(PROJECT_ROOT / "meta" / "editor_part1_top.png"))
        print("Screenshot salvato in meta/editor_part1_top.png")

        # Esamina tutti i toggle / switch
        switches = page.locator('[role="switch"]').all()
        print(f"Switches trovati: {len(switches)}")
        for s in switches:
            lbl = s.locator('xpath=ancestor::div[contains(@class, "x")]').first.inner_text().replace('\n', ' ')[:80]
            print(f"Switch: checked={s.get_attribute('aria-checked')} | label={lbl}")

        # Esamina tutte le sezioni
        page.mouse.move(500, 500)
        page.mouse.wheel(0, 500)
        time.sleep(2)
        page.screenshot(path=str(PROJECT_ROOT / "meta" / "editor_part2_mid.png"))

        page.mouse.wheel(0, 500)
        time.sleep(2)
        page.screenshot(path=str(PROJECT_ROOT / "meta" / "editor_part3_dest.png"))

        page.mouse.wheel(0, 500)
        time.sleep(2)
        page.screenshot(path=str(PROJECT_ROOT / "meta" / "editor_part4_cta.png"))

    finally:
        context.close()

if __name__ == "__main__":
    run()

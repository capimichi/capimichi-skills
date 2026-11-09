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
        if copia_target.count() > 0:
            copia_target.click()
            time.sleep(2)

        # Clicca Modifica
        mod_btn = page.locator(':text("Modifica")').first
        mod_btn.click()
        time.sleep(6)

        # Scroll del pannello centrale (x around 500, y around 500)
        page.mouse.move(500, 500)
        page.mouse.wheel(0, 800)
        time.sleep(2)
        page.screenshot(path=str(PROJECT_ROOT / "meta" / "editor_scroll_1.png"))
        print("Screenshot salvato in meta/editor_scroll_1.png")

        page.mouse.wheel(0, 800)
        time.sleep(2)
        page.screenshot(path=str(PROJECT_ROOT / "meta" / "editor_scroll_2.png"))
        print("Screenshot salvato in meta/editor_scroll_2.png")

        page.mouse.wheel(0, 800)
        time.sleep(2)
        page.screenshot(path=str(PROJECT_ROOT / "meta" / "editor_scroll_3.png"))
        print("Screenshot salvato in meta/editor_scroll_3.png")

        # Cerca tutte le sezioni, label, radio button e combobox
        radios = page.locator('input[type="radio"], div[role="radio"]').all()
        print(f"Radios trovati: {len(radios)}")
        for r in radios:
            print("Radio:", r.inner_text().strip(), r.get_attribute("aria-checked"), r.get_attribute("value"))

        combos = page.locator('div[role="combobox"]').all()
        print(f"Combos trovati: {len(combos)}")
        for c in combos:
            print("Combo:", c.inner_text().strip().replace('\n', ' '))

    finally:
        context.close()

if __name__ == "__main__":
    run()

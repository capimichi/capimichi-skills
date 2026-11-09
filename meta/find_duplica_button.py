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
        page.goto(url, wait_until="domcontentloaded")
        time.sleep(5)
        page.keyboard.press("Escape")
        time.sleep(1)

        boxes = page.locator('input[type="checkbox"]').all()
        if len(boxes) > 1:
            boxes[1].click(force=True)
            time.sleep(1)

        # Clicca Duplica nella toolbar
        toolbar_dup = page.locator('div[role="toolbar"] button:has-text("Duplica"), div[role="button"]:has-text("Duplica"), button:has-text("Duplica")').first
        toolbar_dup.click()
        time.sleep(3)

        # Dump di tutti gli elementi con 'Duplica'
        elements = page.evaluate("""() => {
            const all = Array.from(document.querySelectorAll('*'));
            return all
                .filter(el => el.innerText && el.innerText.trim() === 'Duplica')
                .map(el => {
                    const rect = el.getBoundingClientRect();
                    return {
                        tag: el.tagName,
                        role: el.getAttribute('role'),
                        ariaLabel: el.getAttribute('aria-label'),
                        className: el.className,
                        x: rect.x,
                        y: rect.y,
                        width: rect.width,
                        height: rect.height,
                        isClickable: typeof el.click === 'function'
                    };
                });
        }""")

        print(f"Elementi 'Duplica' trovati: {len(elements)}")
        for idx, el in enumerate(elements):
            print(f"[{idx}] {el}")

        # Se troviamo quello nel modal (y attorno a 440-460)
        for el in elements:
            if el['y'] > 300 and el['width'] > 30 and el['height'] > 20:
                print(f"Clicco su elemento a coordinate ({el['x'] + el['width']/2}, {el['y'] + el['height']/2})...")
                page.mouse.click(el['x'] + el['width'] / 2, el['y'] + el['height'] / 2)
                time.sleep(8)
                break

        page.screenshot(path=str(PROJECT_ROOT / "meta" / "editor_after_js_click.png"))
        print("Screenshot salvato in meta/editor_after_js_click.png")

    finally:
        context.close()

if __name__ == "__main__":
    run()

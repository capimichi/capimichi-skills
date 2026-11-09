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

        menu_items = page.locator('div[role="menuitem"], div[role="button"]').all()
        for item in menu_items:
            t = item.inner_text().lower()
            if "immagine" in t and "video" not in t:
                item.click()
                break
        time.sleep(5)

        # Inspect the dialog elements
        res = page.evaluate("""() => {
            const dialogs = document.querySelectorAll('div[role="dialog"]');
            const dialog = dialogs[dialogs.length - 1];
            if (!dialog) return { error: "no dialog" };

            // Find all images or cards
            const imgs = Array.from(dialog.querySelectorAll('img')).map(img => {
                const rect = img.getBoundingClientRect();
                return {
                    src: img.src.substring(0, 40),
                    alt: img.alt,
                    x: Math.round(rect.x),
                    y: Math.round(rect.y),
                    w: Math.round(rect.width),
                    h: Math.round(rect.height)
                };
            });

            // Find texts containing rikrestin
            const allElements = Array.from(dialog.querySelectorAll('*'));
            const rikText = allElements.find(el => el.children.length === 0 && el.innerText && el.innerText.includes('rikrestin'));
            let rikRect = null;
            if (rikText) {
                const r = rikText.getBoundingClientRect();
                rikRect = { x: Math.round(r.x), y: Math.round(r.y), w: Math.round(r.width), h: Math.round(r.height) };
            }

            return { imgs: imgs.slice(0, 10), rikRect };
        }""")
        print("Inspection result:", res)

        # Now click the first image or rikRect
        if res.get("imgs"):
            first_img = res["imgs"][0]
            cx = first_img["x"] + first_img["w"] // 2
            cy = first_img["y"] + first_img["h"] // 2
            print(f"Clicking at image center: ({cx}, {cy})")
            page.mouse.click(cx, cy)
            time.sleep(2)

        page.screenshot(path="meta/debug_image_clicked.png")

        # Check Avanti button status
        avanti_status = page.evaluate("""() => {
            const dialogs = document.querySelectorAll('div[role="dialog"]');
            const dialog = dialogs[dialogs.length - 1];
            const avanti = Array.from(dialog.querySelectorAll('button, div[role="button"]')).find(b => b.innerText && b.innerText.includes('Avanti'));
            return avanti ? {
                text: avanti.innerText,
                disabled: avanti.getAttribute('aria-disabled'),
                rect: avanti.getBoundingClientRect()
            } : null;
        }""")
        print("Avanti status:", avanti_status)

    finally:
        context.close()

if __name__ == "__main__":
    run()

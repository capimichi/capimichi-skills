import sys
import time
import json
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

        add_btn = page.locator('div[role="button"]:has-text("Aggiungi contenuto multimediale"), button:has-text("Aggiungi contenuto multimediale")').first
        add_btn.click()
        time.sleep(2)

        add_img = page.locator(':text("Aggiungi un\'immagine"), :text("Aggiungi immagine")').first
        add_img.click()
        time.sleep(5)

        page.screenshot(path="meta/inspect_media_modal.png")

        info = page.evaluate("""() => {
            const dialog = document.querySelector('div[role="dialog"]');
            if (!dialog) return "No dialog";
            const text = dialog.innerText;
            const buttons = Array.from(dialog.querySelectorAll('button, div[role="button"]')).map(b => ({
                tag: b.tagName,
                text: b.innerText.trim().replace(/\\n/g, " "),
                ariaDisabled: b.getAttribute('aria-disabled'),
                role: b.getAttribute('role'),
                className: b.className.substring(0, 30)
            }));
            const cards = Array.from(dialog.querySelectorAll('div[data-testid], div[tabindex]')).filter(el => {
                return el.innerText && (el.innerText.includes('rikrestin') || el.innerText.includes('1080'));
            }).map(el => ({
                tag: el.tagName,
                text: el.innerText.replace(/\\n/g, ' '),
                tabIndex: el.tabIndex,
                role: el.getAttribute('role')
            }));
            return { cards, buttons: buttons.slice(0, 25), textSnippet: text.substring(0, 400) };
        }""")
        print(json.dumps(info, indent=2))

    finally:
        context.close()

if __name__ == "__main__":
    run()

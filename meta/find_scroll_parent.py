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
        time.sleep(8)
        page.keyboard.press("Escape")
        time.sleep(2)

        page.locator('[role="tab"]:has-text("Inserz")').last.click()
        time.sleep(2)

        page.locator(':text("Inserzione B - Offerta COD"), :text("Inserzione senza nome"), :text("In bozza")').first.click()
        time.sleep(2)

        page.locator('div[role="toolbar"] button:has-text("Modifica"), div[role="toolbar"] div[role="button"]:has-text("Modifica")').first.click()
        time.sleep(6)

        # Trova il genitore con overflow
        scroll_info = page.evaluate("""() => {
            const btn = Array.from(document.querySelectorAll('*')).find(el => el.innerText && el.innerText.trim() === 'Aggiungi contenuto multimediale');
            if (!btn) return {found: false};
            
            let p = btn.parentElement;
            const parents = [];
            while (p && p !== document.body) {
                const style = window.getComputedStyle(p);
                const overflowY = style.overflowY;
                if (overflowY === 'auto' || overflowY === 'scroll' || p.scrollHeight > p.clientHeight) {
                    parents.push({
                        tagName: p.tagName,
                        className: p.className,
                        scrollHeight: p.scrollHeight,
                        clientHeight: p.clientHeight,
                        scrollTop: p.scrollTop,
                        overflowY: overflowY
                    });
                    // Scroll this parent
                    p.scrollTop = 800;
                }
                p = p.parentElement;
            }
            return {found: true, parents: parents};
        }""")
        print("Scroll info:", scroll_info)
        time.sleep(2)

        page.screenshot(path=str(PROJECT_ROOT / "meta" / "after_parent_scroll.png"))
        print("Screenshot salvato in meta/after_parent_scroll.png")

    finally:
        context.close()

if __name__ == "__main__":
    run()

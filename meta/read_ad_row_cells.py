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
        url = f"https://adsmanager.facebook.com/adsmanager/manage/ads?act={AD_ACCOUNT_ID}"
        page.goto(url, wait_until="domcontentloaded")
        time.sleep(8)

        # Assicurati intervallo massimo
        d_btn = page.locator('button:has-text("Intervallo"), div[role="button"]:has-text("Intervallo")').first
        if d_btn.count() == 0:
            d_btn = page.locator('button:has-text("ott"), div[role="button"]:has-text("ott")').first
            if d_btn.count() > 0:
                d_btn.click()
                time.sleep(1)
                opt = page.locator('text="Intervallo massimo"').first
                if opt.count() > 0:
                    opt.click()
                    time.sleep(1)
                    agg = page.locator('button:has-text("Aggiorna")').first
                    if agg.count() > 0:
                        agg.click()
                        time.sleep(4)

        # Ispeziona tutte le righe
        rows = page.locator('div[role="row"]').all()
        print(f"Righe trovate: {len(rows)}")
        for idx, r in enumerate(rows):
            print(f"\n--- RIGA [{idx}] ---")
            print(r.inner_text().replace("\n", " | "))

        # Scorri la tabella a destra con javascript per forzare il rendering virtualizzato delle colonne
        print("\n--- SCORRIMENTO ORIZZONTALE DELLA TABELLA ---")
        page.evaluate("""() => {
            const scrollers = document.querySelectorAll('div[class*="scroll"], div[class*="table"], div[role="grid"], div[role="table"]');
            for (const s of scrollers) {
                if (s.scrollWidth > s.clientWidth) {
                    s.scrollLeft = 800;
                }
            }
        }""")
        time.sleep(2)

        page.screenshot(path=str(PROJECT_ROOT / "meta" / "table_scrolled_right.png"))

        rows_scrolled = page.locator('div[role="row"]').all()
        for idx, r in enumerate(rows_scrolled):
            print(f"\n--- RIGA SCROLLED [{idx}] ---")
            print(r.inner_text().replace("\n", " | "))

    finally:
        context.close()

if __name__ == "__main__":
    run()

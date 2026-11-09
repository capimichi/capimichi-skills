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
    print("LETTURA COMPLETA VALORI DI OGGI (TABELLA SCROLLATA)")
    print("=" * 60)

    context = launch_meta_browser(
        headless=True,
        args=["--window-size=1600,1000"],
        viewport={"width": 1600, "height": 1000}
    )
    page = context.pages[0] if context.pages else context.new_page()

    try:
        url = f"https://adsmanager.facebook.com/adsmanager/manage/campaigns?act={AD_ACCOUNT_ID}"
        page.goto(url, wait_until="domcontentloaded")
        time.sleep(5)
        page.keyboard.press("Escape")
        time.sleep(1)

        # 1. Imposta data su Oggi
        d_btn = page.locator('button[aria-label*="Data"], div[role="button"]:has-text("ott"), button:has-text("ott"), button:has-text("Ultimi")').first
        if d_btn.count() > 0:
            d_btn.click()
            time.sleep(2)
            oggi_label = page.locator('label:has-text("Oggi"), :text-is("Oggi")').first
            if oggi_label.count() > 0:
                oggi_label.click()
                time.sleep(1)
            agg_btn = page.locator('button:has-text("Aggiorna")').last
            if agg_btn.count() > 0:
                agg_btn.click()
                time.sleep(5)

        # 2. Aggiorna tabella
        ref = page.locator('[aria-label="Aggiorna dati tabella"]').first
        if ref.count() > 0:
            ref.click()
            time.sleep(5)

        # 3. Scorri la tabella orizzontalmente
        page.evaluate("""() => {
            const scrollers = document.querySelectorAll('div[class*="scroll"], div[role="grid"], div[role="table"], div[style*="overflow"]');
            for (const s of scrollers) {
                if (s.scrollWidth > s.clientWidth) {
                    s.scrollLeft = 800;
                }
            }
        }""")
        time.sleep(2)
        page.screenshot(path=str(PROJECT_ROOT / "meta" / "today_campaigns_scrolled.png"))

        # Estrai colonne e celle
        data = page.evaluate("""() => {
            const headers = Array.from(document.querySelectorAll('div[role="columnheader"]')).map(h => h.innerText.trim().replace(/\\n/g, ' '));
            const rows = Array.from(document.querySelectorAll('div[role="row"]')).map(r => {
                const cells = Array.from(r.querySelectorAll('div[role="gridcell"]')).map(c => c.innerText.trim().replace(/\\n/g, ' '));
                return cells;
            });
            return { headers, rows };
        }""")

        print("\n--- DATI LIVE CAMPAGNA OGGI ---")
        print("Headers:", data["headers"])
        for idx, r in enumerate(data["rows"]):
            print(f"Row {idx}: {r}")

        # Ora livello Inserzioni
        print("\n--- PASSO A LIVELLO INSERZIONI ---")
        ads_tab = page.locator('text="Inserzioni", div[role="tab"]:has-text("Inserzioni")').first
        if ads_tab.count() > 0:
            ads_tab.click()
            time.sleep(5)

            # Rinfresca
            ref = page.locator('[aria-label="Aggiorna dati tabella"]').first
            if ref.count() > 0:
                ref.click()
                time.sleep(4)

            # Scroll destra
            page.evaluate("""() => {
                const scrollers = document.querySelectorAll('div[class*="scroll"], div[role="grid"], div[role="table"], div[style*="overflow"]');
                for (const s of scrollers) {
                    if (s.scrollWidth > s.clientWidth) {
                        s.scrollLeft = 800;
                    }
                }
            }""")
            time.sleep(2)
            page.screenshot(path=str(PROJECT_ROOT / "meta" / "today_ads_scrolled.png"))

            ads_data = page.evaluate("""() => {
                const headers = Array.from(document.querySelectorAll('div[role="columnheader"]')).map(h => h.innerText.trim().replace(/\\n/g, ' '));
                const rows = Array.from(document.querySelectorAll('div[role="row"]')).map(r => {
                    const cells = Array.from(r.querySelectorAll('div[role="gridcell"]')).map(c => c.innerText.trim().replace(/\\n/g, ' '));
                    return cells;
                });
                return { headers, rows };
            }""")

            print("Ads Headers:", ads_data["headers"])
            for idx, r in enumerate(ads_data["rows"]):
                print(f"Ad Row {idx}: {r}")

    finally:
        context.close()

if __name__ == "__main__":
    run()

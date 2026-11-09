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
        time.sleep(6)

        # Assicurati intervallo massimo
        date_btn = page.locator('button:has-text("Intervallo"), div[role="button"]:has-text("Intervallo")').first
        if date_btn.count() == 0:
            # Apri e seleziona
            d_btn = page.locator('button:has-text("ott"), div[role="button"]:has-text("ott"), button:has-text("Ultimi"), div[role="button"]:has-text("Ultimi")').first
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

        # Estrai tutti i dati della tabella
        table_data = page.evaluate("""() => {
            const headers = Array.from(document.querySelectorAll('div[role="columnheader"]')).map(h => h.innerText.trim().replace(/\\n/g, ' '));
            const rows = Array.from(document.querySelectorAll('div[role="row"]')).map(r => {
                const cells = Array.from(r.querySelectorAll('div[role="gridcell"]')).map(c => c.innerText.trim().replace(/\\n/g, ' '));
                return cells;
            });
            return { headers, rows };
        }""")

        print("=== COLONNE TROVATE ===")
        print(table_data["headers"])

        print("\n=== RIGHE TABELLA ===")
        for r_idx, r in enumerate(table_data["rows"]):
            if any(r):
                print(f"Row {r_idx}: {r}")

        # Seleziona anche livello Campagne e Gruppi di inserzioni
        # Clicca su tab Campagne
        camp_tab = page.locator('button:has-text("Campagne"), div[role="tab"]:has-text("Campagne")').first
        if camp_tab.count() > 0:
            camp_tab.click()
            time.sleep(3)
            camp_data = page.evaluate("""() => {
                return Array.from(document.querySelectorAll('div[role="row"]')).map(r => {
                    return Array.from(r.querySelectorAll('div[role="gridcell"]')).map(c => c.innerText.trim().replace(/\\n/g, ' '));
                });
            }""")
            print("\n=== LIVELLO CAMPAGNE ===")
            for r in camp_data:
                if any(r):
                    print("Campagna:", r)

    finally:
        context.close()

if __name__ == "__main__":
    run()

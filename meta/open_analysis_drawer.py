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
    print("APERTURA PANNELLO ANALISI E PRESTAZIONI CAMPAGNA")
    print("=" * 60)

    context = launch_meta_browser(headless=True)
    page = context.pages[0] if context.pages else context.new_page()

    try:
        url = f"https://adsmanager.facebook.com/adsmanager/manage/campaigns?act={AD_ACCOUNT_ID}"
        page.goto(url, wait_until="domcontentloaded")
        time.sleep(6)

        # 1. Imposta data su Intervallo massimo
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

        # 2. Seleziona la riga della campagna Rikrestin
        chk = page.locator('input[type="checkbox"]').nth(1)
        if chk.count() > 0:
            chk.click(force=True)
            time.sleep(1)

        # 3. Clicca sul pulsante 'Analizza'
        analizza_btn = page.locator('button:has-text("Analizza"), div[role="button"]:has-text("Analizza")').first
        if analizza_btn.count() == 0:
            # Cerca l'icona grafico nella barra a destra
            analizza_btn = page.locator('[aria-label*="Analizza"], [aria-label*="Grafici"]').first
        print(f"Pulsante Analizza: {analizza_btn.count()}")
        if analizza_btn.count() > 0:
            analizza_btn.click()
            time.sleep(5)

        page.screenshot(path=str(PROJECT_ROOT / "meta" / "analysis_drawer_panel.png"))

        # Estrai testo del pannello laterale
        drawer = page.locator('div[role="region"], div[class*="drawer"], div[class*="sidePanel"]').first
        if drawer.count() > 0:
            print("\n--- TESTO PANNELLO PRESTAZIONI ---")
            for line in [l.strip() for l in drawer.inner_text().splitlines() if l.strip()][:50]:
                print(line)
        else:
            print("\n--- TESTO BODY ---")
            for line in [l.strip() for l in page.locator("body").inner_text().splitlines() if l.strip()][:50]:
                print(line)

    finally:
        context.close()

if __name__ == "__main__":
    run()

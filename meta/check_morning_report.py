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
    print("REPORT MATTUTINO META ADS MANAGER (18 OTTOBRE 2026)")
    print(f"Ad Account ID: {AD_ACCOUNT_ID}")
    print("=" * 60)

    context = launch_meta_browser(headless=True)
    page = context.pages[0] if context.pages else context.new_page()

    try:
        url = f"https://adsmanager.facebook.com/adsmanager/manage/campaigns?act={AD_ACCOUNT_ID}"
        print(f"Navigazione a: {url}")
        page.goto(url, wait_until="domcontentloaded")
        time.sleep(6)

        # Chiudi pannelli laterali o alert se ci sono
        page.keyboard.press("Escape")
        time.sleep(1)

        # 1. Seleziona filtro data: Durata massima / Ultimi 7 giorni per includere ieri e oggi
        print("Imposto filtro data su Durata massima o Ultimi 7 giorni...")
        date_btn = page.locator('button:has-text("Ultimi"), div[role="button"]:has-text("Ultimi"), button:has-text("Oggi"), div[role="button"]:has-text("Oggi")').first
        if date_btn.count() > 0:
            date_btn.click()
            time.sleep(1)
            # Cerca opzione 'Durata massima' o 'Ultimi 7 giorni' o 'Oggi'
            opt = page.locator('text="Durata massima", text="Durata complessiva", text="Ultimi 7 giorni"').first
            if opt.count() > 0:
                print(f"Seleziono opzione data: {opt.inner_text()}")
                opt.click()
                time.sleep(3)

        # Screenshot a livello Campagne
        shot_camp = PROJECT_ROOT / "meta" / "morning_campaigns_report.png"
        page.screenshot(path=str(shot_camp))
        print(f"Screenshot Campagne salvato in: {shot_camp}")

        # Stampa righe tabella Campagne
        print("\n--- RIGHE TABELLA CAMPAGNE ---")
        rows = page.locator('div[role="row"]').all()
        for idx, r in enumerate(rows):
            txt = r.inner_text().strip().replace('\n', ' | ')
            if txt and ('Rikrestin' in txt or 'Campagna' in txt or 'Vendite' in txt or 'Attiva' in txt or 'Importo' in txt):
                print(f"Campagna [{idx}]: {txt}")

        # 2. Vai a livello Inserzioni
        print("\n--- NAVIGAZIONE A LIVELLO INSERZIONI ---")
        ads_tab = page.locator('div[role="tab"]:has-text("Inserzioni"), button:has-text("Inserzioni")').first
        if ads_tab.count() > 0:
            ads_tab.click()
            time.sleep(4)
        else:
            page.goto(f"https://adsmanager.facebook.com/adsmanager/manage/ads?act={AD_ACCOUNT_ID}", wait_until="domcontentloaded")
            time.sleep(6)

        shot_ads = PROJECT_ROOT / "meta" / "morning_ads_report.png"
        page.screenshot(path=str(shot_ads))
        print(f"Screenshot Inserzioni salvato in: {shot_ads}")

        ad_rows = page.locator('div[role="row"]').all()
        for idx, r in enumerate(ad_rows):
            txt = r.inner_text().strip().replace('\n', ' | ')
            if txt and ('Vendite' in txt or 'Inserzione' in txt or 'Attiva' in txt or 'elaborazione' in txt or 'Importo' in txt or 'Rikrestin' in txt):
                print(f"Inserzione [{idx}]: {txt}")

    finally:
        context.close()

if __name__ == "__main__":
    run()

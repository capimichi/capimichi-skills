import sys
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from meta.paths import get_cache_dir
from meta.browser import launch_meta_browser

AD_ACCOUNT_ID = "1116925509636183"

def check_live_metrics():
    cache_dir = get_cache_dir()
    print("=" * 60)
    print("CONTROLLO METRICHE LIVE META ADS MANAGER")
    print(f"Ad Account ID: {AD_ACCOUNT_ID}")
    print("=" * 60)

    context = launch_meta_browser(headless=True)
    page = context.pages[0] if context.pages else context.new_page()

    try:
        url = f"https://adsmanager.facebook.com/adsmanager/manage/campaigns?act={AD_ACCOUNT_ID}"
        print(f"Navigazione a: {url}")
        page.goto(url, wait_until="domcontentloaded")
        time.sleep(6)

        # Seleziona filtro data: Oggi
        date_btn = page.locator('button:has-text("Ultimi"), div[role="button"]:has-text("Ultimi"), div[role="button"]:has-text("Oggi"), button:has-text("Oggi")').first
        if date_btn.count() > 0:
            if "Oggi" not in date_btn.inner_text():
                date_btn.click()
                time.sleep(1)
                oggi_opt = page.locator('text="Oggi"').first
                if oggi_opt.count() > 0:
                    oggi_opt.click()
                    time.sleep(3)

        # Assicurati di essere su Tutte le inserzioni o rimuovi filtri
        filtro_attivo = page.locator('text=Pubblicazione effettuata').first
        if filtro_attivo.count() > 0:
            print("Filtro 'Pubblicazione effettuata' attivo.")

        # Screenshot Campagne
        shot_camp = cache_dir / "live_report_campaigns.png"
        page.screenshot(path=str(shot_camp))
        print(f"Screenshot Campagne salvato: {shot_camp}")

        # Dump righe Campagne
        print("\n--- RIGHE TABELLA CAMPAGNE ---")
        rows = page.locator('div[role="row"], tr').all()
        for i, r in enumerate(rows):
            txt = r.inner_text().strip().replace('\n', ' | ')
            if txt and ('Rikrestin' in txt or 'Campagna' in txt or 'Vendite' in txt):
                print(f"[{i}] {txt}")

        # Vai su Inserzioni
        print("\nNavigazione a livello Inserzioni...")
        ads_tab = page.locator('div[role="tab"]:has-text("Inserzioni"), button:has-text("Inserzioni")').first
        if ads_tab.count() > 0:
            ads_tab.click()
            time.sleep(4)
        else:
            page.goto(f"https://adsmanager.facebook.com/adsmanager/manage/ads?act={AD_ACCOUNT_ID}", wait_until="domcontentloaded")
            time.sleep(6)

        shot_ads = cache_dir / "live_report_ads.png"
        page.screenshot(path=str(shot_ads))
        print(f"Screenshot Inserzioni salvato: {shot_ads}")

        print("\n--- RIGHE TABELLA INSERZIONI ---")
        ad_rows = page.locator('div[role="row"], tr').all()
        for i, r in enumerate(ad_rows):
            txt = r.inner_text().strip().replace('\n', ' | ')
            if txt and ('Rikrestin' in txt or 'Inserzione' in txt or 'Vendite' in txt or 'Attiva' in txt or 'controllo' in txt):
                print(f"[{i}] {txt}")

    finally:
        context.close()

if __name__ == "__main__":
    check_live_metrics()

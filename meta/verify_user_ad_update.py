import sys
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from meta.browser import launch_meta_browser

AD_ACCOUNT_ID = "1116925509636183"

def verify():
    print("=" * 60)
    print("VERIFICA STATO AGGIORNATO CAMPAGNA E INSERZIONE")
    print("=" * 60)

    context = launch_meta_browser(headless=True)
    page = context.pages[0] if context.pages else context.new_page()

    try:
        url = f"https://adsmanager.facebook.com/adsmanager/manage/campaigns?act={AD_ACCOUNT_ID}"
        print(f"Navigazione a: {url}")
        page.goto(url, wait_until="networkidle")
        time.sleep(5)

        # 1. Screenshot e stato Campagne
        page.screenshot(path=str(PROJECT_ROOT / "meta" / "verified_campaigns.png"))
        print("\n=== LIVELLO CAMPAGNE ===")
        rows = page.locator('div[role="row"]').all()
        for idx, r in enumerate(rows):
            txt = r.inner_text().strip().replace('\n', ' | ')
            if 'Rikrestin' in txt:
                print(f"Campagna: {txt}")

        # 2. Clicca sulla campagna Rikrestin
        camp = page.locator('text="Rikrestin 2x49 - Test Vendite"').first
        if camp.count() > 0:
            camp.click()
            time.sleep(3)

        # 3. Tab Inserzioni
        print("\n=== LIVELLO INSERZIONI ===")
        ads_tab = page.locator('text="Inserzioni per 1 Campagna", div[role="tab"]:has-text("Inserzioni")').first
        if ads_tab.count() > 0:
            ads_tab.click()
            time.sleep(4)

        page.screenshot(path=str(PROJECT_ROOT / "meta" / "verified_ads.png"))
        ad_rows = page.locator('div[role="row"]').all()
        for idx, r in enumerate(ad_rows):
            txt = r.inner_text().strip().replace('\n', ' | ')
            if txt and ('Vendite' in txt or 'Inserzione' in txt or 'Rikrestin' in txt or 'Attiva' in txt or 'controllo' in txt or 'bozza' in txt):
                print(f"Inserzione [{idx}]: {txt}")

        # 4. Apri anteprima o dettagli inserzione se possibile
        thumb = page.locator('img[src*="scontent"], div[role="gridcell"]:has-text("Nuova inserzione")').first
        if thumb.count() > 0:
            thumb.hover()
            time.sleep(1)
            anteprima_btn = page.locator('button:has-text("Anteprima"), div[role="button"]:has-text("Anteprima"), a:has-text("Anteprima")').first
            if anteprima_btn.count() > 0:
                print("\nClick Anteprima inserzione...")
                anteprima_btn.click()
                time.sleep(4)
                page.screenshot(path=str(PROJECT_ROOT / "meta" / "verified_ad_preview.png"))
                print("Screenshot anteprima salvato in meta/verified_ad_preview.png")

    finally:
        context.close()

if __name__ == "__main__":
    verify()

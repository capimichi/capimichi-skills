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
    print("CONTROLLO METRICHE CON FILTRO DATA CORRETTO")
    print("=" * 60)

    context = launch_meta_browser(headless=True)
    page = context.pages[0] if context.pages else context.new_page()

    try:
        url = f"https://adsmanager.facebook.com/adsmanager/manage/campaigns?act={AD_ACCOUNT_ID}"
        page.goto(url, wait_until="domcontentloaded")
        time.sleep(6)

        # 1. Imposta data su "Durata massima" per vedere TUTTO (ieri + oggi)
        date_btn = page.locator('button:has-text("Ultimi"), div[role="button"]:has-text("Ultimi"), button:has-text("Oggi")').first
        if date_btn.count() > 0:
            print(f"Click selettore data ({date_btn.inner_text().strip()})...")
            date_btn.click()
            time.sleep(2)
            
            # Cerca opzione Durata massima
            life = page.locator('text="Durata massima"').first
            if life.count() == 0:
                life = page.locator('text="Durata complessiva"').first
            if life.count() == 0:
                life = page.locator('text="Oggi"').first

            if life.count() > 0:
                print(f"Click su opzione: {life.inner_text()}")
                life.click()
                time.sleep(4)

        # Salva screenshot e dump tabella Campagne
        shot_camp = PROJECT_ROOT / "meta" / "campaigns_lifetime_report.png"
        page.screenshot(path=str(shot_camp))
        print("Screenshot salvato in:", shot_camp)

        print("\n=== METRICHE CAMPAGNE ===")
        rows = page.locator('div[role="row"]').all()
        for idx, r in enumerate(rows):
            txt = r.inner_text().strip().replace('\n', ' | ')
            if 'Rikrestin' in txt:
                print(f"Campagna: {txt}")

        # 2. Vai a Inserzioni
        page.goto(f"https://adsmanager.facebook.com/adsmanager/manage/ads?act={AD_ACCOUNT_ID}", wait_until="domcontentloaded")
        time.sleep(5)

        # Seleziona di nuovo Durata massima se necessario
        date_btn2 = page.locator('button:has-text("Ultimi"), div[role="button"]:has-text("Ultimi"), button:has-text("Oggi")').first
        if date_btn2.count() > 0 and "Durata" not in date_btn2.inner_text():
            date_btn2.click()
            time.sleep(1)
            life = page.locator('text="Durata massima", text="Durata complessiva", text="Oggi"').first
            if life.count() > 0:
                life.click()
                time.sleep(3)

        shot_ads = PROJECT_ROOT / "meta" / "ads_lifetime_report.png"
        page.screenshot(path=str(shot_ads))
        print("Screenshot Inserzioni salvato in:", shot_ads)

        print("\n=== METRICHE INSERZIONI ===")
        rows = page.locator('div[role="row"]').all()
        for idx, r in enumerate(rows):
            txt = r.inner_text().strip().replace('\n', ' | ')
            if 'Vendite' in txt or 'Rikrestin' in txt or 'Attiva' in txt:
                print(f"Inserzione [{idx}]: {txt}")

    finally:
        context.close()

if __name__ == "__main__":
    run()

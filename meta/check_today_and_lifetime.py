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
    print("CONTROLLO METRICHE OGGI E COMPLESSIVE")
    print("=" * 60)

    context = launch_meta_browser(headless=True)
    page = context.pages[0] if context.pages else context.new_page()

    try:
        url = f"https://adsmanager.facebook.com/adsmanager/manage/ads?act={AD_ACCOUNT_ID}"
        page.goto(url, wait_until="domcontentloaded")
        time.sleep(6)

        # 1. Imposta data su "Oggi"
        date_btn = page.locator('button:has-text("17 ott"), button:has-text("Ultimi"), div[role="button"]:has-text("17 ott"), div[role="button"]:has-text("Ultimi")').first
        if date_btn.count() > 0:
            print(f"Click selettore data ({date_btn.inner_text().strip()})...")
            date_btn.click()
            time.sleep(1)
            oggi_opt = page.locator('div[role="option"]:has-text("Oggi"), text="Oggi"').first
            if oggi_opt.count() > 0:
                print("Seleziono 'Oggi'...")
                oggi_opt.click()
                time.sleep(4)

        # Screenshot Oggi
        shot_today = PROJECT_ROOT / "meta" / "metrics_today.png"
        page.screenshot(path=str(shot_today))
        print("Screenshot Oggi salvato in:", shot_today)

        # Dump righe per Oggi
        print("\n--- METRICHE OGGI (18 OTT) ---")
        rows = page.locator('div[role="row"]').all()
        for idx, r in enumerate(rows):
            txt = r.inner_text().strip().replace('\n', ' | ')
            if 'Vendite' in txt or 'Rikrestin' in txt:
                print(f"Row [{idx}]: {txt}")

        # 2. Imposta data su "Durata massima"
        date_btn = page.locator('button:has-text("Oggi"), div[role="button"]:has-text("Oggi")').first
        if date_btn.count() > 0:
            date_btn.click()
            time.sleep(1)
            life_opt = page.locator('div[role="option"]:has-text("Durata massima"), text="Durata massima", text="Durata complessiva"').first
            if life_opt.count() > 0:
                print("Seleziono 'Durata massima'...")
                life_opt.click()
                time.sleep(4)

        shot_lifetime = PROJECT_ROOT / "meta" / "metrics_lifetime.png"
        page.screenshot(path=str(shot_lifetime))
        print("Screenshot Lifetime salvato in:", shot_lifetime)

        print("\n--- METRICHE DURATA COMPLESSIVA ---")
        rows = page.locator('div[role="row"]').all()
        for idx, r in enumerate(rows):
            txt = r.inner_text().strip().replace('\n', ' | ')
            if 'Vendite' in txt or 'Rikrestin' in txt:
                print(f"Lifetime Row [{idx}]: {txt}")

    finally:
        context.close()

if __name__ == "__main__":
    run()

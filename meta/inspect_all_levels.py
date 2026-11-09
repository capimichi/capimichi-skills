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
        # 1. Livello Gruppi di Inserzioni
        url_adsets = f"https://adsmanager.facebook.com/adsmanager/manage/adsets?act={AD_ACCOUNT_ID}"
        print(f"Navigazione a Gruppi di inserzioni: {url_adsets}")
        page.goto(url_adsets, wait_until="domcontentloaded")
        time.sleep(6)

        page.screenshot(path=str(PROJECT_ROOT / "meta" / "adsets_status.png"))
        print("\n--- STATO GRUPPO INSERZIONI ---")
        rows = page.locator('div[role="row"]').all()
        for idx, r in enumerate(rows):
            txt = r.inner_text().strip().replace('\n', ' | ')
            if 'Vendite' in txt or 'Gruppo' in txt or 'Attiv' in txt:
                print(f"AdSet [{idx}]: {txt}")

        # Controlliamo anche notifiche account in alto a sinistra (icona campanella con badge rosso "2")
        bell = page.locator('[aria-label*="Notifiche"], div[role="button"]:has(span:has-text("2")), button:has(span:has-text("2"))').first
        print(f"\nNotifiche badge: {bell.inner_text() if bell.count() > 0 else 'Nessun badge'}")

        # Account status overview
        page.goto(f"https://adsmanager.facebook.com/adsmanager/manage/account_overview?act={AD_ACCOUNT_ID}", wait_until="domcontentloaded")
        time.sleep(5)
        page.screenshot(path=str(PROJECT_ROOT / "meta" / "account_overview.png"))
        print("\n--- PANORAMICA ACCOUNT ---")
        overview_text = page.locator('main, body').first.inner_text()
        for line in overview_text.splitlines()[:25]:
            if line.strip():
                print(line.strip())

    finally:
        context.close()

if __name__ == "__main__":
    run()

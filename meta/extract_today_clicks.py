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
    print("ESTRAZIONE PRESTAZIONI E CLIC (2400px)")
    print("=" * 60)

    context = launch_meta_browser(
        headless=True,
        args=["--window-size=2400,1080"],
        viewport={"width": 2400, "height": 1080}
    )
    page = context.pages[0] if context.pages else context.new_page()

    try:
        url = f"https://adsmanager.facebook.com/adsmanager/manage/campaigns?act={AD_ACCOUNT_ID}"
        page.goto(url, wait_until="domcontentloaded")
        time.sleep(5)
        page.keyboard.press("Escape")
        time.sleep(1)

        # 1. Imposta data su Oggi se non già impostata
        date_txt = page.locator('div[role="button"]:has-text("Oggi"), button:has-text("Oggi")').count()
        if date_txt == 0:
            d_btn = page.locator('div[role="button"]:has-text("ott"), button:has-text("ott")').first
            if d_btn.count() > 0:
                d_btn.click()
                time.sleep(1)
                page.locator('label:has-text("Oggi"), :text-is("Oggi")').first.click()
                time.sleep(1)
                page.locator('button:has-text("Aggiorna")').last.click()
                time.sleep(4)

        # 2. Clicca sul dropdown 'Colonne'
        cols_btn = page.locator('button:has-text("Colonne"), div[role="button"]:has-text("Colonne")').first
        if cols_btn.count() > 0:
            cols_btn.click()
            time.sleep(2)
            perf_opt = page.locator('div[role="menuitem"]:has-text("Prestazioni e clic"), text="Prestazioni e clic"').first
            if perf_opt.count() > 0:
                perf_opt.click()
                time.sleep(4)

        # 3. Aggiorna dati
        ref = page.locator('[aria-label="Aggiorna dati tabella"]').first
        if ref.count() > 0:
            ref.click()
            time.sleep(5)

        page.screenshot(path=str(PROJECT_ROOT / "meta" / "today_prestazioni_e_clic.png"))
        print("Screenshot salvato in meta/today_prestazioni_e_clic.png")

        # Tab Inserzioni
        ads_tab = page.locator('text="Inserzioni", div[role="tab"]:has-text("Inserzioni")').first
        if ads_tab.count() > 0:
            ads_tab.click()
            time.sleep(4)
            page.screenshot(path=str(PROJECT_ROOT / "meta" / "today_ads_prestazioni_e_clic.png"))

    finally:
        context.close()

if __name__ == "__main__":
    run()

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
    print("LETTURA COMPLETA RISOLUZIONE ULTRA-WIDE (2400px)")
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

        # 2. Aggiorna dati
        ref = page.locator('[aria-label="Aggiorna dati tabella"]').first
        if ref.count() > 0:
            ref.click()
            time.sleep(5)

        page.screenshot(path=str(PROJECT_ROOT / "meta" / "today_campaigns_2400.png"))
        print("Screenshot salvato in meta/today_campaigns_2400.png")

        # 3. Tab Inserzioni
        ads_tab = page.locator('text="Inserzioni", div[role="tab"]:has-text("Inserzioni")').first
        if ads_tab.count() > 0:
            ads_tab.click()
            time.sleep(5)
            ref = page.locator('[aria-label="Aggiorna dati tabella"]').first
            if ref.count() > 0:
                ref.click()
                time.sleep(4)
            page.screenshot(path=str(PROJECT_ROOT / "meta" / "today_ads_2400.png"))
            print("Screenshot salvato in meta/today_ads_2400.png")

        # Estrai testo
        text = page.locator('body').inner_text()
        with open(PROJECT_ROOT / "meta" / "today_2400_text.txt", "w", encoding="utf-8") as f:
            f.write(text)

        print("\n--- TESTO RIGHE TABELLA ---")
        rows = page.locator('div[role="row"]').all()
        for idx, r in enumerate(rows):
            print(f"Row [{idx}]: {r.inner_text().strip().replace(chr(10), ' | ')}")

    finally:
        context.close()

if __name__ == "__main__":
    run()

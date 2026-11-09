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
    print("ESTRAZIONE METRICHE OGGI (18 OTTOBRE 2026)")
    print("=" * 60)

    context = launch_meta_browser(
        headless=True,
        args=["--window-size=1600,1000"],
        viewport={"width": 1600, "height": 1000}
    )
    page = context.pages[0] if context.pages else context.new_page()

    try:
        url = f"https://adsmanager.facebook.com/adsmanager/manage/campaigns?act={AD_ACCOUNT_ID}"
        page.goto(url, wait_until="domcontentloaded")
        time.sleep(5)
        page.keyboard.press("Escape")
        time.sleep(1)

        # 1. Clicca sul selettore della data
        date_btn = page.locator('button[aria-label*="Data"], div[role="button"]:has-text("ott"), button:has-text("ott"), button:has-text("Ultimi")').first
        if date_btn.count() > 0:
            print("Clicco selettore data:", date_btn.inner_text().strip())
            date_btn.click()
            time.sleep(2)

            # Clicca su 'Oggi'
            oggi_opt = page.locator('text="Oggi", div[role="option"]:has-text("Oggi")').first
            if oggi_opt.count() > 0:
                print("Seleziono 'Oggi'...")
                oggi_opt.click()
                time.sleep(1)
            
            # Clicca Aggiorna se presente
            agg = page.locator('button:has-text("Aggiorna")').first
            if agg.count() > 0:
                agg.click()
                time.sleep(3)

        # 2. Aggiorna dati tabella
        refresh = page.locator('[aria-label="Aggiorna dati tabella"]').first
        if refresh.count() > 0:
            refresh.click()
            time.sleep(5)

        page.screenshot(path=str(PROJECT_ROOT / "meta" / "today_campaign_table.png"))
        print("Screenshot campagna salvato in meta/today_campaign_table.png")

        # 3. Seleziona preset colonne 'Prestazioni e clic'
        cols_btn = page.locator('button:has-text("Colonne"), div[role="button"]:has-text("Colonne")').first
        if cols_btn.count() > 0:
            cols_btn.click()
            time.sleep(1)
            perf = page.locator('div[role="menuitem"]:has-text("Prestazioni e clic"), div[role="option"]:has-text("Prestazioni e clic"), text="Prestazioni e clic"').first
            if perf.count() > 0:
                perf.click()
                time.sleep(4)

        page.screenshot(path=str(PROJECT_ROOT / "meta" / "today_campaign_prestazioni.png"))

        # Scorri la tabella a destra per leggere tutte le colonne
        grid = page.locator('div[role="grid"]').first
        if grid.count() > 0:
            try:
                grid.evaluate("el => el.scrollLeft = 800")
                time.sleep(2)
                page.screenshot(path=str(PROJECT_ROOT / "meta" / "today_table_scrolled.png"))
            except:
                pass

        # 4. Spostati sulla tab Inserzioni
        ads_tab = page.locator('button:has-text("Inserzioni"), div[role="tab"]:has-text("Inserzioni")').first
        if ads_tab.count() > 0:
            ads_tab.click()
            time.sleep(5)
            page.screenshot(path=str(PROJECT_ROOT / "meta" / "today_ads_table.png"))

        # Estrai tutto il testo della tabella e della pagina
        text = page.locator('body').inner_text()
        with open(PROJECT_ROOT / "meta" / "today_full_text.txt", "w", encoding="utf-8") as f:
            f.write(text)

        print("\n--- RIGHE TABELLA E DATI ESTRATTI ---")
        lines = [l.strip() for l in text.splitlines() if l.strip()]
        for l in lines:
            if any(k in l.lower() for k in ["rikrestin", "speso", "copertura", "impression", "click", "cpc", "ctr", "risultati", "acquisti", "€"]):
                print("->", l)

    finally:
        context.close()

if __name__ == "__main__":
    run()

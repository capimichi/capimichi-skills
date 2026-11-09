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
    print("ESTRAZIONE KPI E METRICHE DI MIGLIORAMENTO (LIVE)")
    print("=" * 60)

    context = launch_meta_browser(headless=True)
    page = context.pages[0] if context.pages else context.new_page()

    try:
        url = f"https://adsmanager.facebook.com/adsmanager/manage/campaigns?act={AD_ACCOUNT_ID}"
        page.goto(url, wait_until="domcontentloaded")
        time.sleep(6)

        # 1. Seleziona colonne "Prestazioni e clic" se possibile
        cols_btn = page.locator('button:has-text("Colonne"), div[role="button"]:has-text("Colonne")').first
        if cols_btn.count() > 0:
            cols_btn.click()
            time.sleep(1)
            perf_opt = page.locator('div[role="menuitem"]:has-text("Prestazioni e clic"), div[role="option"]:has-text("Prestazioni e clic")').first
            if perf_opt.count() > 0:
                print("Seleziono preset colonne: Prestazioni e clic...")
                perf_opt.click()
                time.sleep(3)

        # 2. Imposta data su Intervallo massimo
        d_btn = page.locator('button:has-text("ott"), div[role="button"]:has-text("ott"), button:has-text("Ultimi"), div[role="button"]:has-text("Ultimi")').first
        if d_btn.count() > 0:
            d_btn.click()
            time.sleep(1)
            opt = page.locator(':text-is("Intervallo massimo"), div[role="option"]:has-text("Intervallo massimo")').first
            if opt.count() > 0:
                opt.click()
                time.sleep(1)
                agg = page.locator('button:has-text("Aggiorna")').first
                if agg.count() > 0:
                    agg.click()
                    time.sleep(5)

        # Rinfresca dati
        refresh_btn = page.locator('[aria-label="Aggiorna dati tabella"]').first
        if refresh_btn.count() > 0:
            refresh_btn.click()
            time.sleep(5)

        page.screenshot(path=str(PROJECT_ROOT / "meta" / "live_kpis_table.png"))

        # Estrai testo tabella e colonne
        txt = page.locator('body').inner_text()
        print("\n--- TESTO GENERALE KPI ---")
        lines = [l.strip() for l in txt.splitlines() if l.strip()]
        for l in lines[:60]:
            print(l)

        # Apri il pannello laterale di analisi grafica per i dati demografici / CTR / CPC
        chart_icon = page.locator('div[role="toolbar"] [aria-label*="Grafic"], [aria-label*="Visualizza grafici"], div[class*="sideRail"] div[role="button"]').first
        if chart_icon.count() > 0:
            chart_icon.click()
            time.sleep(4)
            vis_btn = page.locator('button:has-text("Visualizza"), div[role="button"]:has-text("Visualizza")').first
            if vis_btn.count() > 0:
                vis_btn.click()
                time.sleep(2)
            page.screenshot(path=str(PROJECT_ROOT / "meta" / "live_kpis_chart.png"))

            print("\n--- TESTO DETTAGLIATO GRAFICO KPI ---")
            lines_chart = [l.strip() for l in page.locator('body').inner_text().splitlines() if l.strip()]
            for l in lines_chart[:60]:
                print(l)

    finally:
        context.close()

if __name__ == "__main__":
    run()

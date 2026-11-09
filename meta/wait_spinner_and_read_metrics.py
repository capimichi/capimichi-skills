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
    print("ATTESA CARICAMENTO DATI TABELLA E LETTURA METRICHE")
    print("=" * 60)

    context = launch_meta_browser(headless=True)
    page = context.pages[0] if context.pages else context.new_page()

    try:
        url = f"https://adsmanager.facebook.com/adsmanager/manage/ads?act={AD_ACCOUNT_ID}"
        page.goto(url, wait_until="domcontentloaded")
        print("Pagina caricata, attendo caricamento dati tabella...")
        
        # Attesa fino a 20 secondi per la scomparsa dello spinner o caricamento dei dati
        for i in range(10):
            time.sleep(2)
            spinner = page.locator('[aria-label*="Caricamento"], svg.spin, div[role="progressbar"]')
            count = spinner.count()
            print(f"[{i*2}s] Spinner presenti: {count}")
            # Controlla se la riga dell'inserzione ha più testo
            rows = page.locator('div[role="row"]').all()
            if len(rows) > 1:
                txt = rows[1].inner_text()
                if any(char.isdigit() for char in txt):
                    print("Dati numerici rilevati nella riga!")
                    break

        page.screenshot(path=str(PROJECT_ROOT / "meta" / "loaded_metrics_table.png"))

        # Stampa testo completo delle righe
        rows = page.locator('div[role="row"]').all()
        print(f"\nRighe totali: {len(rows)}")
        for idx, r in enumerate(rows):
            print(f"\nRow [{idx}]:")
            print(r.inner_text().replace("\n", " | "))

        # Estrazione Campagna e Gruppo inserzioni
        print("\n--- LIVELLO CAMPAGNE ---")
        page.goto(f"https://adsmanager.facebook.com/adsmanager/manage/campaigns?act={AD_ACCOUNT_ID}", wait_until="domcontentloaded")
        time.sleep(8)
        page.screenshot(path=str(PROJECT_ROOT / "meta" / "loaded_campaigns_table.png"))
        c_rows = page.locator('div[role="row"]').all()
        for idx, r in enumerate(c_rows):
            print(f"Campagna [{idx}]: {r.inner_text().replace('\n', ' | ')}")

    finally:
        context.close()

if __name__ == "__main__":
    run()

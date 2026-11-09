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
    print("CLICK DEFINITIVO PAGA ORA SALDO 3,03 €")
    print("=" * 60)

    context = launch_meta_browser(headless=True)
    page = context.pages[0] if context.pages else context.new_page()

    try:
        url = f"https://adsmanager.facebook.com/adsmanager/billing_hub/payment_settings?asset_id={AD_ACCOUNT_ID}"
        print(f"1. Navigazione a: {url}")
        page.goto(url, wait_until="domcontentloaded")
        time.sleep(6)

        # Clicca sul pulsante Paga ora nella pagina
        pay_btn = page.locator('button:has-text("Paga ora"), div[role="button"]:has-text("Paga ora")').first
        print(f"Pulsante 'Paga ora' trovato: {pay_btn.count()}")
        pay_btn.click()
        time.sleep(3)

        # Trova il modal specifico Salda l'importo attuale
        modal = page.locator('div[role="dialog"]:has-text("Salda l\'importo attuale")').first
        print(f"Modal 'Salda l\'importo attuale' trovato: {modal.count()}")

        # Trova il pulsante 'Paga ora' dentro questo modal
        modal_pay_btn = modal.locator('button:has-text("Paga ora"), div[role="button"]:has-text("Paga ora")').first
        print(f"Pulsante 'Paga ora' nel modal abilitato: {modal_pay_btn.is_enabled()}")

        modal_pay_btn.click()
        print("Pulsante 'Paga ora' nel modal CLICCATO! In attesa elaborazione pagamento...")
        time.sleep(12)

        page.screenshot(path=str(PROJECT_ROOT / "meta" / "pay_now_processing.png"))

        # Controlla eventuale messaggio di successo o errore
        modal_text = modal.inner_text() if modal.count() > 0 else ""
        print("\n--- TESTO MODAL DOPO IL CLICK ---")
        print(modal_text)

        # Ricarica la pagina per verificare il nuovo saldo
        print("\n2. Verifica nuovo saldo...")
        page.goto(url, wait_until="domcontentloaded")
        time.sleep(6)
        page.screenshot(path=str(PROJECT_ROOT / "meta" / "billing_status_after_pay.png"))

        txt = page.locator("body").inner_text()
        print("\n--- STATO FATTURAZIONE FINALE ---")
        lines = [l.strip() for l in txt.splitlines() if l.strip()]
        for l in lines[:40]:
            print(l)

        # 3. Controlla Gestione Inserzioni
        url_ads = f"https://adsmanager.facebook.com/adsmanager/manage/campaigns?act={AD_ACCOUNT_ID}"
        print(f"\n3. Controllo campagna: {url_ads}")
        page.goto(url_ads, wait_until="domcontentloaded")
        time.sleep(6)
        page.screenshot(path=str(PROJECT_ROOT / "meta" / "campaign_active_after_pay.png"))

        lines_ads = [l.strip() for l in page.locator("body").inner_text().splitlines() if l.strip()]
        for l in lines_ads[:35]:
            print(l)

    finally:
        context.close()

if __name__ == "__main__":
    run()

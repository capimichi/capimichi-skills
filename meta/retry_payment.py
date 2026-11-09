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
    print("RETRY PAGAMENTO SALDO PENDENTE (3,03 €)")
    print("=" * 60)

    context = launch_meta_browser(headless=True)
    page = context.pages[0] if context.pages else context.new_page()

    try:
        url = f"https://adsmanager.facebook.com/adsmanager/billing_hub/payment_settings?asset_id={AD_ACCOUNT_ID}"
        print(f"1. Apertura {url}...")
        page.goto(url, wait_until="domcontentloaded")
        time.sleep(6)

        page.screenshot(path=str(PROJECT_ROOT / "meta" / "payment_screen_before.png"))

        # Cerca pulsante "Paga ora" o "Salda l'importo attuale"
        pay_btn = page.locator('button:has-text("Paga ora"), div[role="button"]:has-text("Paga ora"), button:has-text("Salda l\'importo attuale")').first
        print(f"Pulsante di pagamento trovato: {pay_btn.count()}")
        if pay_btn.count() > 0:
            print(f"Clicco su: '{pay_btn.inner_text().strip()}'")
            pay_btn.click()
            time.sleep(4)

            page.screenshot(path=str(PROJECT_ROOT / "meta" / "payment_modal_opened.png"))

            # Controlla eventuale dialog / modal di conferma pagamento
            dialog = page.locator('div[role="dialog"]').first
            if dialog.count() > 0:
                print("\n--- TESTO MODAL PAGAMENTO ---")
                print(dialog.inner_text())

                # Cerca pulsante di conferma nel dialog (es: "Paga ora", "Effettua pagamento", "Conferma")
                confirm_pay = dialog.locator('button:has-text("Paga"), button:has-text("Conferma"), div[role="button"]:has-text("Paga")').first
                if confirm_pay.count() > 0:
                    print(f"Clicco conferma pagamento: '{confirm_pay.inner_text().strip()}'")
                    confirm_pay.click()
                    time.sleep(8)
                    page.screenshot(path=str(PROJECT_ROOT / "meta" / "payment_processing_result.png"))

        # Ricarica la pagina e verifica saldo
        print("\n2. Verifica stato del saldo e dell'account...")
        page.goto(url, wait_until="domcontentloaded")
        time.sleep(6)
        page.screenshot(path=str(PROJECT_ROOT / "meta" / "payment_screen_after.png"))

        txt = page.locator("body").inner_text()
        print("\n--- TESTO FATTURAZIONE DOPO IL TENTATIVO ---")
        lines = [l.strip() for l in txt.splitlines() if l.strip()]
        for l in lines[:40]:
            print(l)

        # 3. Controlla lo stato della campagna
        url_camp = f"https://adsmanager.facebook.com/adsmanager/manage/campaigns?act={AD_ACCOUNT_ID}"
        print(f"\n3. Controllo stato campagna: {url_camp}")
        page.goto(url_camp, wait_until="domcontentloaded")
        time.sleep(6)
        page.screenshot(path=str(PROJECT_ROOT / "meta" / "campaign_status_after_payment.png"))

        camp_txt = page.locator("body").inner_text()
        print("\n--- STATO CAMPAGNA ---")
        lines_camp = [l.strip() for l in camp_txt.splitlines() if l.strip()]
        for l in lines_camp[:35]:
            print(l)

    finally:
        context.close()

if __name__ == "__main__":
    run()

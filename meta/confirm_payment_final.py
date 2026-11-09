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
    print("CONFERMA FINALE PAGAMENTO 3,03 €")
    print("=" * 60)

    context = launch_meta_browser(headless=True)
    page = context.pages[0] if context.pages else context.new_page()

    try:
        url = f"https://adsmanager.facebook.com/adsmanager/billing_hub/payment_settings?asset_id={AD_ACCOUNT_ID}"
        print(f"1. Navigazione a: {url}")
        page.goto(url, wait_until="domcontentloaded")
        time.sleep(6)

        # 1. Clicca Paga ora nella pagina principale
        pay_btn = page.locator('button:has-text("Paga ora"), div[role="button"]:has-text("Paga ora")').first
        print(f"Pulsante 'Paga ora' in pagina: {pay_btn.count()}")
        pay_btn.click()
        time.sleep(3)

        # 2. Clicca Paga ora nel primo modal
        modal_pay_btn = page.locator('button:has-text("Paga ora"), div[role="button"]:has-text("Paga ora")').last
        print(f"Pulsante 'Paga ora' nel modal: {modal_pay_btn.count()}")
        modal_pay_btn.click()
        time.sleep(3)

        page.screenshot(path=str(PROJECT_ROOT / "meta" / "step2_confirm_screen.png"))

        # 3. Clicca Conferma nella schermata "Controlla il tuo pagamento"
        confirm_btn = page.locator('button:has-text("Conferma"), div[role="button"]:has-text("Conferma")').first
        print(f"Pulsante 'Conferma' trovato: {confirm_btn.count()}")
        if confirm_btn.count() > 0:
            print("Clicco su CONFERMA PAGAMENTO...")
            confirm_btn.click()
            time.sleep(15)

        page.screenshot(path=str(PROJECT_ROOT / "meta" / "after_payment_confirmation.png"))

        # 4. Ricarica e verifica il nuovo saldo
        print("\n2. Verifica stato dopo la transazione...")
        page.goto(url, wait_until="domcontentloaded")
        time.sleep(6)
        page.screenshot(path=str(PROJECT_ROOT / "meta" / "final_billing_status_verified.png"))

        txt = page.locator("body").inner_text()
        print("\n--- STATO FATTURAZIONE DOPO IL SALDO ---")
        lines = [l.strip() for l in txt.splitlines() if l.strip()]
        for l in lines[:40]:
            print(l)

        # 5. Verifica stato della campagna
        url_camp = f"https://adsmanager.facebook.com/adsmanager/manage/campaigns?act={AD_ACCOUNT_ID}"
        page.goto(url_camp, wait_until="domcontentloaded")
        time.sleep(6)
        page.screenshot(path=str(PROJECT_ROOT / "meta" / "campaign_active_resumed.png"))

        txt_camp = page.locator("body").inner_text()
        print("\n--- STATO CAMPAGNA DOPO LO SBLOCCO ---")
        lines_camp = [l.strip() for l in txt_camp.splitlines() if l.strip()]
        for l in lines_camp[:35]:
            print(l)

    finally:
        context.close()

if __name__ == "__main__":
    run()

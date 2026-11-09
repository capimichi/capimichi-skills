import sys
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from meta.browser import launch_meta_browser

AD_ACCOUNT_ID = "1116925509636183"
CAMPAIGN_ID = "120251426951480676"

def run():
    print("=" * 60)
    print("FINAL STEP: CLICK SALTA & PUBBLICA DEFINITIVO")
    print("=" * 60)

    context = launch_meta_browser(headless=True, args=["--window-size=2000,1080"], viewport={"width": 2000, "height": 1080})
    page = context.pages[0] if context.pages else context.new_page()

    try:
        url = f"https://adsmanager.facebook.com/adsmanager/manage/ads?act={AD_ACCOUNT_ID}&selected_campaign_ids={CAMPAIGN_ID}"
        page.goto(url, wait_until="domcontentloaded")
        time.sleep(8)
        page.keyboard.press("Escape")
        time.sleep(1)

        page.locator('[role="tab"]:has-text("Inserz")').last.click()
        time.sleep(3)

        page.locator(':text("Inserzione B - Offerta COD"), :text("Inserzione senza nome"), :text("In bozza")').first.click()
        time.sleep(2)

        page.locator('div[role="toolbar"] button:has-text("Modifica"), div[role="toolbar"] div[role="button"]:has-text("Modifica")').first.click()
        time.sleep(6)

        # Clicca "Visualizza l'anteprima per pubblicare" oppure "Pubblica"
        pub_btn = page.locator('button:has-text("pubblicare"), div[role="button"]:has-text("pubblicare"), button:has-text("Pubblica"), div[role="button"]:has-text("Pubblica")').last
        print("Clicco pulsante pubblicazione:", pub_btn.inner_text().strip())
        pub_btn.click()
        time.sleep(4)

        # Se compare il modal "Soddisfa le esigenze..." con il pulsante "Salta"
        salta_btn = page.locator('button:has-text("Salta"), div[role="button"]:has-text("Salta")').first
        if salta_btn.count() > 0 and salta_btn.is_visible():
            print("Trovato pulsante Salta! Clicco Salva/Salta...")
            salta_btn.click()
            time.sleep(6)

        # Verifica se compare la barra di caricamento o il modal di conferma/revisione
        page.screenshot(path="meta/after_salta_click.png")

        # Se c'è un modal di conferma o se c'è "Prova a pubblicare elementi con errori"
        dialog = page.locator('div[role="dialog"]').first
        if dialog.count() > 0 and dialog.is_visible():
            print("Modal di conferma/revisione attivo:", dialog.inner_text()[:120].replace('\n', ' '))
            force_box = dialog.locator('input[type="checkbox"], :has-text("Prova a pubblicare")').first
            if force_box.count() > 0:
                print("Spunto Prova a pubblicare elementi con errori...")
                force_box.click(force=True)
                time.sleep(2)

            confirm_pub = dialog.locator('button:has-text("Pubblica"), div[role="button"]:has-text("Pubblica")').last
            if confirm_pub.count() > 0:
                print("Clicco Pubblica definitivo...")
                confirm_pub.click()
                time.sleep(15)

        time.sleep(10)
        page.screenshot(path="meta/final_published_verification.png")
        print("Screenshot finale salvato in meta/final_published_verification.png")

        # Ricarica la tabella inserzioni per verificare lo stato attivo / in controllo
        page.goto(url, wait_until="domcontentloaded")
        time.sleep(8)
        page.keyboard.press("Escape")
        time.sleep(1)
        page.locator('[role="tab"]:has-text("Inserz")').last.click()
        time.sleep(4)
        page.screenshot(path="meta/ads_table_status_proof.png")
        print("Stato tabella inserzioni salvato in meta/ads_table_status_proof.png")

    finally:
        context.close()

if __name__ == "__main__":
    run()

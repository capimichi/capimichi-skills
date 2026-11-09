import sys
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from meta.browser import launch_meta_browser

AD_ACCOUNT_ID = "1116925509636183"

def run():
    print("=== CREAZIONE TAURO PLUS E VERIFICA TOTALE ===")
    context = launch_meta_browser(headless=True, args=["--window-size=2000,1080"], viewport={"width": 2000, "height": 1080})
    page = context.pages[0] if context.pages else context.new_page()

    try:
        page.goto(f"https://adsmanager.facebook.com/adsmanager/manage/campaigns?act={AD_ACCOUNT_ID}", wait_until="domcontentloaded")
        time.sleep(8)
        page.keyboard.press("Escape")
        time.sleep(1)

        # 1. Seleziona la riga di Rikrestin tramite checkbox
        rik_text = page.locator(':text-is("Rikrestin 2x49 - Test Vendite")').first
        box = rik_text.bounding_box()
        print("Rikrestin box:", box)

        # Deseleziona eventuali altre checkbox attive
        for item in page.locator('input[type="checkbox"][aria-checked="true"], div[role="checkbox"][aria-checked="true"]').all():
            item.click(force=True)
            time.sleep(1)

        # Clicca sulla checkbox di Rikrestin
        for item in page.locator('input[type="checkbox"], div[role="checkbox"]').all():
            ibox = item.bounding_box()
            if ibox and abs(ibox['y'] - box['y']) < 30 and ibox['x'] < box['x']:
                print("Seleziono checkbox di Rikrestin...")
                item.click(force=True)
                time.sleep(2)
                break

        # 2. Clicca Duplica nella toolbar
        toolbar_dup = page.locator('div[role="toolbar"] div[role="button"]:has-text("Duplica"), div[role="toolbar"] button:has-text("Duplica")').first
        print("Toolbar Duplica disabled:", toolbar_dup.get_attribute("aria-disabled"))
        toolbar_dup.click()
        time.sleep(3)

        # 3. Dialog: Clicca "Duplica e modifica"
        dialog = page.locator('div[role="dialog"]').filter(has_text='Duplica la tua campagna').first
        action_btn = dialog.locator('div[role="button"]:has-text("Duplica e modifica"), button:has-text("Duplica e modifica")').first
        print("Clicco Duplica e modifica nel dialog...")
        action_btn.click()
        time.sleep(6)

        # 4. Rinomina in "(NTM) Tauro Plus - Test"
        name_inputs = page.locator('input[type="text"]').all()
        for inp in name_inputs:
            val = inp.input_value()
            if "Rikrestin" in val:
                print(f"Aggiorno input nome a Tauro Plus (era {val})...")
                inp.click()
                page.keyboard.press("Meta+A")
                page.keyboard.press("Backspace")
                time.sleep(1)
                inp.fill("(NTM) Tauro Plus - Test")
                time.sleep(2)
                break

        # Chiudi drawer
        close_btn = page.locator('div[role="button"][aria-label="Chiudi"], button[aria-label="Chiudi"]').first
        if close_btn.count() > 0:
            print("Chiudo drawer...")
            close_btn.click()
            time.sleep(3)

        # 5. Ricarica e verifica finale della tabella Campagne
        print("\n--- CONTROLLO FINALE TUTTE LE CAMPAGNE ---")
        page.goto(f"https://adsmanager.facebook.com/adsmanager/manage/campaigns?act={AD_ACCOUNT_ID}", wait_until="domcontentloaded")
        time.sleep(8)
        page.keyboard.press("Escape")
        time.sleep(1)

        # Assicurati che tutti gli switch siano spenti
        switches = page.locator('input[role="switch"][aria-label="Sì/no"]').all()
        for i, s in enumerate(switches):
            checked = s.get_attribute("aria-checked")
            print(f"Switch campagna {i}: checked={checked}")
            if checked == "true":
                print(f"Spengo switch {i}!")
                s.click(force=True)
                time.sleep(2)

        page.screenshot(path="meta/final_three_campaigns_proof.png")
        print("Screenshot salvato in meta/final_three_campaigns_proof.png")

        # Dump testo
        lines = [l.strip() for l in page.locator("body").inner_text().splitlines() if l.strip()]
        with open("meta/final_three_campaigns.txt", "w", encoding="utf-8") as f:
            for l in lines:
                f.write(l + "\n")

        print("OPERAZIONE COMPLETATA CON SUCCESSO!")

    except Exception as e:
        print("Errore:", e)
        page.screenshot(path="meta/tauro_error.png")
    finally:
        context.close()

if __name__ == "__main__":
    run()

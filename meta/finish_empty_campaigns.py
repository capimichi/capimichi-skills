import sys
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from meta.browser import launch_meta_browser

AD_ACCOUNT_ID = "1116925509636183"

def run():
    print("=== FINALIZZAZIONE CAMPAGNE VUOTE SPENTE ===")
    context = launch_meta_browser(headless=True, args=["--window-size=2000,1080"], viewport={"width": 2000, "height": 1080})
    page = context.pages[0] if context.pages else context.new_page()

    try:
        # STEP 1: Rinomina la prima copia in "(NTM) Metabolismo Active 1x19 - Test"
        print("\n--- 1. RINOMINA METABOLISMO ACTIVE ---")
        page.goto(f"https://adsmanager.facebook.com/adsmanager/manage/campaigns?act={AD_ACCOUNT_ID}", wait_until="domcontentloaded")
        time.sleep(8)
        page.keyboard.press("Escape")
        time.sleep(1)

        # Seleziona checkbox della prima riga (la copia)
        copia_text = page.locator(':text("Rikrestin 2x49 - Test Vendite - Copia")').first
        if copia_text.count() > 0:
            box = copia_text.bounding_box()
            for item in page.locator('input[type="checkbox"], div[role="checkbox"]').all():
                ibox = item.bounding_box()
                if ibox and abs(ibox['y'] - box['y']) < 30 and ibox['x'] < box['x']:
                    print("Clicco checkbox della Copia...")
                    item.click(force=True)
                    time.sleep(2)
                    break

            # Clicca Modifica nella toolbar
            mod_btn = page.locator('div[role="toolbar"] div[role="button"]:has-text("Modifica"), div[role="toolbar"] button:has-text("Modifica")').first
            print("Clicco Modifica toolbar...")
            mod_btn.click()
            time.sleep(5)

            # Trova l'input del nome nell'editor drawer
            name_inputs = page.locator('input[type="text"]').all()
            for inp in name_inputs:
                val = inp.input_value()
                if "Rikrestin" in val:
                    print(f"Trovato input nome (val={val}), aggiorno a Metabolismo Active...")
                    inp.click()
                    page.keyboard.press("Meta+A")
                    page.keyboard.press("Backspace")
                    time.sleep(1)
                    inp.fill("(NTM) Metabolismo Active 1x19 - Test")
                    time.sleep(2)
                    break

            # Assicurati che lo switch sia OFF
            switches = page.locator('[role="dialog"] input[role="switch"], div[data-testid*="drawer"] input[role="switch"]').all()
            for s in switches:
                if s.get_attribute("aria-checked") == "true":
                    print("Spengo switch...")
                    s.click(force=True)
                    time.sleep(1)

            # Chiudi drawer
            close_btn = page.locator('div[role="button"][aria-label="Chiudi"], button[aria-label="Chiudi"]').first
            if close_btn.count() > 0:
                print("Chiudo drawer...")
                close_btn.click()
                time.sleep(3)

        # STEP 2: Duplica per Tauro Plus
        print("\n--- 2. DUPLICAZIONE PER TAURO PLUS ---")
        page.goto(f"https://adsmanager.facebook.com/adsmanager/manage/campaigns?act={AD_ACCOUNT_ID}", wait_until="domcontentloaded")
        time.sleep(8)
        page.keyboard.press("Escape")
        time.sleep(1)

        # Hover sulla riga originale Rikrestin
        orig_row = page.locator(':text-is("Rikrestin 2x49 - Test Vendite")').first
        orig_row.hover()
        time.sleep(1)

        # Trova il pulsante Duplica che appare sull'hover
        row_container = orig_row.locator('xpath=ancestor::div[@role="row" or contains(@class, "row")][1]')
        dup_hover = row_container.locator('div[role="button"]:has-text("Duplica"), button:has-text("Duplica")').first
        if dup_hover.count() == 0:
            dup_hover = page.locator('div[role="button"]:has-text("Duplica"):not([aria-disabled="true"])').first

        print("Clicco Duplica hover...")
        dup_hover.click()
        time.sleep(3)

        # Nel modal, clicca "Duplica e modifica"
        dialog = page.locator('div[role="dialog"]').filter(has_text='Duplica la tua campagna').first
        action_btn = dialog.locator('div[role="button"]:has-text("Duplica e modifica"), button:has-text("Duplica e modifica")').first
        print("Clicco Duplica e modifica nel dialog...")
        action_btn.click()
        time.sleep(6)

        # Rinomina in "(NTM) Tauro Plus - Test"
        name_inputs = page.locator('input[type="text"]').all()
        for inp in name_inputs:
            val = inp.input_value()
            if "Rikrestin" in val:
                print(f"Trovato input nome (val={val}), aggiorno a Tauro Plus...")
                inp.click()
                page.keyboard.press("Meta+A")
                page.keyboard.press("Backspace")
                time.sleep(1)
                inp.fill("(NTM) Tauro Plus - Test")
                time.sleep(2)
                break

        # Assicurati switch OFF
        switches = page.locator('[role="dialog"] input[role="switch"], div[data-testid*="drawer"] input[role="switch"]').all()
        for s in switches:
            if s.get_attribute("aria-checked") == "true":
                print("Spengo switch Tauro Plus...")
                s.click(force=True)
                time.sleep(1)

        # Chiudi drawer
        close_btn = page.locator('div[role="button"][aria-label="Chiudi"], button[aria-label="Chiudi"]').first
        if close_btn.count() > 0:
            print("Chiudo drawer...")
            close_btn.click()
            time.sleep(3)

        # STEP 3: Controllo Finale e Verifica Spento
        print("\n--- 3. VERIFICA FINALE TUTTE LE CAMPAGNE SPENTE ---")
        page.goto(f"https://adsmanager.facebook.com/adsmanager/manage/campaigns?act={AD_ACCOUNT_ID}", wait_until="domcontentloaded")
        time.sleep(8)
        page.keyboard.press("Escape")
        time.sleep(1)

        # Assicurati che OGNI switch sia spento
        all_switches = page.locator('input[role="switch"][aria-label="Sì/no"]').all()
        print(f"Trovati {len(all_switches)} switch nella tabella campagne.")
        for i, s in enumerate(all_switches):
            checked = s.get_attribute("aria-checked")
            print(f"Switch campagna {i}: checked={checked}")
            if checked == "true":
                print(f"Disattivo switch {i} per sicurezza!")
                s.click(force=True)
                time.sleep(2)

        page.screenshot(path="meta/campaigns_all_empty_spente.png")
        print("Screenshot salvato in meta/campaigns_all_empty_spente.png")

        # Dump testo finale
        with open("meta/final_campaigns_list.txt", "w", encoding="utf-8") as f:
            f.write(page.locator("body").inner_text())

    except Exception as e:
        print("Errore durante l'esecuzione:", e)
        page.screenshot(path="meta/final_error.png")
    finally:
        context.close()

if __name__ == "__main__":
    run()

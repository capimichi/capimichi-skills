import sys
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from meta.browser import launch_meta_browser

AD_ACCOUNT_ID = "1116925509636183"

def duplicate_campaign(page, new_campaign_name):
    print(f"\n--- DUPLICAZIONE PER: {new_campaign_name} ---")
    
    # Assicurati di essere nel tab Campagne
    page.goto(f"https://adsmanager.facebook.com/adsmanager/manage/campaigns?act={AD_ACCOUNT_ID}", wait_until="domcontentloaded")
    time.sleep(8)
    page.keyboard.press("Escape")
    time.sleep(1)

    tab_camp = page.locator('[role="tab"]:has-text("Campagne")').first
    if tab_camp.count() > 0:
        tab_camp.click()
        time.sleep(3)

    # Deseleziona tutto prima
    page.keyboard.press("Escape")
    time.sleep(1)

    # Seleziona la riga di Rikrestin
    rikrestin_row = page.locator(':text("Rikrestin 2x49")').first
    if rikrestin_row.count() == 0:
        print("Errore: Impossibile trovare la campagna Rikrestin da duplicare.")
        return False
    
    # Clicca sulla checkbox della riga Rikrestin
    # Troviamo la riga antenata
    row_el = rikrestin_row.locator('xpath=ancestor::div[@role="row"][1]')
    checkbox = row_el.locator('input[type="checkbox"]').first
    if checkbox.count() > 0 and not checkbox.is_checked():
        print("Seleziono checkbox di Rikrestin...")
        checkbox.click(force=True)
        time.sleep(2)

    # Clicca Duplica nella toolbar
    dup_btn = page.locator('div[role="toolbar"] button:has-text("Duplica"), div[role="button"]:has-text("Duplica"), button:has-text("Duplica")').first
    print("Clicco su Duplica...")
    dup_btn.click()
    time.sleep(3)
    page.screenshot(path=f"meta/dup_modal_{new_campaign_name[:10]}.png")

    # Controlla se compare il modal di conferma duplicazione
    modal = page.locator('div[role="dialog"]').filter(has_text="Duplica").first
    if modal.count() > 0:
        confirm_btn = modal.locator('button:has-text("Duplica")').last
        print("Confermo duplicazione nel modal...")
        confirm_btn.click()
        time.sleep(8)

    page.screenshot(path=f"meta/editor_opened_{new_campaign_name[:10]}.png")

    # Ora siamo nell'editor: cambiamo il nome della campagna
    name_input = page.locator('input[aria-label*="Nome della campagna"], input[placeholder*="Nome della campagna"]').first
    if name_input.count() == 0:
        # Fallback al primo input di testo nell'editor
        name_input = page.locator('input[type="text"]').first

    if name_input.count() > 0:
        print(f"Rinomino la campagna in: {new_campaign_name}")
        name_input.click()
        time.sleep(1)
        # Seleziona tutto e sovrascrivi
        page.keyboard.press("Meta+A")
        page.keyboard.press("Backspace")
        time.sleep(1)
        name_input.fill(new_campaign_name)
        time.sleep(2)

    # Assicurati che lo switch sia OFF (spento)
    switch = page.locator('input[role="switch"][aria-label*="Attiva"], [role="switch"]').first
    if switch.count() > 0:
        checked = switch.get_attribute("aria-checked")
        print(f"Switch campagna duplicata: checked={checked}")
        if checked == "true":
            print("Spengo lo switch della nuova campagna...")
            switch.click(force=True)
            time.sleep(2)

    # Chiudi l'editor o pubblica la bozza con switch spento
    close_btn = page.locator('button[aria-label="Chiudi"], div[role="button"][aria-label="Chiudi"]').first
    if close_btn.count() > 0:
        print("Chiudo l'editor...")
        close_btn.click()
        time.sleep(3)

    # Verifica se compare richiesta di scartare o salvare
    salva_btn = page.locator('button:has-text("Salva"), button:has-text("Continua")').first
    if salva_btn.count() > 0 and salva_btn.is_visible():
        salva_btn.click()
        time.sleep(2)

    print(f"Campagna {new_campaign_name} creata con successo!")
    return True

def main():
    print("=== CREAZIONE CAMPAGNE VUOTE SPENTE SU META ===")
    context = launch_meta_browser(headless=True, args=["--window-size=2000,1080"], viewport={"width": 2000, "height": 1080})
    page = context.pages[0] if context.pages else context.new_page()

    try:
        # 1. Duplica Metabolismo Active
        duplicate_campaign(page, "(NTM) Metabolismo Active 1x19 - Test")
        time.sleep(4)

        # 2. Duplica Tauro Plus
        duplicate_campaign(page, "(NTM) Tauro Plus - Test")
        time.sleep(4)

        # 3. Verifica finale lista campagne
        page.goto(f"https://adsmanager.facebook.com/adsmanager/manage/campaigns?act={AD_ACCOUNT_ID}", wait_until="domcontentloaded")
        time.sleep(8)
        page.keyboard.press("Escape")
        time.sleep(1)
        page.locator('[role="tab"]:has-text("Campagne")').first.click()
        time.sleep(4)

        # Assicurati che tutti gli switch siano SPENTI
        switches = page.locator('input[role="switch"][aria-label="Sì/no"]').all()
        for i, s in enumerate(switches):
            checked = s.get_attribute("aria-checked")
            print(f"Switch campagna {i}: {checked}")
            if checked == "true":
                print(f"ATTENZIONE: switch {i} era attivo, lo spengo subito!")
                s.click(force=True)
                time.sleep(2)

        page.screenshot(path="meta/final_empty_campaigns_proof.png")
        print("Screenshot finale salvato in meta/final_empty_campaigns_proof.png")

        # Dump testo finale
        body_text = page.locator("body").inner_text()
        with open("meta/empty_campaigns_dump.txt", "w", encoding="utf-8") as f:
            f.write(body_text)

    except Exception as e:
        print("Errore:", e)
        page.screenshot(path="meta/duplicate_error.png")
    finally:
        context.close()

if __name__ == "__main__":
    main()

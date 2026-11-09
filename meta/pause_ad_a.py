import sys
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from meta.browser import launch_meta_browser

AD_ACCOUNT_ID = "1116925509636183"
CAMPAIGN_ID = "120251426951480676"

def pause_ad_a():
    print("=== DISATTIVAZIONE AD A (Nuova inserzione Vendite) ===")
    context = launch_meta_browser(headless=True, args=["--window-size=2000,1080"], viewport={"width": 2000, "height": 1080})
    page = context.pages[0] if context.pages else context.new_page()

    try:
        url = f"https://adsmanager.facebook.com/adsmanager/manage/ads?act={AD_ACCOUNT_ID}&selected_campaign_ids={CAMPAIGN_ID}"
        print(f"Navigazione a: {url}")
        page.goto(url, wait_until="domcontentloaded")
        time.sleep(8)
        page.keyboard.press("Escape")
        time.sleep(1)

        # Tab Inserzioni
        tab = page.locator('[role="tab"]:has-text("Inserz")').last
        if tab.count() > 0:
            tab.click()
            time.sleep(3)
        
        page.screenshot(path="meta/pause_step0_table.png")
        print("Screenshot iniziale salvato in meta/pause_step0_table.png")

        # Cerca la riga di "Nuova inserzione Vendite"
        # Spesso ogni riga ha un [role="row"]
        rows = page.locator('[role="row"]').all()
        print(f"Trovate {len(rows)} righe nella tabella.")

        target_row = None
        for r in rows:
            txt = r.inner_text()
            if "Nuova inserzione Vendite" in txt:
                target_row = r
                print("Trovata riga per 'Nuova inserzione Vendite'!")
                print("Testo riga:", txt[:200])
                break

        if not target_row:
            print("Cercando tramite locator testo...")
            target_cell = page.locator(':text-is("Nuova inserzione Vendite"), :text("Nuova inserzione Vendite")').first
            target_row = target_cell.locator('xpath=ancestor::*[@role="row"]').first

        # Trova il toggle/switch all'interno della riga
        # Su Facebook Ads, lo switch ha solitamente role="switch" oppure checkbox oppure aria-checked="true"
        switch_elem = target_row.locator('[role="switch"], input[type="checkbox"], [aria-label*="Attiva"], [aria-label*="Disattiva"]').first
        
        if switch_elem.count() == 0:
            print("Switch non trovato direttamente con role='switch', cerco pulsanti o elementi cliccabili nella riga...")
            # Cerchiamo elementi con classe o attributi tipici
            candidates = target_row.locator('div[role="button"], span, div').all()
            for c in candidates:
                role = c.get_attribute("role") or ""
                label = c.get_attribute("aria-label") or ""
                checked = c.get_attribute("aria-checked") or ""
                if role == "switch" or "attiva" in label.lower() or checked in ["true", "false"]:
                    switch_elem = c
                    print(f"Trovato candidato switch: role={role}, label={label}, checked={checked}")
                    break

        if switch_elem and switch_elem.count() > 0:
            current_state = switch_elem.get_attribute("aria-checked")
            label = switch_elem.get_attribute("aria-label")
            print(f"Stato switch attuale: aria-checked={current_state}, aria-label={label}")

            print("Clicco sullo switch per disattivare...")
            switch_elem.click()
            time.sleep(4)
            page.screenshot(path="meta/pause_step1_clicked.png")

            # Verifica se compare un modale di conferma
            confirm_modal = page.locator('div[role="dialog"]')
            if confirm_modal.count() > 0:
                print("Modale di conferma rilevato!")
                print(confirm_modal.inner_text()[:300])
                # Cerca pulsante conferma tipo "Disattiva" o "Conferma"
                disattiva_btn = confirm_modal.locator('button:has-text("Disattiva"), button:has-text("Conferma"), button:has-text("Sì")').first
                if disattiva_btn.count() > 0:
                    disattiva_btn.click()
                    time.sleep(3)

            # Controlla se c'è una barra di pubblicazione in alto (es. "Rivedi e pubblica" o "Pubblica modifiche")
            pub_bar_btn = page.locator('button:has-text("Rivedi e pubblica"), button:has-text("Pubblica")').first
            if pub_bar_btn.count() > 0 and pub_bar_btn.is_visible():
                print(f"Pulsante visibile: {pub_bar_btn.inner_text()}")
                # Nota: spesso per i toggle non serve, ma verifichiamo

            time.sleep(3)
            page.screenshot(path="meta/pause_step2_verified.png")

            # Verifica stato finale
            ref = page.locator('[aria-label="Aggiorna dati tabella"]').first
            if ref.count() > 0:
                ref.click()
                time.sleep(3)

            page.screenshot(path="meta/pause_final_status.png")
            print("Screenshot finale salvato in meta/pause_final_status.png")

            # Dump del testo finale delle righe
            body_txt = page.locator('body').inner_text()
            with open("meta/pause_final_dump.txt", "w", encoding="utf-8") as f:
                f.write(body_txt)

            print("Operazione completata con successo!")

        else:
            print("ERRORE: Impossibile trovare lo switch per Ad A.")
            page.screenshot(path="meta/pause_error_no_switch.png")

    except Exception as e:
        print("Errore durante la disattivazione:", e)
        page.screenshot(path="meta/pause_exception.png")
    finally:
        context.close()

if __name__ == "__main__":
    pause_ad_a()

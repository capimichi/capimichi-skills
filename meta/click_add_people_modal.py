import sys
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from meta.browser import launch_meta_browser

AD_ACCOUNT_ID = "1116925509636183"
TARGET_NAME = "Michele Capicchioni"

def run():
    print("=" * 60)
    print(f"AGGIUNTA DI {TARGET_NAME} COME AMMINISTRATORE")
    print("=" * 60)

    context = launch_meta_browser(headless=True)
    page = context.pages[0] if context.pages else context.new_page()

    try:
        url = f"https://adsmanager.facebook.com/adsmanager/manage/account_settings?act={AD_ACCOUNT_ID}"
        print(f"Navigazione a: {url}")
        page.goto(url, wait_until="networkidle")
        time.sleep(5)

        # Clicca su Aggiungi persone
        add_btn = page.locator('button:has-text("Aggiungi persone"), div[role="button"]:has-text("Aggiungi persone")').first
        print(f"Pulsante 'Aggiungi persone': {add_btn.count()}")
        if add_btn.count() == 0:
            print("Riprovo con wait_for_selector...")
            page.wait_for_selector('button:has-text("Aggiungi persone"), div[role="button"]:has-text("Aggiungi persone")', timeout=10000)
            add_btn = page.locator('button:has-text("Aggiungi persone"), div[role="button"]:has-text("Aggiungi persone")').first

        if add_btn.count() > 0:
            add_btn.click()
            time.sleep(3)

            page.screenshot(path=str(PROJECT_ROOT / "meta" / "add_people_modal_active.png"))
            print("Screenshot modal salvato.")

            dialog = page.locator('div[role="dialog"]').first
            if dialog.count() > 0:
                print("\n--- TESTO MODAL AGGIUNGI PERSONE ---")
                print(dialog.inner_text())

                # Cerca input
                inp = dialog.locator('input').first
                if inp.count() > 0:
                    print(f"Digitazione '{TARGET_NAME}'...")
                    inp.click()
                    inp.fill(TARGET_NAME)
                    time.sleep(3)
                    page.screenshot(path=str(PROJECT_ROOT / "meta" / "add_people_typed_michele.png"))

                    # Opzioni dropdown
                    opts = page.locator('div[role="listbox"] div[role="option"], ul[role="listbox"] li, div[role="option"]').all()
                    print(f"Risultati dropdown: {len(opts)}")
                    selected = False
                    for o in opts:
                        txt = o.inner_text().strip()
                        print(f"  Opzione: '{txt}'")
                        if "Michele" in txt:
                            print("-> Clicco su opzione:", txt)
                            o.click()
                            selected = True
                            break

                    if not selected and len(opts) > 0:
                        print("-> Clicco sulla prima opzione:", opts[0].inner_text())
                        opts[0].click()
                        selected = True

                    time.sleep(2)

                    # Seleziona radio Amministratore
                    # Verifichiamo se c'è un radio button per 'Amministratore'
                    admin_radio = dialog.locator('input[type="radio"]').first
                    print(f"Radio trovati nel modal: {dialog.locator('input[type="radio"]').count()}")
                    # Cerchiamo l'elemento che contiene "Amministratore dell'account pubblicitario"
                    admin_label = dialog.locator('label:has-text("Amministratore dell\'account pubblicitario"), div:has-text("Amministratore dell\'account pubblicitario")').first
                    if admin_label.count() > 0:
                        print("Clicco su ruolo Amministratore...")
                        admin_label.click()
                        time.sleep(1)

                    page.screenshot(path=str(PROJECT_ROOT / "meta" / "admin_selected.png"))

                    # Clicca Conferma
                    confirm_btn = dialog.locator('button:has-text("Conferma"), div[role="button"]:has-text("Conferma")').first
                    print(f"Pulsante Conferma trovato: {confirm_btn.count()}")
                    if confirm_btn.count() > 0:
                        print("Clicco Conferma...")
                        confirm_btn.click()
                        time.sleep(5)
                        page.screenshot(path=str(PROJECT_ROOT / "meta" / "after_confirm.png"))
                        print("Conferma inviata con successo!")

            # Verifica finale
            page.goto(url, wait_until="networkidle")
            time.sleep(4)
            page.screenshot(path=str(PROJECT_ROOT / "meta" / "final_account_settings_with_new_admin.png"))
            print("\n--- TESTO FINALE RUOLI ---")
            lines = [l.strip() for l in page.locator('body').inner_text().splitlines() if l.strip()]
            for l in lines[:35]:
                print(l)

    finally:
        context.close()

if __name__ == "__main__":
    run()

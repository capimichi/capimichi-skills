import sys
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from meta.browser import launch_meta_browser

AD_ACCOUNT_ID = "1116925509636183"
TARGET_EMAIL = "capim@hotmail.it"

def run():
    print("=" * 60)
    print(f"AGGIUNTA UTENTE {TARGET_EMAIL} SU ACCOUNT PUBBLICITARIO")
    print("=" * 60)

    context = launch_meta_browser(headless=True)
    page = context.pages[0] if context.pages else context.new_page()

    try:
        url = f"https://adsmanager.facebook.com/adsmanager/manage/account_settings?act={AD_ACCOUNT_ID}"
        print(f"1. Navigazione a Impostazioni Account: {url}")
        page.goto(url, wait_until="domcontentloaded")
        time.sleep(6)

        page.screenshot(path=str(PROJECT_ROOT / "meta" / "account_settings_view.png"))
        print("Screenshot salvato in meta/account_settings_view.png")

        # Cerca pulsante "Aggiungi persone"
        add_btn = page.locator('button:has-text("Aggiungi persone"), div[role="button"]:has-text("Aggiungi persone")').first
        print(f"Pulsante 'Aggiungi persone' trovato: {add_btn.count() > 0}")

        if add_btn.count() > 0:
            add_btn.click()
            time.sleep(3)
            page.screenshot(path=str(PROJECT_ROOT / "meta" / "add_person_dialog.png"))
            print("Dialog Aggiungi persone aperto!")

            # Cerca campo input per amico/email/nome
            inp = page.locator('div[role="dialog"] input').first
            if inp.count() > 0:
                print(f"Inserimento {TARGET_EMAIL}...")
                inp.click()
                inp.fill(TARGET_EMAIL)
                time.sleep(2)

                page.screenshot(path=str(PROJECT_ROOT / "meta" / "add_person_typed.png"))

                # Cerca risultati dropdown o pulsanti di conferma
                options = page.locator('div[role="listbox"] div[role="option"], ul[role="listbox"] li, div[role="menuitem"]').all()
                print(f"Opzioni trovate nel dropdown: {len(options)}")
                for o in options:
                    print("Opzione utente:", o.inner_text())
                
                if len(options) > 0:
                    options[0].click()
                    time.sleep(1)

                confirm_btn = page.locator('div[role="dialog"] button:has-text("Conferma"), div[role="dialog"] button:has-text("Aggiungi"), div[role="dialog"] button:has-text("Avanti")').first
                if confirm_btn.count() > 0:
                    print("Clicco conferma:", confirm_btn.inner_text())
                    confirm_btn.click()
                    time.sleep(4)
                    print("Utente aggiunto con successo!")
        else:
            print("Pulsante non trovato, provo Business Settings People...")
            url_bm = "https://business.facebook.com/settings/people"
            page.goto(url_bm, wait_until="domcontentloaded")
            time.sleep(6)
            page.screenshot(path=str(PROJECT_ROOT / "meta" / "bm_people_view.png"))
            print("Screenshot Business Settings People salvato.")

    finally:
        context.close()

if __name__ == "__main__":
    run()

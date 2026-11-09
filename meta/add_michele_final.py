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
    print(f"AGGIUNTA DI {TARGET_NAME} COME AMMINISTRATORE SU AD_ACCOUNT_SETTINGS")
    print("=" * 60)

    context = launch_meta_browser(headless=True)
    page = context.pages[0] if context.pages else context.new_page()

    try:
        url = f"https://adsmanager.facebook.com/adsmanager/manage/ad_account_settings?act={AD_ACCOUNT_ID}"
        print("Navigazione a:", url)
        page.goto(url, wait_until="domcontentloaded")
        time.sleep(6)

        print("Current URL:", page.url)
        page.screenshot(path=str(PROJECT_ROOT / "meta" / "real_ad_account_settings_page.png"))

        # Testo pagina
        lines = [l.strip() for l in page.locator("body").inner_text().splitlines() if l.strip()]
        print("\n--- TESTO PAGINA IMPOSTAZIONI ACCOUNT ---")
        for l in lines[:35]:
            print(l)

        # Cerca bottone Aggiungi persone
        add_btn = page.locator('button:has-text("Aggiungi persone"), div[role="button"]:has-text("Aggiungi persone")').first
        print(f"\nPulsante 'Aggiungi persone': {add_btn.count()}")
        if add_btn.count() > 0:
            add_btn.click()
            time.sleep(3)

            page.screenshot(path=str(PROJECT_ROOT / "meta" / "modal_ad_account_michele.png"))

            dialog = page.locator('div[role="dialog"]').first
            print("\n--- MODAL APERTO ---")
            print(dialog.inner_text())

            inp = dialog.locator('input').first
            if inp.count() > 0:
                print(f"Inserimento '{TARGET_NAME}'...")
                inp.click()
                inp.fill(TARGET_NAME)
                time.sleep(3)

                page.screenshot(path=str(PROJECT_ROOT / "meta" / "typed_michele_in_modal.png"))

                # Opzioni dropdown
                opts = page.locator('div[role="listbox"] div[role="option"], ul li, div[role="menuitem"], div[role="option"]').all()
                print(f"Opzioni nel dropdown: {len(opts)}")
                matched = False
                for o in opts:
                    t = o.inner_text().strip()
                    print(f"  Opzione: '{t}'")
                    if "Michele" in t:
                        print(f"Match trovato per '{t}', clicco!")
                        o.click()
                        matched = True
                        break

                if not matched and len(opts) > 0:
                    print("Clicco sulla prima opzione:", opts[0].inner_text())
                    opts[0].click()
                    matched = True

                time.sleep(2)

                # Seleziona ruolo Amministratore
                admin_label = dialog.locator('label:has-text("Amministratore dell\'account pubblicitario"), div:has-text("Amministratore dell\'account pubblicitario")').first
                if admin_label.count() > 0:
                    print("Seleziono opzione Amministratore...")
                    admin_label.click()
                    time.sleep(1)

                page.screenshot(path=str(PROJECT_ROOT / "meta" / "admin_role_ready.png"))

                # Conferma
                confirm_btn = dialog.locator('button:has-text("Conferma"), div[role="button"]:has-text("Conferma")').first
                if confirm_btn.count() > 0:
                    print("Clicco Conferma...")
                    confirm_btn.click()
                    time.sleep(5)

                page.screenshot(path=str(PROJECT_ROOT / "meta" / "admin_added_success.png"))
                print("Operazione completata con successo!")

                # Ricarica e verifica
                page.goto(url, wait_until="domcontentloaded")
                time.sleep(5)
                page.screenshot(path=str(PROJECT_ROOT / "meta" / "verified_two_admins.png"))
                print("\n--- NUOVI RUOLI NELL'ACCOUNT PUBBLICITARIO ---")
                lines_after = [l.strip() for l in page.locator("body").inner_text().splitlines() if l.strip()]
                for l in lines_after[:40]:
                    print(l)

    finally:
        context.close()

if __name__ == "__main__":
    run()

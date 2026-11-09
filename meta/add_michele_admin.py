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
    print(f"AGGIUNTA DI {TARGET_NAME} COME AMMINISTRATORE ACCOUNT PUBBLICITARIO")
    print("=" * 60)

    context = launch_meta_browser(headless=True)
    page = context.pages[0] if context.pages else context.new_page()

    try:
        url_settings = f"https://adsmanager.facebook.com/adsmanager/manage/account_settings?act={AD_ACCOUNT_ID}"
        print(f"1. Navigazione a: {url_settings}")
        page.goto(url_settings, wait_until="networkidle")
        time.sleep(5)

        # Clicca Aggiungi persone
        add_btn = page.locator('button:has-text("Aggiungi persone"), div[role="button"]:has-text("Aggiungi persone")').first
        print(f"Pulsante 'Aggiungi persone': {add_btn.count()}")
        if add_btn.count() > 0:
            add_btn.click()
            time.sleep(3)

            page.screenshot(path=str(PROJECT_ROOT / "meta" / "modal_add_michele.png"))

            dialog = page.locator('div[role="dialog"]').first
            print("Modal aperto. Testo:", dialog.inner_text())

            # Input amico
            inp = dialog.locator('input').first
            inp.click()
            inp.fill(TARGET_NAME)
            time.sleep(3)

            page.screenshot(path=str(PROJECT_ROOT / "meta" / "typed_michele.png"))

            # Opzioni
            opts = page.locator('div[role="listbox"] div[role="option"], ul li, div[role="menuitem"]').all()
            print(f"Opzioni trovate per {TARGET_NAME}: {len(opts)}")
            matched = False
            for o in opts:
                txt = o.inner_text().strip()
                print(" -> Opzione:", txt)
                if "Michele Capicchioni" in txt:
                    print("Trovato match esatto! Clicco...")
                    o.click()
                    matched = True
                    break

            if not matched and len(opts) > 0:
                print("Clicco la prima opzione disponibile...")
                opts[0].click()
                matched = True

            time.sleep(2)

            # Seleziona ruolo Amministratore
            # Il ruolo di default potrebbe essere Inserzionista o Amministratore. Cerchiamo la radio o il testo Amministratore
            admin_opt = dialog.locator('label:has-text("Amministratore"), div:has-text("Amministratore dell\'account pubblicitario")').last
            if admin_opt.count() > 0:
                print("Seleziono ruolo Amministratore...")
                admin_opt.click()
                time.sleep(1)

            page.screenshot(path=str(PROJECT_ROOT / "meta" / "role_selected.png"))

            # Clicca Conferma
            confirm_btn = dialog.locator('button:has-text("Conferma"), div[role="button"]:has-text("Conferma")').first
            print(f"Pulsante Conferma attivo: {confirm_btn.is_enabled() if confirm_btn.count() > 0 else False}")
            if confirm_btn.count() > 0:
                confirm_btn.click()
                time.sleep(5)

            page.screenshot(path=str(PROJECT_ROOT / "meta" / "after_confirm_admin.png"))
            print("Operazione completata! Screenshot finale salvato.")

            # Verifica chi è presente tra i ruoli
            page.goto(url_settings, wait_until="networkidle")
            time.sleep(4)
            roles_text = page.locator('body').inner_text()
            print("\n--- RUOLI ATTUALI NELL'ACCOUNT PUBBLICITARIO ---")
            for line in roles_text.splitlines()[:35]:
                if line.strip():
                    print(line.strip())

    finally:
        context.close()

if __name__ == "__main__":
    run()

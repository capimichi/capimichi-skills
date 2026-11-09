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
    print("AGGIUNTA MICHELE CAPICCHIONI AMMINISTRATORE")
    print("=" * 60)

    context = launch_meta_browser(headless=True)
    page = context.pages[0] if context.pages else context.new_page()

    try:
        url = f"https://adsmanager.facebook.com/adsmanager/manage/ad_account_settings?act={AD_ACCOUNT_ID}"
        page.goto(url, wait_until="domcontentloaded")
        time.sleep(6)

        # Clicca Aggiungi persone
        add_btn = page.locator('[role="button"]:has-text("Aggiungi persone")').first
        add_btn.click()
        time.sleep(3)

        dialog = page.locator('[role="dialog"]:has-text("Aggiungi persone a questo account pubblicitario")').first
        inp = dialog.locator('input:not([type="hidden"])').first
        inp.click()
        time.sleep(1)

        # Digita Michele Capicchioni
        page.keyboard.type("Michele Capicchioni", delay=120)
        time.sleep(3)

        # Clicca sul suggerimento
        friend_item = page.locator('div:has-text("Michele Capicchioni"):has-text("Città di San Marino")').last
        if friend_item.count() == 0:
            friend_item = page.locator('text="Michele Capicchioni"').last
        friend_item.click()
        time.sleep(2)
        print("Profilo Michele Capicchioni selezionato!")

        # Ora apriamo il menu a tendina del ruolo cliccando sul testo 'Inserzionista dell'acc'
        role_trigger = dialog.locator('text="Inserzionista dell\'acc"').first
        print(f"Role trigger trovato: {role_trigger.count()}")
        role_trigger.click()
        time.sleep(2)

        page.screenshot(path=str(PROJECT_ROOT / "meta" / "role_dropdown_open.png"))

        # Cerca l'opzione Amministratore
        admin_opt = page.locator('div[role="menuitem"]:has-text("Amministratore"), li:has-text("Amministratore"), text="Amministratore dell\'account pubblicitario"').first
        print(f"Opzione Amministratore trovata: {admin_opt.count()}")
        if admin_opt.count() > 0:
            admin_opt.click()
            time.sleep(2)

        page.screenshot(path=str(PROJECT_ROOT / "meta" / "admin_role_set.png"))

        # Clicca Conferma
        confirm_btn = dialog.locator('button:has-text("Conferma"), div[role="button"]:has-text("Conferma")').first
        print(f"Pulsante Conferma abilitato: {confirm_btn.is_enabled()}")
        confirm_btn.click()
        time.sleep(6)

        page.screenshot(path=str(PROJECT_ROOT / "meta" / "final_confirm_clicked.png"))

        # Ricarica pagina e verifica ruoli
        page.goto(url, wait_until="domcontentloaded")
        time.sleep(5)
        page.screenshot(path=str(PROJECT_ROOT / "meta" / "final_verified_two_admins.png"))

        lines = [l.strip() for l in page.locator("body").inner_text().splitlines() if l.strip()]
        print("\n--- TESTO RUOLI AGGIORNATO ---")
        for l in lines[:45]:
            print(l)

    finally:
        context.close()

if __name__ == "__main__":
    run()

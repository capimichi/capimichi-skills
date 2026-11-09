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
    print("ESECUZIONE AGGIUNTA MICHELE CAPICCHIONI COME ADMIN")
    print("=" * 60)

    context = launch_meta_browser(headless=True)
    page = context.pages[0] if context.pages else context.new_page()

    try:
        url = f"https://adsmanager.facebook.com/adsmanager/manage/ad_account_settings?act={AD_ACCOUNT_ID}"
        print("1. Apertura pagina impostazioni...")
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
        print("2. Digitazione nome...")
        page.keyboard.type("Michele Capicchioni", delay=120)
        time.sleep(3)

        # Clicca sulla scheda del profilo nel popup
        print("3. Selezione profilo Michele Capicchioni...")
        friend_item = page.locator('div:has-text("Michele Capicchioni"):has-text("Città di San Marino")').last
        if friend_item.count() == 0:
            friend_item = page.locator('text="Michele Capicchioni"').last
        friend_item.click()
        time.sleep(2)

        page.screenshot(path=str(PROJECT_ROOT / "meta" / "step_friend_chosen.png"))

        # 4. Cambia ruolo in Amministratore
        print("4. Selezione ruolo Amministratore...")
        # Clicca sul dropdown del ruolo (accanto all'input o dentro dialog)
        role_btn = dialog.locator('a[role="button"], div[role="button"]:has-text("dell\'acc"), div[role="combobox"]').first
        if role_btn.count() == 0:
            role_btn = dialog.locator('div:has-text("Inserzionista")').last
        role_btn.click()
        time.sleep(2)

        page.screenshot(path=str(PROJECT_ROOT / "meta" / "step_role_opened.png"))

        # Cerca l'opzione "Amministratore dell'account pubblicitario"
        admin_opt = page.locator('text="Amministratore dell\'account pubblicitario"').first
        if admin_opt.count() == 0:
            admin_opt = page.locator('text="Amministratore"').first
        admin_opt.click()
        time.sleep(2)

        page.screenshot(path=str(PROJECT_ROOT / "meta" / "step_admin_selected.png"))

        # 5. Clicca Conferma
        print("5. Conferma...")
        confirm_btn = dialog.locator('button:has-text("Conferma"), [role="button"]:has-text("Conferma")').first
        print(f"Pulsante conferma abilitato: {confirm_btn.is_enabled()}")
        confirm_btn.click()
        time.sleep(6)

        page.screenshot(path=str(PROJECT_ROOT / "meta" / "step_confirmed.png"))

        # 6. Ricarica e verifica ruoli
        print("6. Verifica finale ruoli...")
        page.goto(url, wait_until="domcontentloaded")
        time.sleep(5)
        page.screenshot(path=str(PROJECT_ROOT / "meta" / "verified_new_admins_page.png"))

        lines = [l.strip() for l in page.locator("body").inner_text().splitlines() if l.strip()]
        print("\n--- NUOVI RUOLI VERIFICATI ---")
        for l in lines[:45]:
            print(l)

    finally:
        context.close()

if __name__ == "__main__":
    run()

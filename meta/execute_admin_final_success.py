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
    print("AGGIUNTA MICHELE CAPICCHIONI AMMINISTRATORE (DEFINITIVO)")
    print("=" * 60)

    context = launch_meta_browser(headless=True)
    page = context.pages[0] if context.pages else context.new_page()

    try:
        url = f"https://adsmanager.facebook.com/adsmanager/manage/ad_account_settings?act={AD_ACCOUNT_ID}"
        print("1. Apertura:", url)
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

        print("2. Digitazione nome...")
        page.keyboard.type("Michele Capicchioni", delay=120)
        time.sleep(3)

        # Seleziona profilo
        print("3. Selezione profilo...")
        friend_item = page.locator('div:has-text("Michele Capicchioni"):has-text("Città di San Marino")').last
        if friend_item.count() == 0:
            friend_item = page.locator('text="Michele Capicchioni"').last
        friend_item.click()
        time.sleep(2)
        print("Profilo selezionato!")

        # 4. Apri popover del ruolo
        print("4. Selezione ruolo Amministratore...")
        role_btn = dialog.locator('a._42fu, a:has-text("Inserzionista")').first
        role_btn.click()
        time.sleep(2)

        page.screenshot(path=str(PROJECT_ROOT / "meta" / "exact_role_popover.png"))

        # Clicca opzione Amministratore
        admin_opt = page.locator('text="Amministratore dell\'account pubblicitario"').last
        print(f"Opzione Amministratore trovata: {admin_opt.count()}")
        admin_opt.click()
        time.sleep(2)

        page.screenshot(path=str(PROJECT_ROOT / "meta" / "exact_admin_chosen.png"))

        # 5. Clicca Conferma
        print("5. Click su Conferma...")
        confirm_btn = dialog.locator('button.layerConfirm, button:has-text("Conferma")').first
        print(f"Conferma abilitata: {confirm_btn.is_enabled()}")
        confirm_btn.click()
        time.sleep(6)

        page.screenshot(path=str(PROJECT_ROOT / "meta" / "exact_confirmed_modal.png"))

        # 6. Verifica ruoli
        print("6. Ricarica e verifica ruoli...")
        page.goto(url, wait_until="domcontentloaded")
        time.sleep(5)
        page.screenshot(path=str(PROJECT_ROOT / "meta" / "verified_two_admins_final.png"))

        txt = page.locator("body").inner_text()
        print("\n--- NUOVI RUOLI NELL'ACCOUNT PUBBLICITARIO ---")
        lines = [l.strip() for l in txt.splitlines() if l.strip()]
        for l in lines[:45]:
            print(l)

    finally:
        context.close()

if __name__ == "__main__":
    run()

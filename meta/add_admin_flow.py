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
    context = launch_meta_browser(headless=True)
    page = context.pages[0] if context.pages else context.new_page()

    try:
        url = f"https://adsmanager.facebook.com/adsmanager/manage/campaigns/?act={AD_ACCOUNT_ID}"
        print(f"1. Apertura {url}")
        page.goto(url, wait_until="domcontentloaded")
        time.sleep(6)

        # Clicca su Impostazioni nella barra laterale sinistra
        # Nel DOM di Ads Manager c'è un'icona ingranaggio con aria-label="Impostazioni"
        gear = page.locator('[aria-label="Impostazioni"], button:has-text("Impostazioni"), a[aria-label="Impostazioni"]').first
        print(f"Gear found: {gear.count()}")
        if gear.count() > 0:
            print("Clicco su Impostazioni...")
            gear.click()
            time.sleep(6)

        print("URL attuale dopo click impostazioni:", page.url)
        page.screenshot(path=str(PROJECT_ROOT / "meta" / "settings_panel_opened.png"))

        # Cerca link o tab "Account pubblicitario" o "Ruoli dell'account pubblicitario"
        # Spesso apre la fatturazione. Nel menu a sinistra delle impostazioni c'è "Account pubblicitario"
        acc_tab = page.locator('a:has-text("Account pubblicitario"), div[role="tab"]:has-text("Account pubblicitario"), span:has-text("Account pubblicitario")').first
        if acc_tab.count() > 0:
            print("Clicco su tab 'Account pubblicitario'...")
            acc_tab.click()
            time.sleep(4)
            page.screenshot(path=str(PROJECT_ROOT / "meta" / "acc_tab_opened.png"))

        # Ora cerca pulsante "Aggiungi persone"
        add_btn = page.locator('button:has-text("Aggiungi persone"), div[role="button"]:has-text("Aggiungi persone")').first
        print(f"Pulsante 'Aggiungi persone' trovato: {add_btn.count()}")
        if add_btn.count() > 0:
            add_btn.click()
            time.sleep(3)
            page.screenshot(path=str(PROJECT_ROOT / "meta" / "add_people_dialog_michele.png"))

            dialog = page.locator('div[role="dialog"]').first
            print("Dialog testo:\n", dialog.inner_text())

            # Cerca campo input
            inp = dialog.locator('input').first
            inp.click()
            inp.fill("Michele Capicchioni")
            time.sleep(3)

            page.screenshot(path=str(PROJECT_ROOT / "meta" / "typed_michele_dialog.png"))

            # Mostra opzioni
            opts = page.locator('div[role="listbox"] div[role="option"], ul li, div[role="option"]').all()
            print(f"Opzioni per Michele: {len(opts)}")
            matched = False
            for o in opts:
                txt = o.inner_text().strip()
                print(" -> Opzione:", txt)
                if "Michele Capicchioni" in txt:
                    print("Match trovato! Clicco...")
                    o.click()
                    matched = True
                    break

            if not matched and len(opts) > 0:
                print("Clicco prima opzione:", opts[0].inner_text())
                opts[0].click()
                matched = True

            time.sleep(2)

            # Ruolo Amministratore
            admin_opt = dialog.locator('label:has-text("Amministratore"), div:has-text("Amministratore dell\'account pubblicitario")').last
            if admin_opt.count() > 0:
                print("Seleziono Amministratore...")
                admin_opt.click()
                time.sleep(1)

            page.screenshot(path=str(PROJECT_ROOT / "meta" / "role_ready.png"))

            # Conferma
            confirm_btn = dialog.locator('button:has-text("Conferma"), div[role="button"]:has-text("Conferma")').first
            if confirm_btn.count() > 0:
                print("Clicco Conferma!")
                confirm_btn.click()
                time.sleep(5)

            page.screenshot(path=str(PROJECT_ROOT / "meta" / "final_added_admin.png"))
            print("Operazione conclusa con successo!")

    finally:
        context.close()

if __name__ == "__main__":
    run()

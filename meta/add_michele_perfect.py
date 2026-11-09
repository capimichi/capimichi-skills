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
    print(f"AGGIUNTA PERFETTA DI {TARGET_NAME} COME AMMINISTRATORE")
    print("=" * 60)

    context = launch_meta_browser(headless=True)
    page = context.pages[0] if context.pages else context.new_page()

    try:
        url = f"https://adsmanager.facebook.com/adsmanager/manage/ad_account_settings?act={AD_ACCOUNT_ID}"
        print("1. Navigazione a:", url)
        page.goto(url, wait_until="domcontentloaded")
        time.sleep(6)

        # Clicca pulsante "Aggiungi persone"
        add_btn = page.locator('button:has-text("Aggiungi persone")').first
        print(f"Pulsante 'Aggiungi persone' trovato: {add_btn.count()}")
        add_btn.click()
        time.sleep(3)

        # Localizza il modal specifico per Aggiungi persone
        dialog = page.locator('div[role="dialog"]:has-text("Aggiungi persone")').first
        print(f"Dialog trovato: {dialog.count()}")

        # Trova input con placeholder 'Inserisci il nome di un amico'
        inp = dialog.locator('input[placeholder*="amico"], input[type="text"]').first
        print(f"Input trovato: {inp.count()}")
        inp.click()
        inp.fill(TARGET_NAME)
        time.sleep(3)

        page.screenshot(path=str(PROJECT_ROOT / "meta" / "step1_typed.png"))

        # Cerca dropdown amici
        # Le opzioni appaiono in div[role="listbox"], ul, o popover
        opts = page.locator('div[role="listbox"] [role="option"], ul [role="option"], div[role="menuitem"], div[role="option"]').all()
        print(f"Opzioni suggerite: {len(opts)}")
        selected = False
        for o in opts:
            txt = o.inner_text().strip()
            print(f" -> Opzione trovata: '{txt}'")
            if "Michele" in txt:
                print(f"Match! Clicco su '{txt}'")
                o.click()
                selected = True
                break

        if not selected and len(opts) > 0:
            print("Clicco sulla prima opzione disponibile:", opts[0].inner_text())
            opts[0].click()
            selected = True

        time.sleep(2)
        page.screenshot(path=str(PROJECT_ROOT / "meta" / "step2_friend_selected.png"))

        # Ora cambia il ruolo in "Amministratore dell'account pubblicitario"
        # Il dropdown del ruolo è dentro dialog accanto all'input
        role_select = dialog.locator('div[role="combobox"], [aria-haspopup="listbox"], button:has-text("dell\'acc"), div:has-text("Inserzionista dell\'acc")').first
        print(f"Role selector trovato: {role_select.count()}")
        if role_select.count() > 0:
            role_select.click()
            time.sleep(2)
            page.screenshot(path=str(PROJECT_ROOT / "meta" / "step3_role_dropdown.png"))

            # Clicca opzione Amministratore
            admin_item = page.locator('div[role="option"]:has-text("Amministratore"), div[role="menuitem"]:has-text("Amministratore"), span:has-text("Amministratore dell\'account")').first
            print(f"Opzione Amministratore trovata: {admin_item.count()}")
            if admin_item.count() > 0:
                admin_item.click()
                time.sleep(1)

        page.screenshot(path=str(PROJECT_ROOT / "meta" / "step4_role_chosen.png"))

        # Clicca Conferma
        confirm_btn = dialog.locator('button:has-text("Conferma")').first
        print(f"Pulsante Conferma attivo: {confirm_btn.is_enabled()}")
        if confirm_btn.count() > 0 and confirm_btn.is_enabled():
            confirm_btn.click()
            print("Pulsante Conferma CLICCATO!")
            time.sleep(6)

        page.screenshot(path=str(PROJECT_ROOT / "meta" / "step5_after_confirmation.png"))

        # Ricarica pagina impostazioni per verificare i Ruoli
        page.goto(url, wait_until="domcontentloaded")
        time.sleep(5)
        page.screenshot(path=str(PROJECT_ROOT / "meta" / "verified_final_roles.png"))

        txt = page.locator("body").inner_text()
        print("\n--- TESTO RUOLI AGGIORNATO ---")
        lines = [l.strip() for l in txt.splitlines() if l.strip()]
        for l in lines[:45]:
            print(l)

    finally:
        context.close()

if __name__ == "__main__":
    run()

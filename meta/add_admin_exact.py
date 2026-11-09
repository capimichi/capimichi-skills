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
    print(f"AGGIUNTA AMMINISTRATORE: {TARGET_NAME}")
    print("=" * 60)

    context = launch_meta_browser(headless=True)
    page = context.pages[0] if context.pages else context.new_page()

    try:
        url = f"https://adsmanager.facebook.com/adsmanager/manage/ad_account_settings?act={AD_ACCOUNT_ID}"
        print(f"1. Apertura: {url}")
        page.goto(url, wait_until="domcontentloaded")
        time.sleep(6)

        # Clicca Aggiungi persone
        add_btn = page.locator('[role="button"]:has-text("Aggiungi persone")').first
        print(f"Pulsante 'Aggiungi persone' trovato: {add_btn.count()}")
        add_btn.click()
        time.sleep(3)

        # Trova il dialog specifico
        dialog = page.locator('[role="dialog"]:has-text("Aggiungi persone a questo account pubblicitario")').first
        if dialog.count() == 0:
            dialog = page.locator('[role="dialog"]').last
        print(f"Dialog identificato: {dialog.count()}")

        # Trova input amico
        inp = dialog.locator('input[placeholder*="amico"], input[type="text"]').first
        print(f"Input amico trovato: {inp.count()}")
        inp.click()
        time.sleep(1)
        inp.fill(TARGET_NAME)
        time.sleep(3)

        page.screenshot(path=str(PROJECT_ROOT / "meta" / "exact_typed.png"))

        # Cerca i risultati di ricerca visualizzati
        results = page.locator('div[role="listbox"] div, ul li, div[role="menuitem"], div[role="option"]').all()
        print(f"Elementi lista risultati: {len(results)}")
        matched_el = None
        for r in results:
            t = r.inner_text().strip()
            if t:
                print(f"  Risultato: '{t}'")
                if "Michele" in t and not matched_el:
                    matched_el = r

        if matched_el:
            print("Clicco su risultato amico...")
            matched_el.click()
        elif len(results) > 0:
            print("Clicco sul primo elemento disponibile...")
            results[0].click()
        else:
            print("Nessun listbox, premo Invio su input...")
            inp.press("Enter")

        time.sleep(2)
        page.screenshot(path=str(PROJECT_ROOT / "meta" / "exact_after_select_friend.png"))

        # Cambia ruolo da Inserzionista ad Amministratore
        # Nel dialog c'è il selettore del ruolo
        role_trigger = dialog.locator('[role="combobox"], [aria-haspopup="listbox"], [role="button"]:has-text("dell\'acc")').first
        if role_trigger.count() == 0:
            role_trigger = dialog.locator('div:has-text("Inserzionista dell\'acc")').last
        print(f"Role trigger trovato: {role_trigger.count()}")
        if role_trigger.count() > 0:
            role_trigger.click()
            time.sleep(2)
            page.screenshot(path=str(PROJECT_ROOT / "meta" / "exact_role_menu.png"))

            admin_option = page.locator('[role="option"]:has-text("Amministratore"), [role="menuitem"]:has-text("Amministratore"), span:has-text("Amministratore")').first
            print(f"Opzione Amministratore trovata: {admin_option.count()}")
            if admin_option.count() > 0:
                admin_option.click()
                time.sleep(1)

        page.screenshot(path=str(PROJECT_ROOT / "meta" / "exact_ready_to_confirm.png"))

        # Clicca Conferma
        confirm_btn = dialog.locator('[role="button"]:has-text("Conferma")').first
        print(f"Pulsante Conferma abilitato: {confirm_btn.is_enabled()}")
        if confirm_btn.count() > 0 and confirm_btn.is_enabled():
            confirm_btn.click()
            print("Pulsante Conferma CLICCATO!")
            time.sleep(6)

        page.screenshot(path=str(PROJECT_ROOT / "meta" / "exact_confirmation_done.png"))

        # Verifica i ruoli attuali
        page.goto(url, wait_until="domcontentloaded")
        time.sleep(5)
        page.screenshot(path=str(PROJECT_ROOT / "meta" / "final_verified_roles.png"))

        body_text = page.locator("body").inner_text()
        print("\n--- STATO RUOLI DOPO L'OPERAZIONE ---")
        for line in [l.strip() for l in body_text.splitlines() if l.strip()][:40]:
            print(line)

    finally:
        context.close()

if __name__ == "__main__":
    run()

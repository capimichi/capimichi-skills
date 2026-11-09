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
    print("VERIFICA RICHIESTE DI AMICIZIA E AGGIUNTA SECONDO ADMIN")
    print("=" * 60)

    context = launch_meta_browser(headless=True)
    page = context.pages[0] if context.pages else context.new_page()

    try:
        # 1. Controlla richieste di amicizia
        print("1. Controllo richieste di amicizia su https://www.facebook.com/friends/requests...")
        page.goto("https://www.facebook.com/friends/requests", wait_until="domcontentloaded")
        time.sleep(5)

        page.screenshot(path=str(PROJECT_ROOT / "meta" / "friends_requests.png"))
        print("Screenshot salvato in meta/friends_requests.png")

        # Cerca eventuali richieste di amicizia
        body_text = page.locator("body").inner_text()
        print("\n--- TESTO PAGINA RICHIESTE DI AMICIZIA ---")
        lines = [l.strip() for l in body_text.splitlines() if l.strip()]
        for l in lines[:40]:
            print(l)

        # Cerca pulsanti "Conferma"
        confirm_btns = page.locator('div[role="button"]:has-text("Conferma"), button:has-text("Conferma")').all()
        print(f"\nPulsanti 'Conferma' trovati: {len(confirm_btns)}")
        for btn in confirm_btns:
            try:
                txt = btn.inner_text().strip()
                parent_text = btn.locator('xpath=ancestor::div[contains(@class, "x1")]').first.inner_text().replace("\n", " ")
                print(f"Richiesta da: {parent_text[:100]}")
                btn.click()
                print("-> Cliccato Conferma!")
                time.sleep(2)
            except Exception as e:
                print(f"Errore click conferma: {e}")

        page.screenshot(path=str(PROJECT_ROOT / "meta" / "friends_after_confirm.png"))

        # 2. Vai su Impostazioni Account Pubblicitario
        url_settings = f"https://adsmanager.facebook.com/adsmanager/manage/account_settings?act={AD_ACCOUNT_ID}"
        print(f"\n2. Navigazione a Impostazioni Account Pubblicitario: {url_settings}")
        page.goto(url_settings, wait_until="domcontentloaded")
        time.sleep(6)

        page.screenshot(path=str(PROJECT_ROOT / "meta" / "ad_account_settings_pre_add.png"))

        # Clicca Aggiungi persone
        add_btn = page.locator('button:has-text("Aggiungi persone"), div[role="button"]:has-text("Aggiungi persone")').first
        if add_btn.count() > 0:
            print("Pulsante 'Aggiungi persone' trovato. Clicco...")
            add_btn.click()
            time.sleep(3)

            page.screenshot(path=str(PROJECT_ROOT / "meta" / "add_people_modal_open.png"))

            dialog = page.locator('div[role="dialog"]').first
            if dialog.count() > 0:
                print("\n--- TESTO MODAL AGGIUNGI PERSONE ---")
                print(dialog.inner_text())

                # Vediamo il campo di input
                inp = dialog.locator('input').first
                if inp.count() > 0:
                    inp.click()
                    time.sleep(1)
                    # Vediamo se ci sono opzioni o suggerimenti
                    options = page.locator('div[role="listbox"] div, ul li, div[role="option"]').all()
                    print(f"Suggerimenti prima di digitare: {len(options)}")
                    for o in options[:10]:
                        t = o.inner_text().strip()
                        if t:
                            print("  Suggerimento:", t)

    finally:
        context.close()

if __name__ == "__main__":
    run()

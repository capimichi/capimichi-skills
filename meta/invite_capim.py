import sys
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from meta.browser import launch_meta_browser

TARGET_EMAIL = "capim@hotmail.it"

def run():
    print("=" * 60)
    print(f"INVITO UTENTE {TARGET_EMAIL} SU META BUSINESS SUITE")
    print("=" * 60)

    context = launch_meta_browser(headless=True)
    page = context.pages[0] if context.pages else context.new_page()

    try:
        url = "https://business.facebook.com/latest/settings/people"
        print(f"Navigazione a: {url}")
        page.goto(url, wait_until="domcontentloaded")
        time.sleep(6)

        # Chiudi tutorial se presenti
        page.keyboard.press("Escape")
        time.sleep(1)

        shot1 = PROJECT_ROOT / "meta" / "bm_settings_people.png"
        page.screenshot(path=str(shot1))
        print("Screenshot salvato in meta/bm_settings_people.png")

        # Cerca pulsante "Invita persone" o "Aggiungi persone"
        invite_btn = page.locator('button:has-text("Invita persone"), button:has-text("Aggiungi persone"), div[role="button"]:has-text("Invita persone")').first
        if invite_btn.count() > 0:
            print("Clicco 'Invita persone'...")
            invite_btn.click()
            time.sleep(3)

            shot2 = PROJECT_ROOT / "meta" / "bm_invite_modal.png"
            page.screenshot(path=str(shot2))
            print("Screenshot modal salvato.")

            # Inserisci email
            email_input = page.locator('input[type="email"], input[placeholder*="email"], input[placeholder*="indirizzo"]').first
            if email_input.count() > 0:
                print(f"Inserisco email {TARGET_EMAIL}...")
                email_input.click()
                email_input.fill(TARGET_EMAIL)
                time.sleep(1)

                shot3 = PROJECT_ROOT / "meta" / "bm_email_entered.png"
                page.screenshot(path=str(shot3))

                # Clicca Avanti
                avanti = page.locator('button:has-text("Avanti")').first
                if avanti.count() > 0:
                    avanti.click()
                    time.sleep(3)

                    # Assegna risorse (Account pubblicitario e Pagina)
                    # Spunta tutto quello che c'è
                    chk = page.locator('input[type="checkbox"]').all()
                    for c in chk:
                        try:
                            if not c.is_checked():
                                c.click(force=True)
                        except Exception:
                            pass
                    time.sleep(1)

                    avanti2 = page.locator('button:has-text("Avanti"), button:has-text("Invita"), button:has-text("Invia richiesta")').first
                    if avanti2.count() > 0:
                        avanti2.click()
                        time.sleep(3)

                        invia = page.locator('button:has-text("Invia richiesta"), button:has-text("Invia"), button:has-text("Invita")').first
                        if invia.count() > 0:
                            invia.click()
                            time.sleep(4)
                            print("Richiesta invito inviata con successo!")

        shot_final = PROJECT_ROOT / "meta" / "bm_invite_final.png"
        page.screenshot(path=str(shot_final))
        print("Screenshot finale salvato.")

    finally:
        context.close()

if __name__ == "__main__":
    run()

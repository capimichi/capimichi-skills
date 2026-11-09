import sys
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from meta.browser import launch_meta_browser

TARGET_EMAIL = "capim@hotmail.it"
BUSINESS_ID = "1416415513234900"
PEOPLE_URL = f"https://business.facebook.com/latest/settings/people?business_id={BUSINESS_ID}"

def run():
    context = launch_meta_browser(headless=True)
    page = context.pages[0] if context.pages else context.new_page()

    try:
        print(f"Navigazione a: {PEOPLE_URL}")
        page.goto(PEOPLE_URL, wait_until="domcontentloaded")
        time.sleep(6)

        # Chiudi eventuali popup con Escape o click fuori
        page.keyboard.press("Escape")
        time.sleep(1)

        page.screenshot(path=str(PROJECT_ROOT / "meta" / "direct_people_view.png"))
        print("Screenshot salvato in meta/direct_people_view.png")

        # Cerca bottone Invita persone
        invite_btn = page.locator('button:has-text("Invita"), div[role="button"]:has-text("Invita"), button:has-text("Aggiungi")').first
        if invite_btn.count() > 0:
            print("Clicco Invita persone...")
            invite_btn.click()
            time.sleep(3)

            page.screenshot(path=str(PROJECT_ROOT / "meta" / "invite_modal_opened.png"))

            # Campo email
            email_inp = page.locator('input[type="email"], input[placeholder*="email"], input[placeholder*="indirizzo"]').first
            if email_inp.count() > 0:
                print(f"Inserisco {TARGET_EMAIL}...")
                email_inp.click()
                email_inp.fill(TARGET_EMAIL)
                time.sleep(1)

                # Avanti
                avanti = page.locator('button:has-text("Avanti")').first
                if avanti.count() > 0:
                    avanti.click()
                    time.sleep(3)

                    # Secondo Avanti
                    avanti2 = page.locator('button:has-text("Avanti")').first
                    if avanti2.count() > 0:
                        avanti2.click()
                        time.sleep(3)

                    # Invia richiesta
                    send = page.locator('button:has-text("Invia"), button:has-text("Invita")').first
                    if send.count() > 0:
                        send.click()
                        time.sleep(4)
                        print(">>> INVITO INVIATO A capim@hotmail.it CON SUCCESSO! <<<")

        page.screenshot(path=str(PROJECT_ROOT / "meta" / "direct_people_after_invite.png"))

    finally:
        context.close()

if __name__ == "__main__":
    run()

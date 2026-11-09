import sys
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from meta.browser import launch_meta_browser

TARGET_EMAIL = "capim@hotmail.it"

def run():
    context = launch_meta_browser(headless=True)
    page = context.pages[0] if context.pages else context.new_page()

    try:
        url = "https://business.facebook.com/latest/home"
        print(f"Navigazione a: {url}")
        page.goto(url, wait_until="domcontentloaded")
        time.sleep(5)

        # Chiudi tutorial popup
        close_x = page.locator('div[aria-label="Chiudi"], button:has-text("Chiudi")').first
        if close_x.count() > 0:
            close_x.click()
            time.sleep(1)

        # Clicca Impostazioni nella sidebar
        settings_link = page.locator('a:has-text("Impostazioni"), span:has-text("Impostazioni")').first
        print("Clicco su Impostazioni...")
        settings_link.click()
        time.sleep(5)

        page.screenshot(path=str(PROJECT_ROOT / "meta" / "bm_settings_clicked.png"))
        print("URL impostazioni:", page.url)

        # Cerca 'Persone' o 'Invita persone'
        invite_btn = page.locator('button:has-text("Invita persone"), button:has-text("Aggiungi persone")').first
        if invite_btn.count() == 0:
            # Clicca sulla voce Persone nel menu laterale delle impostazioni
            persone = page.locator('text="Persone"').first
            if persone.count() > 0:
                persone.click()
                time.sleep(3)
                invite_btn = page.locator('button:has-text("Invita persone")').first

        if invite_btn.count() > 0:
            print("Clicco Invita persone...")
            invite_btn.click()
            time.sleep(3)

            inp = page.locator('input[type="email"], input[placeholder*="email"]').first
            if inp.count() > 0:
                inp.click()
                inp.fill(TARGET_EMAIL)
                time.sleep(1)

                page.screenshot(path=str(PROJECT_ROOT / "meta" / "invite_email_inserted.png"))

                # Clicca Avanti fino all'invio
                avanti = page.locator('button:has-text("Avanti")').first
                if avanti.count() > 0:
                    avanti.click()
                    time.sleep(2)

                    # Assegna accesso completo o di base
                    # Clicca di nuovo Avanti
                    avanti2 = page.locator('button:has-text("Avanti")').first
                    if avanti2.count() > 0:
                        avanti2.click()
                        time.sleep(2)

                    send = page.locator('button:has-text("Invia richiesta"), button:has-text("Invia invito"), button:has-text("Invita")').first
                    if send.count() > 0:
                        send.click()
                        time.sleep(4)
                        print("INVITO INVIATO UFFICIALMENTE!")

        page.screenshot(path=str(PROJECT_ROOT / "meta" / "invite_confirmed_screen.png"))

    finally:
        context.close()

if __name__ == "__main__":
    run()

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
    print("INVIO NOTIFICA ANTEPRIMA ALL'APP FACEBOOK")
    print("=" * 60)

    context = launch_meta_browser(headless=True)
    page = context.pages[0] if context.pages else context.new_page()

    try:
        url = f"https://adsmanager.facebook.com/adsmanager/manage/ads?act={AD_ACCOUNT_ID}"
        page.goto(url, wait_until="domcontentloaded")
        time.sleep(6)

        # Seleziona riga inserzione
        chk = page.locator('div[role="row"]').nth(1).locator('input[type="checkbox"]').first
        if chk.count() > 0:
            chk.click(force=True)
            time.sleep(1)

        # Clicca Anteprima
        prev = page.locator('button:has-text("Anteprima"), div[role="button"]:has-text("Anteprima")').first
        if prev.count() > 0:
            print("Apro pannello Anteprima...")
            prev.click()
            time.sleep(4)

            # Clicca Condividi
            share = page.locator('button:has-text("Condividi"), div[role="button"]:has-text("Condividi")').first
            if share.count() > 0:
                print("Click Condividi...")
                share.click()
                time.sleep(2)

                # Cerca opzione 'Invia notifica a Facebook'
                notif_opt = page.locator('text="Invia notifica a Facebook"').first
                if notif_opt.count() > 0:
                    print("Trovata opzione 'Invia notifica a Facebook', clicco!")
                    notif_opt.click()
                    time.sleep(3)

                    # Controlla eventuale messaggio di conferma (toast)
                    toast = page.locator('div[role="alert"], div:has-text("Notifica inviata")').first
                    print(f"Esito invio: {toast.inner_text() if toast.count() > 0 else 'Comando inviato'}")

                    shot = PROJECT_ROOT / "meta" / "notification_sent_confirm.png"
                    page.screenshot(path=str(shot))
                    print("Screenshot conferma salvato in:", shot)
                else:
                    print("Opzione 'Invia notifica a Facebook' non trovata nel menu")

    finally:
        context.close()

if __name__ == "__main__":
    run()

import sys
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from meta.browser import launch_meta_browser

AD_ACCOUNT_ID = "1116925509636183"

def run():
    context = launch_meta_browser(headless=True)
    page = context.pages[0] if context.pages else context.new_page()

    try:
        url = f"https://adsmanager.facebook.com/adsmanager/manage/campaigns?act={AD_ACCOUNT_ID}"
        print(f"1. Navigazione a Campagne: {url}")
        page.goto(url, wait_until="domcontentloaded")
        time.sleep(5)

        # Clicca sulla campagna Rikrestin
        camp = page.locator('text="Rikrestin 2x49 - Test Vendite"').first
        if camp.count() > 0:
            camp.click()
            time.sleep(3)

        # Tab Inserzioni
        page.get_by_role("tab", name="Inserzioni per 1 Campagna", exact=True).click()
        time.sleep(3)

        # Seleziona la riga dell'inserzione
        chk = page.locator('div[role="row"]').nth(1).locator('input[type="checkbox"]').first
        if chk.count() > 0:
            chk.click(force=True)
            time.sleep(1)

        # Clicca Anteprima
        prev = page.locator('button:has-text("Anteprima"), div[role="button"]:has-text("Anteprima")').first
        if prev.count() > 0:
            print("Click Anteprima...")
            prev.click()
            time.sleep(4)

            # Clicca Condividi
            share = page.locator('button:has-text("Condividi"), div[role="button"]:has-text("Condividi")').first
            if share.count() > 0:
                print("Click Condividi...")
                share.click()
                time.sleep(2)

                # Clicca 'Invia notifica a Facebook'
                notif = page.locator('text="Invia notifica a Facebook"').first
                if notif.count() > 0:
                    print("CLICCO 'Invia notifica a Facebook'...")
                    notif.click()
                    time.sleep(3)
                    print(">>> NOTIFICA INVIATA CON SUCCESSO! <<<")

    finally:
        context.close()

if __name__ == "__main__":
    run()

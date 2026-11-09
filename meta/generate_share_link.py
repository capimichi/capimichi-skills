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
        url = f"https://adsmanager.facebook.com/adsmanager/manage/ads?act={AD_ACCOUNT_ID}"
        print(f"Navigazione a: {url}")
        page.goto(url, wait_until="domcontentloaded")
        time.sleep(6)

        # Seleziona la riga dell'inserzione
        chk = page.locator('div[role="row"]').nth(1).locator('input[type="checkbox"]').first
        if chk.count() > 0:
            chk.click(force=True)
            time.sleep(1)

        # Clicca Anteprima
        prev_btn = page.locator('button:has-text("Anteprima"), div[role="button"]:has-text("Anteprima")').first
        if prev_btn.count() > 0:
            print("Click su Anteprima...")
            prev_btn.click()
            time.sleep(4)

            # Salva screenshot anteprima completa
            shot = PROJECT_ROOT / "meta" / "ad_preview_card.png"
            page.screenshot(path=str(shot))
            print(f"Screenshot salvato in {shot}")

            # Clicca Condividi
            share = page.locator('button:has-text("Condividi"), div[role="button"]:has-text("Condividi")').first
            if share.count() > 0:
                print("Click su Condividi...")
                share.click()
                time.sleep(2)

                # Cerca opzione 'Condividi un link'
                share_link_opt = page.locator('text="Condividi un link"').first
                if share_link_opt.count() > 0:
                    share_link_opt.click()
                    time.sleep(2)
                    # Cerca l'input con il link o il pulsante 'Copia link'
                    inputs = page.locator('div[role="dialog"] input').all()
                    for inp in inputs:
                        val = inp.input_value()
                        if "http" in val or "fb.me" in val or "facebook.com" in val:
                            print(f"\nLINK ANTEPRIMA PUBBLICO: {val}")

                    shot_dialog = PROJECT_ROOT / "meta" / "share_link_dialog.png"
                    page.screenshot(path=str(shot_dialog))

    finally:
        context.close()

if __name__ == "__main__":
    run()

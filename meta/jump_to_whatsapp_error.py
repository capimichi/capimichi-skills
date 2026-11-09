import sys
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from meta.browser import launch_meta_browser

AD_ACCOUNT_ID = "1116925509636183"
CAMPAIGN_ID = "120251426951480676"

def run():
    context = launch_meta_browser(
        headless=True,
        args=["--window-size=2000,1080"],
        viewport={"width": 2000, "height": 1080}
    )
    page = context.pages[0] if context.pages else context.new_page()

    try:
        url = f"https://adsmanager.facebook.com/adsmanager/manage/ads?act={AD_ACCOUNT_ID}&selected_campaign_ids={CAMPAIGN_ID}"
        print(f"Navigo a: {url}")
        page.goto(url, wait_until="domcontentloaded")
        time.sleep(8)
        page.keyboard.press("Escape")
        time.sleep(2)

        # Clicca bozza
        target = page.locator(':text("Inserzione B - Offerta COD"), :text("Inserzione senza nome"), :text("In bozza")').first
        target.click()
        time.sleep(2)

        # Clicca Modifica nella toolbar
        page.mouse.click(490, 233)
        time.sleep(6)

        page.screenshot(path=str(PROJECT_ROOT / "meta" / "jump_step0.png"))

        # Cerca il bottone Modifica dentro il box dell'errore (lato destro)
        err_box = page.locator('div:has-text("Numero WhatsApp necessario")')
        print(f"Error box trovato: {err_box.count() > 0}")
        if err_box.count() > 0:
            mod_btn = err_box.locator('button:has-text("Modifica"), div[role="button"]:has-text("Modifica")').first
            if mod_btn.count() > 0:
                print("Clicco Modifica dentro il box errore...")
                mod_btn.click()
                time.sleep(3)
            else:
                # Clicca sul testo dell'errore stesso
                print("Clicco sul testo dell'errore...")
                err_box.first.click()
                time.sleep(3)

        page.screenshot(path=str(PROJECT_ROOT / "meta" / "jump_after_click_error.png"))
        print("Screenshot salvato in meta/jump_after_click_error.png")

        # Cerca elementi evidenziati in rosso o con aria-invalid
        invalids = page.locator('[aria-invalid="true"], [data-error="true"], .has-error, div[style*="red"]').all()
        print(f"Campi non validi evidenziati: {len(invalids)}")
        for inv in invalids:
            print("Invalid element:", inv.inner_text().strip().replace('\n', ' ')[:80])

    finally:
        context.close()

if __name__ == "__main__":
    run()

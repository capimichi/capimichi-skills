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
        time.sleep(6)
        page.keyboard.press("Escape")
        time.sleep(1)

        # Clicca Modifica nella barra degli strumenti in alto o nella riga
        print("Cerco pulsante Modifica...")
        mod_btn = page.locator('button:has-text("Modifica"), div[role="button"]:has-text("Modifica")').first
        if mod_btn.count() > 0:
            print("Clicco Modifica:", mod_btn.inner_text().strip())
            mod_btn.click()
            time.sleep(6)
        
        page.screenshot(path=str(PROJECT_ROOT / "meta" / "ad_editor_panel_open.png"))
        print("Screenshot salvato in meta/ad_editor_panel_open.png")

        # Esamina tutti i testi / bottoni / input visibili nell'editor
        print("--- Elementi nel pannello editor ---")
        buttons = page.locator('button, div[role="button"]').all()
        for b in buttons:
            txt = b.inner_text().strip().replace('\n', ' ')
            if txt and len(txt) < 80:
                if any(w in txt.lower() for w in ["errore", "multimediale", "immagine", "sostituisci", "modifica", "carica", "pubblica", "chiudi", "avanti", "fine"]):
                    print(f"Button: {txt}")

    finally:
        context.close()

if __name__ == "__main__":
    run()

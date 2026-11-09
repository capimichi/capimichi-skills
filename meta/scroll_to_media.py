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
        page.goto(url, wait_until="domcontentloaded")
        time.sleep(8)
        page.keyboard.press("Escape")
        time.sleep(2)

        # Clicca target bozza
        target = page.locator(':text("Inserzione senza nome"), :text("In bozza")').first
        target.click()
        time.sleep(2)

        # Clicca Modifica
        page.mouse.click(490, 233)
        time.sleep(6)

        # 1. Riempi il nome
        name_inp = page.locator('input[placeholder*="nome della tua inserzione"]').first
        print("Trovato name input:", name_inp.count() > 0)
        if name_inp.count() > 0:
            name_inp.fill("Inserzione B - Offerta COD & Spedizione Gratis")
            time.sleep(1)

        # 2. Scrolla a 'Creatività dell'inserzione'
        page.mouse.move(500, 500)
        page.mouse.wheel(0, 900)
        time.sleep(2)

        page.screenshot(path=str(PROJECT_ROOT / "meta" / "media_section_view.png"))
        print("Screenshot salvato in meta/media_section_view.png")

        # Trova bottoni nel pannello centrale
        buttons = page.locator('button, div[role="button"]').all()
        for b in buttons:
            txt = b.inner_text().strip().replace('\n', ' ')
            if any(w in txt.lower() for w in ["modifica gruppo", "sostituisci", "modifica elemento", "modifica immagine", "aggiungi"]):
                print("Media button found:", txt)

    finally:
        context.close()

if __name__ == "__main__":
    run()

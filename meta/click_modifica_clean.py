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

        # Clicca sulla cella della bozza per selezionarla
        copia_target = page.locator(':text("Nuova inserzione Vendite - Copia")').first
        if copia_target.count() > 0:
            print("Clicco su testo bozza...")
            copia_target.click()
            time.sleep(2)

        # Ora clicchiamo Modifica
        # Proviamo il pulsante Modifica nella riga o nella toolbar
        mod_candidates = page.locator(':text("Modifica")').all()
        print(f"Trovati {len(mod_candidates)} elementi con 'Modifica'")
        clicked = False
        for idx, m in enumerate(mod_candidates):
            if m.is_visible():
                box = m.bounding_box()
                print(f"Candidate {idx}: text='{m.inner_text().strip()}', bbox={box}")
                # Cerchiamo quello nella toolbar (y attorno a 200-230) o nella riga (y attorno a 320-360)
                if box and box['y'] > 180 and box['y'] < 400 and box['width'] > 20:
                    print(f"Clicco su candidato {idx} a coordinate ({box['x'] + box['width']/2}, {box['y'] + box['height']/2})")
                    page.mouse.click(box['x'] + box['width']/2, box['y'] + box['height']/2)
                    clicked = True
                    time.sleep(6)
                    break

        page.screenshot(path=str(PROJECT_ROOT / "meta" / "editor_panel_opened_check.png"))
        print("Screenshot salvato in meta/editor_panel_opened_check.png")

    finally:
        context.close()

if __name__ == "__main__":
    run()

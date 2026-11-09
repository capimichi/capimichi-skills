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
        page.goto(url, wait_until="domcontentloaded")
        time.sleep(5)

        # Campagna
        page.locator('text="Rikrestin 2x49 - Test Vendite"').first.click()
        time.sleep(3)

        # Tab Inserzioni
        page.locator('text="Inserzioni per 1 Campagna"').first.click()
        time.sleep(3)

        # Checkbox riga
        boxes = page.locator('input[type="checkbox"]').all()
        if len(boxes) > 1:
            boxes[1].click(force=True)
            time.sleep(1)

        # Trova tutti gli elementi con 'Modifica'
        edit_elements = page.locator(':text("Modifica")').all()
        print(f"Elementi con 'Modifica' trovati: {len(edit_elements)}")
        clicked = False
        for el in edit_elements:
            try:
                tag = el.evaluate("el => el.tagName")
                role = el.get_attribute("role") or ""
                bbox = el.bounding_box()
                text = el.inner_text().strip()
                print(f"El: tag={tag}, role={role}, text='{text}', bbox={bbox}")
                # Clicchiamo quello nella toolbar (y tra 300 e 500)
                if bbox and 300 < bbox['y'] < 500 and not clicked:
                    print("Clicco su:", el)
                    el.click()
                    clicked = True
                    time.sleep(6)
            except Exception as e:
                print("Error inspecting el:", e)

        page.screenshot(path=str(PROJECT_ROOT / "meta" / "editor_clicked_result.png"))
        print("Screenshot salvato in meta/editor_clicked_result.png")

        # Cerca Advantage e generazione
        full_text = page.locator('body').inner_text()
        with open(PROJECT_ROOT / "meta" / "editor_dump_adv.txt", "w", encoding="utf-8") as f:
            f.write(full_text)

        for l in full_text.splitlines():
            ls = l.strip()
            if any(k in ls.lower() for k in ["advantage", "creativit", "immagine", "immagini", "generazione", "espansione", "sfondo", "musica", "ottimizz"]):
                print("->", ls)

    finally:
        context.close()

if __name__ == "__main__":
    run()

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
        print(f"Navigazione a: {url}")
        page.goto(url, wait_until="domcontentloaded")
        time.sleep(5)

        # Campagna
        print("Click campagna...")
        page.locator('text="Rikrestin 2x49 - Test Vendite"').first.click()
        time.sleep(3)

        # Tab Inserzioni
        print("Click Inserzioni per 1 Campagna...")
        page.locator('text="Inserzioni per 1 Campagna"').first.click()
        time.sleep(4)

        # Trova tutte le checkbox
        boxes = page.locator('input[type="checkbox"]').all()
        print(f"Checkbox trovati: {len(boxes)}")
        # box 0 è header, box 1 è riga dell'inserzione
        if len(boxes) > 1:
            print("Clicco checkbox riga 1...")
            boxes[1].click(force=True)
            time.sleep(2)

        # Ora il bottone Modifica in alto
        mod_btn = page.locator('button:has-text("Modifica")').first
        print(f"Bottone Modifica enabled: {mod_btn.is_enabled()}")
        if mod_btn.is_enabled():
            mod_btn.click()
            time.sleep(6)

        page.screenshot(path=str(PROJECT_ROOT / "meta" / "ad_edit_panel_full.png"))
        print("Screenshot salvato in meta/ad_edit_panel_full.png")

        # Cerca Advantage / Immagini / Creatività
        text = page.locator('body').inner_text()
        with open(PROJECT_ROOT / "meta" / "ad_edit_panel_text.txt", "w", encoding="utf-8") as f:
            f.write(text)

        print("\n--- RISULTATI RICERCA TESTUALE ---")
        lines = text.split("\n")
        for i, l in enumerate(lines):
            l_str = l.strip()
            if any(k in l_str.lower() for k in ["advantage", "creativit", "immagine", "immagini", "generazione", "espansione", "sfondo", "musica"]):
                print(f"L{i}: {l_str}")
                print("   Context:", " | ".join(lines[max(0, i-2):min(len(lines), i+3)]))

    finally:
        context.close()

if __name__ == "__main__":
    run()

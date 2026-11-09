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
        time.sleep(6)

        # Chiudi pannelli laterali 'Crea visualizzazione' se aperti
        close_btn = page.locator('button[aria-label="Chiudi"]').all()
        for b in close_btn:
            try:
                b.click()
                time.sleep(1)
            except Exception:
                pass
        page.keyboard.press("Escape")
        time.sleep(1)

        # Clicca sulla campagna Rikrestin
        print("2. Apertura campagna 'Rikrestin 2x49 - Test Vendite'...")
        camp_link = page.locator('text="Rikrestin 2x49 - Test Vendite"').first
        if camp_link.count() > 0:
            camp_link.click()
            time.sleep(4)

        # Tab Inserzioni
        print("3. Navigazione a livello Inserzioni...")
        ads_tab = page.locator('button:has-text("Inserzioni"), div[role="tab"]:has-text("Inserzioni")').first
        if ads_tab.count() > 0:
            ads_tab.click()
            time.sleep(4)

        # Chiudi eventuale popup o Escape
        page.keyboard.press("Escape")
        time.sleep(1)

        # Seleziona la riga dell'inserzione attiva
        print("4. Selezione riga e click Modifica...")
        chks = page.locator('div[role="row"] input[type="checkbox"]').all()
        print(f"Checkbox trovati: {len(chks)}")
        if len(chks) >= 2:
            chks[1].click(force=True)
            time.sleep(1)

        mod_btn = page.locator('button:has-text("Modifica")').first
        if mod_btn.count() > 0:
            mod_btn.click()
            time.sleep(6)

        page.screenshot(path=str(PROJECT_ROOT / "meta" / "ad_editor_opened.png"))
        print("Screenshot salvato in meta/ad_editor_opened.png")

        # Cerca tutto il testo
        body_text = page.locator('body').inner_text()
        print("\n=== RICERCA 'ADVANTAGE' / 'IMMAGIN' / 'CREATIVIT' ===")
        found = False
        for line in body_text.split("\n"):
            line_str = line.strip()
            if any(k in line_str.lower() for k in ["advantage", "immagine", "immagini", "creativit", "generazione", "espansione", "ottimizz"]):
                print("->", line_str)
                found = True

        # Cerca bottoni o sezioni specifiche di Advantage+ creative
        adv_sections = page.locator('text*="Advantage+", text*="advantage+", text*="Miglioramenti", text*="Generazione"').all()
        print(f"\nElementi locator specifici trovati: {len(adv_sections)}")
        for idx, el in enumerate(adv_sections[:10]):
            try:
                print(f"Section {idx}: {el.inner_text().strip().replace(chr(10), ' | ')}")
            except:
                pass

    finally:
        context.close()

if __name__ == "__main__":
    run()

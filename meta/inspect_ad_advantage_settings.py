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
        print("Navigo su campaigns...")
        page.goto(url, wait_until="domcontentloaded")
        time.sleep(5)

        # Clicca sulla campagna Rikrestin
        camp = page.locator('text="Rikrestin 2x49 - Test Vendite"').first
        if camp.count() > 0:
            print("Clicco su campagna...")
            camp.click()
            time.sleep(3)

        # Tab Inserzioni
        print("Clicco su tab inserzioni...")
        ads_tab = page.locator('text="Inserzioni per 1 Gruppo di inserzioni", text="Inserzioni per 1 Campagna", div[role="tab"]:has-text("Inserzioni")').first
        if ads_tab.count() > 0:
            ads_tab.click()
            time.sleep(3)

        # Clicca Modifica dell'inserzione
        print("Cerco inserzione...")
        name_cell = page.locator('div[role="gridcell"]:has-text("Nuova inserzione Vendite")').first
        if name_cell.count() > 0:
            name_cell.hover()
            time.sleep(1)

        mod_btn = page.locator('button:has-text("Modifica"), a:has-text("Modifica")').first
        if mod_btn.count() > 0:
            print("Clicco Modifica...")
            mod_btn.click()
            time.sleep(6)

        # Ora siamo nell'editor dell'inserzione
        # Scorriamo il pannello centrale dell'editor
        page.screenshot(path=str(PROJECT_ROOT / "meta" / "ad_editor_view_1.png"))
        
        # Cerchiamo tutti i testi relativi ad Advantage+, Creatività Advantage+, Generazione immagini
        full_text = page.locator('body').inner_text()
        print("\n--- OCCORRENZE ADVANTAGE / CREATIVITÀ / GENERAZIONE / IMMAGINE ---")
        lines = full_text.split("\n")
        for i, l in enumerate(lines):
            line_clean = l.strip()
            if any(term in line_clean.lower() for term in ["advantage", "creativit", "generazione", "espansione", "sfondo", "catalogo", "ottimizz"]):
                print(f"L{i}: {line_clean}")
                # Stampa contesto
                start = max(0, i-2)
                end = min(len(lines), i+3)
                print("   Context:", " /// ".join(lines[start:end]))

        # Cerca checkbox o switch (aria-checked)
        switches = page.locator('div[role="switch"], input[type="checkbox"]').all()
        print(f"\n--- SWITCH / CHECKBOX TROVATI: {len(switches)} ---")
        for s in switches:
            lbl = s.get_attribute("aria-label") or s.inner_text().strip()
            checked = s.get_attribute("aria-checked") or s.is_checked()
            if lbl:
                print(f"Switch/Box: '{lbl}' -> Checked: {checked}")

        # Scorri il pannello editor verso il basso
        # Il pannello di editing di solito ha overflow o è scrollabile
        scroll_containers = page.locator('div[style*="overflow"]').all()
        for c in scroll_containers:
            try:
                c.evaluate("el => el.scrollTop += 800")
            except:
                pass
        time.sleep(2)
        page.screenshot(path=str(PROJECT_ROOT / "meta" / "ad_editor_view_2.png"))

    finally:
        context.close()

if __name__ == "__main__":
    run()

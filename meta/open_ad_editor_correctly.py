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

        # Hover sul testo dell'inserzione
        cell = page.locator('div[role="gridcell"]:has-text("Nuova inserzione Vendite")').first
        cell.hover()
        time.sleep(1)

        # Cerca link o bottoni inline
        # In alternativa, clicca sul checkbox della riga dell'inserzione
        row_chk = page.locator('div[role="row"]').nth(1).locator('input[type="checkbox"], [role="checkbox"]').first
        if row_chk.count() > 0:
            print("Clicco checkbox riga...")
            row_chk.click(force=True)
            time.sleep(1)

        # Clicca sul pulsante Modifica in alto (ora attivo)
        mod_btn = page.locator('button:has-text("Modifica")').first
        print("Stato bottone Modifica enabled:", mod_btn.is_enabled())
        if mod_btn.is_enabled():
            mod_btn.click()
            time.sleep(5)
        else:
            # Prova a cliccare su Modifica inline
            inline_mod = page.locator('button:has-text("Modifica"), div[role="button"]:has-text("Modifica"), a:has-text("Modifica")').all()
            for b in inline_mod:
                if b.is_visible():
                    b.click()
                    time.sleep(5)
                    break

        page.screenshot(path=str(PROJECT_ROOT / "meta" / "editor_ad_open_final.png"))
        print("Screenshot salvato in meta/editor_ad_open_final.png")

        # Cerca Advantage, Immagini, Creatività
        text = page.locator('body').inner_text()
        with open(PROJECT_ROOT / "meta" / "editor_ad_details.txt", "w", encoding="utf-8") as f:
            f.write(text)

        lines = text.split("\n")
        print("\n=== MATCH ADVANTAGE / CREATIVITÀ ===")
        for i, l in enumerate(lines):
            l_clean = l.strip()
            if any(k in l_clean.lower() for k in ["advantage", "creativit", "immagine", "immagini", "generazione", "espansione"]):
                print(f"[{i}] {l_clean}")
                print("   Snippet:", " | ".join(lines[max(0, i-2):min(len(lines), i+3)]))

    finally:
        context.close()

if __name__ == "__main__":
    run()

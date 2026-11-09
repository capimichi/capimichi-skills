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
        url = f"https://adsmanager.facebook.com/adsmanager/manage/ads?act={AD_ACCOUNT_ID}&selected_campaign_ids=120251426951480676&treenav=true"
        page.goto(url, wait_until="networkidle")
        time.sleep(5)

        # Tab Inserzioni
        tab = page.get_by_role("tab", name="Inserzioni per 1 Campagna", exact=True)
        if tab.count() > 0:
            tab.click()
            time.sleep(3)

        # Clicca Modifica
        row = page.locator('div[role="row"]').nth(1)
        row.hover()
        time.sleep(1)

        mod = page.locator('button:has-text("Modifica")').first
        if mod.count() > 0:
            mod.click()
            time.sleep(5)

        # Cerca tutti i testi contenenti Advantage+, Creativit, Immagin, Generazione, Ottimizz
        body_text = page.locator('body').inner_text()
        
        keywords = ["advantage", "creativit", "immagine", "generazione", "espansione", "musica", "ottimizz", "miglioramenti"]
        print("--- SEARCH IN BODY TEXT ---")
        lines = [line.strip() for line in body_text.split("\n") if line.strip()]
        for idx, line in enumerate(lines):
            for kw in keywords:
                if kw in line.lower():
                    context_snippet = " | ".join(lines[max(0, idx-2):min(len(lines), idx+3)])
                    print(f"[MATCH '{kw}'] -> {line}")
                    print(f"    Context: {context_snippet}")
                    break

        page.screenshot(path=str(PROJECT_ROOT / "meta" / "ad_editor_advantage_inspect.png"), full_page=True)
        print("Screenshot saved to meta/ad_editor_advantage_inspect.png")

    finally:
        context.close()

if __name__ == "__main__":
    run()

import sys
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from meta.browser import launch_meta_browser

AD_ACCOUNT_ID = "1116925509636183"
CAMPAIGN_ID = "120251426951480676"
AD_ID = "120251426951500676"

URL = f"https://adsmanager.facebook.com/adsmanager/manage/ads/edit?act={AD_ACCOUNT_ID}&selected_campaign_ids={CAMPAIGN_ID}&selected_ad_ids={AD_ID}"

def run():
    context = launch_meta_browser(headless=True)
    page = context.pages[0] if context.pages else context.new_page()

    try:
        print(f"Navigo a edit URL: {URL}")
        page.goto(URL, wait_until="networkidle")
        time.sleep(6)

        # Chiudi popover se ce ne sono
        page.keyboard.press("Escape")
        time.sleep(1)

        page.screenshot(path=str(PROJECT_ROOT / "meta" / "ad_direct_edit_page.png"))
        print("Screenshot salvato in meta/ad_direct_edit_page.png")

        # Dump text
        body_text = page.locator('body').inner_text()
        with open(PROJECT_ROOT / "meta" / "ad_direct_edit_text.txt", "w", encoding="utf-8") as f:
            f.write(body_text)

        print("\n=== MATCH CHIAVE NEL TESTO DELL'EDITOR ===")
        keywords = ["advantage", "creativit", "immagine", "immagini", "generazione", "espansione", "sfondo", "musica", "ottimizz", "miglioramenti", "standard"]
        lines = body_text.splitlines()
        for idx, l in enumerate(lines):
            ls = l.strip()
            if any(k in ls.lower() for k in keywords):
                print(f"L{idx}: {ls}")
                ctx = " | ".join(lines[max(0, idx-2):min(len(lines), idx+3)])
                print(f"   Context: {ctx}")

        # Controlliamo tutti gli switch / checkbox attivi
        switches = page.locator('div[role="switch"], input[type="checkbox"]').all()
        print(f"\n--- SWITCH / CHECKBOX ({len(switches)}) ---")
        for s in switches:
            label = s.get_attribute("aria-label") or s.get_attribute("title") or s.inner_text().strip()
            is_checked = s.get_attribute("aria-checked") or s.is_checked()
            print(f"Switch: '{label}' -> Checked: {is_checked}")

    finally:
        context.close()

if __name__ == "__main__":
    run()

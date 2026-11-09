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
    context = launch_meta_browser(
        headless=True,
        args=["--window-size=1600,1000"],
        viewport={"width": 1600, "height": 1000}
    )
    page = context.pages[0] if context.pages else context.new_page()

    try:
        print(f"Navigo a URL: {URL}")
        page.goto(URL, wait_until="networkidle")
        time.sleep(5)
        page.keyboard.press("Escape")
        time.sleep(1)

        # Clicca sulla matita della toolbar (o pulsante Modifica)
        # Cerchiamo il bottone che contiene l'icona matita o il testo Modifica
        edit_btn = page.locator('button[aria-label*="Modifica"], div[role="button"][aria-label*="Modifica"], button:has-text("Modifica")').first
        if edit_btn.count() > 0:
            print("Clicco edit_btn...")
            edit_btn.click()
            time.sleep(6)
        else:
            # Proviamo click per coordinate sul pulsante matita
            print("Click coordinate matita...")
            page.mouse.click(305, 425)
            time.sleep(6)

        page.screenshot(path=str(PROJECT_ROOT / "meta" / "ad_editor_1600.png"))
        print("Screenshot salvato in meta/ad_editor_1600.png")

        # Verifica se l'editor laterale o modale è aperto
        text = page.locator('body').inner_text()
        with open(PROJECT_ROOT / "meta" / "ad_editor_1600_text.txt", "w", encoding="utf-8") as f:
            f.write(text)

        lines = text.splitlines()
        print("\n=== MATCH ADVANTAGE / CREATIVITÀ ===")
        for i, l in enumerate(lines):
            ls = l.strip()
            if any(k in ls.lower() for k in ["advantage", "creativit", "immagine", "immagini", "generazione", "espansione", "sfondo", "musica", "ottimizz", "standard"]):
                print(f"L{i}: {ls}")
                ctx = " | ".join(lines[max(0, i-2):min(len(lines), i+3)])
                print(f"   Context: {ctx}")

    finally:
        context.close()

if __name__ == "__main__":
    run()

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
        url = f"https://adsmanager.facebook.com/adsmanager/manage/campaigns/?act={AD_ACCOUNT_ID}"
        print("Navigazione a:", url)
        page.goto(url, wait_until="domcontentloaded")
        time.sleep(6)

        # Trova tutti gli elementi cliccabili nella barra laterale sinistra
        side_items = page.locator('nav a, div[role="navigation"] a, div[role="navigation"] div[role="button"]').all()
        print(f"Elementi nella barra di navigazione: {len(side_items)}")
        for idx, item in enumerate(side_items):
            href = item.get_attribute("href")
            label = item.get_attribute("aria-label") or item.inner_text().replace("\n", " ").strip()
            print(f"[{idx}] href={href} | label='{label}'")

        # Cerca quello che corrisponde all'ingranaggio (gear)
        gear = None
        for item in side_items:
            href = item.get_attribute("href") or ""
            label = item.get_attribute("aria-label") or ""
            if "billing" in href or "setting" in href or "Impostazioni" in label:
                gear = item
                print(f"-> Selezionato gear: href={href}, label={label}")
                break

        if not gear and len(side_items) >= 9:
            # Di solito è terzultimo o quartultimo
            print("Uso elemento vicino alla fine...")
            gear = side_items[-3]

        if gear:
            gear.click()
            time.sleep(6)
            print("Dopo click su gear, URL:", page.url)
            page.screenshot(path=str(PROJECT_ROOT / "meta" / "after_gear_click.png"))

            # Ispezione testo e sottomenu
            lines = [l.strip() for l in page.locator("body").inner_text().splitlines() if l.strip()]
            print("\n--- TESTO DOPO CLICK SU GEAR ---")
            for l in lines[:40]:
                print(l)

    finally:
        context.close()

if __name__ == "__main__":
    run()

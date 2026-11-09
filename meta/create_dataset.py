import sys
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from meta.paths import get_cache_dir
from meta.browser import launch_meta_browser

AD_ACCOUNT_ID = "1116925509636183"
DATASET_NAME = "Naturale e sostenibile"
EVENTS_OVERVIEW_URL = f"https://eventsmanager.facebook.com/events_manager2/overview?act={AD_ACCOUNT_ID}"

def create_dataset(headless: bool = True):
    cache_dir = get_cache_dir()
    print("=" * 60)
    print(f"CREAZIONE NUOVO DATASET / PIXEL META: '{DATASET_NAME}'")
    print("=" * 60)

    context = launch_meta_browser(headless=headless)
    page = context.pages[0] if context.pages else context.new_page()

    try:
        print(f"Navigo su Events Manager: {EVENTS_OVERVIEW_URL}")
        page.goto(EVENTS_OVERVIEW_URL, wait_until="domcontentloaded")
        time.sleep(6)

        # Clicchiamo sul combobox 'Modlily'
        combo = page.locator('div[role="combobox"]:has-text("Modlily"), div[role="button"]:has-text("Modlily")').first
        if combo.count() == 0:
            print("Cerco dropdown dataset generico...")
            combo = page.locator('div[role="combobox"]').first

        combo.click()
        time.sleep(2)

        # Clicca su "Crea un nuovo dataset"
        create_option = page.locator('text=Crea un nuovo dataset').first
        print("Clicco su 'Crea un nuovo dataset'...")
        create_option.click()
        time.sleep(3)

        page.screenshot(path=str(cache_dir / "meta_create_dataset_step1.png"))

        # Compila il nome del dataset
        name_input = page.locator('input[type="text"]').first
        if name_input.count() > 0:
            print(f"Inserisco nome dataset: '{DATASET_NAME}'")
            name_input.fill(DATASET_NAME)
            time.sleep(1)

            # Clicca sul pulsante 'Crea' o 'Crea dataset'
            create_btn = page.locator('button:has-text("Crea")').first
            print("Clicco sul pulsante Crea...")
            create_btn.click()
            time.sleep(5)

        page.screenshot(path=str(cache_dir / "meta_create_dataset_step2.png"))

        # Recuperiamo il nuovo ID
        content = page.content()
        (cache_dir / "meta_created_dataset.html").write_text(content, encoding="utf-8")
        
        # Cerca ID nel testo
        body_text = page.inner_text("body")
        for line in body_text.splitlines():
            if "id:" in line.lower() or "dataset" in line.lower() or DATASET_NAME.lower() in line.lower():
                print("Info:", line.strip())

    except Exception as e:
        print(f"Errore durante la creazione del dataset: {e}")
    finally:
        context.close()

if __name__ == "__main__":
    is_headless = "--no-headless" not in sys.argv
    create_dataset(headless=is_headless)

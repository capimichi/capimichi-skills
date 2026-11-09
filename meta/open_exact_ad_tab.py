import sys
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from meta.paths import get_cache_dir
from meta.browser import launch_meta_browser

AD_ACCOUNT_ID = "1116925509636183"

def run():
    cache_dir = get_cache_dir()
    context = launch_meta_browser(headless=False)
    page = context.pages[0] if context.pages else context.new_page()

    try:
        url = f"https://adsmanager.facebook.com/adsmanager/manage/campaigns?act={AD_ACCOUNT_ID}"
        page.goto(url, wait_until="networkidle")
        time.sleep(5)

        # 1. Chiudi drawer laterale
        page.keyboard.press("Escape")
        time.sleep(1)

        # 2. Clicca su Rikrestin per selezionare la campagna
        print("Apertura campagna Rikrestin...")
        page.locator('text="Rikrestin 2x49 - Test Vendite"').first.click()
        time.sleep(4)

        # 3. Clicca sulla tab esatta delle INSERZIONI
        print("Click tab Inserzioni...")
        ads_tab = page.locator('text="Inserzioni per 1 Campagna", div[role="tab"]:has-text("Inserzioni per")').first
        if ads_tab.count() > 0:
            ads_tab.click()
            time.sleep(4)
        else:
            print("Tab Inserzioni per 1 Campagna non trovata col primo selettore, cerco alternativo...")
            page.get_by_role("tab", name="Inserzioni per 1 Campagna").click()
            time.sleep(4)

        shot = cache_dir / "ads_tab_exact_view.png"
        page.screenshot(path=str(shot))
        print("Screenshot tab Inserzioni:", shot)

        # Seleziona la riga dell'inserzione e clicca Modifica
        chk = page.locator('div[role="row"] input[type="checkbox"]').all()
        if len(chk) >= 2:
            chk[1].click(force=True)
            time.sleep(1)

        mod = page.locator('button:has-text("Modifica")').first
        if mod.count() > 0:
            print("Click Modifica inserzione...")
            mod.click()
            time.sleep(5)

        shot_mod = cache_dir / "real_ad_edit_panel.png"
        page.screenshot(path=str(shot_mod))
        print("Screenshot pannello Modifica:", shot_mod)

        # Ispeziona selettori interni dell'editor
        print("\n--- ISPEZIONE CAMPI EDITING ---")
        combos = page.locator('div[role="combobox"]').all()
        for idx, c in enumerate(combos):
            print(f"Combobox {idx}: {c.inner_text()[:60].replace(chr(10), ' ')}")

        radios = page.locator('div[role="radio"]').all()
        for idx, r in enumerate(radios):
            print(f"Radio {idx}: {r.inner_text().strip()}")

    finally:
        context.close()

if __name__ == "__main__":
    run()

import sys
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from meta.browser import launch_meta_browser

AD_ACCOUNT_ID = "1116925509636183"
CAMPAIGN_ID = "120251426951480676"
IMAGE_PATH = PROJECT_ROOT / "meta" / "assets" / "rikrestin_ad_b_graphic.jpeg"

def run():
    context = launch_meta_browser(
        headless=True,
        args=["--window-size=2000,1080"],
        viewport={"width": 2000, "height": 1080}
    )
    page = context.pages[0] if context.pages else context.new_page()

    try:
        url = f"https://adsmanager.facebook.com/adsmanager/manage/ads?act={AD_ACCOUNT_ID}&selected_campaign_ids={CAMPAIGN_ID}"
        page.goto(url, wait_until="domcontentloaded")
        time.sleep(8)
        page.keyboard.press("Escape")
        time.sleep(2)

        page.locator('[role="tab"]:has-text("Inserz")').last.click()
        time.sleep(2)

        page.locator(':text("Inserzione B - Offerta COD"), :text("Inserzione senza nome"), :text("In bozza")').first.click()
        time.sleep(2)

        page.locator('div[role="toolbar"] button:has-text("Modifica"), div[role="toolbar"] div[role="button"]:has-text("Modifica")').first.click()
        time.sleep(6)

        page.evaluate("""() => {
            const container = Array.from(document.querySelectorAll('div')).find(el => el.scrollHeight > 3000 && el.clientHeight < 1000);
            if (container) container.scrollTop = 1500;
        }""")
        time.sleep(2)

        add_btn = page.locator('div[role="button"]:has-text("Aggiungi contenuto multimediale"), button:has-text("Aggiungi contenuto multimediale")').first
        add_btn.click()
        time.sleep(2)

        add_img = page.locator(':text("Aggiungi un\'immagine"), :text("Aggiungi immagine")').first
        add_img.click()
        time.sleep(5)

        # Clicca + Carica
        carica_btn = page.locator('button:has-text("Carica"), div[role="button"]:has-text("Carica")').last
        with page.expect_file_chooser() as fc_info:
            carica_btn.click()
        
        file_chooser = fc_info.value
        file_chooser.set_files(str(IMAGE_PATH))
        time.sleep(6)

        # Trova bbox di Salva via JS
        salva_info = page.evaluate("""() => {
            const btns = Array.from(document.querySelectorAll('button, div[role="button"]'));
            const s = btns.find(b => b.innerText && b.innerText.trim() === 'Salva');
            if (s) {
                const rect = s.getBoundingClientRect();
                s.click();
                return {found: true, rect: rect};
            }
            return {found: false};
        }""")
        print("Salva info:", salva_info)
        time.sleep(6)

        page.screenshot(path=str(PROJECT_ROOT / "meta" / "after_js_salva.png"))
        print("Screenshot salvato in meta/after_js_salva.png")

        # Verifica bottoni attuali
        btns_after = page.evaluate("""() => {
            return Array.from(document.querySelectorAll('button, div[role="button"]'))
                .filter(b => b.offsetWidth > 0 && b.offsetHeight > 0)
                .map(b => b.innerText.trim().replace(/\\n/g, ' '))
                .filter(t => t.length > 0 && t.length < 50);
        }""")
        print("Bottoni visibili dopo Salva:", btns_after)

    finally:
        context.close()

if __name__ == "__main__":
    run()

import sys
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from meta.browser import launch_meta_browser

AD_ACCOUNT_ID = "1116925509636183"
CAMPAIGN_ID = "120251426951480676"

def run():
    print("=" * 60)
    print("CLICK PUBBLICA DEFINITIVO SUL MODALE ANTEPRIMA")
    print("=" * 60)

    context = launch_meta_browser(headless=True, args=["--window-size=2000,1080"], viewport={"width": 2000, "height": 1080})
    page = context.pages[0] if context.pages else context.new_page()

    try:
        url = f"https://adsmanager.facebook.com/adsmanager/manage/ads?act={AD_ACCOUNT_ID}&selected_campaign_ids={CAMPAIGN_ID}"
        page.goto(url, wait_until="domcontentloaded")
        time.sleep(8)
        page.keyboard.press("Escape")
        time.sleep(1)

        page.locator('[role="tab"]:has-text("Inserz")').last.click()
        time.sleep(3)

        page.locator(':text("Inserzione B - Offerta COD"), :text("Inserzione senza nome"), :text("In bozza")').first.click()
        time.sleep(2)

        page.locator('div[role="toolbar"] button:has-text("Modifica"), div[role="toolbar"] div[role="button"]:has-text("Modifica")').first.click()
        time.sleep(6)

        # Clicca "Visualizza l'anteprima per pubblicare" oppure "Pubblica"
        pub_preview = page.locator('button:has-text("Visualizza l\'anteprima per pubblicare"), div[role="button"]:has-text("Visualizza l\'anteprima per pubblicare"), button:has-text("Pubblica"), div[role="button"]:has-text("Pubblica")').last
        print("Clicco pulsante iniziale:", pub_preview.inner_text().strip())
        pub_preview.click()
        time.sleep(3)

        # Se c'è Salta
        salta = page.locator('button:has-text("Salta"), div[role="button"]:has-text("Salta")').first
        if salta.count() > 0 and salta.is_visible():
            print("Clicco Salta...")
            salta.click()
            time.sleep(4)

        page.screenshot(path="meta/modal_anteprima_shown.png")

        # Clicca il pulsante verde Pubblica nel modale Anteprima
        # In after_salta_click.png, il pulsante è verde con testo 'Pubblica' in basso a destra
        print("Cerco il pulsante verde Pubblica...")
        res = page.evaluate("""() => {
            const btns = Array.from(document.querySelectorAll('button, div[role="button"]')).filter(b => 
                b.innerText && b.innerText.trim() === 'Pubblica'
            );
            if (btns.length > 0) {
                const target = btns[btns.length - 1];
                target.click();
                return { success: true, text: target.innerText };
            }
            return { success: false, count: btns.length };
        }""")
        print("Click Pubblica result:", res)
        time.sleep(8)

        # Controlla se compare il popup 'Esamina le bozze' / 'WhatsApp glitch'
        page.screenshot(path="meta/after_green_pubblica_click.png")
        
        # Gestisci eventuale errore WhatsApp / Prova a pubblicare elementi con errori
        bypass = page.evaluate("""() => {
            const chk = Array.from(document.querySelectorAll('input[type="checkbox"], div[role="checkbox"]')).find(c => 
                (c.parentElement && c.parentElement.innerText.includes('Prova a pubblicare')) ||
                (c.innerText && c.innerText.includes('Prova a pubblicare'))
            );
            if (chk) {
                chk.click();
                return "checked_force";
            }
            return "not_found";
        }""")
        print("Bypass checkbox result:", bypass)
        if bypass == "checked_force":
            time.sleep(2)
            page.evaluate("""() => {
                const btns = Array.from(document.querySelectorAll('button, div[role="button"]')).filter(b => 
                    b.innerText && b.innerText.trim() === 'Pubblica'
                );
                if (btns.length > 0) btns[btns.length - 1].click();
            }""")
            time.sleep(10)

        # Attesa pubblicazione
        time.sleep(10)
        page.screenshot(path="meta/publish_result_screen.png")

        # Ricarica tabella per vedere lo stato finale
        page.goto(url, wait_until="domcontentloaded")
        time.sleep(8)
        page.keyboard.press("Escape")
        time.sleep(1)
        page.locator('[role="tab"]:has-text("Inserz")').last.click()
        time.sleep(4)
        page.screenshot(path="meta/ads_table_final_proof.png")
        print("Tabella finale salvata in meta/ads_table_final_proof.png")

    finally:
        context.close()

if __name__ == "__main__":
    run()

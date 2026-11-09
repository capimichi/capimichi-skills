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
    print("=== DISATTIVAZIONE AD A (SWITCH 1) ===")
    context = launch_meta_browser(headless=True, args=["--window-size=2000,1080"], viewport={"width": 2000, "height": 1080})
    page = context.pages[0] if context.pages else context.new_page()

    try:
        url = f"https://adsmanager.facebook.com/adsmanager/manage/ads?act={AD_ACCOUNT_ID}&selected_campaign_ids={CAMPAIGN_ID}"
        print(f"Navigazione a: {url}")
        page.goto(url, wait_until="domcontentloaded")
        time.sleep(8)
        page.keyboard.press("Escape")
        time.sleep(1)

        # Tab Inserzioni
        page.locator('[role="tab"]:has-text("Inserz")').last.click()
        time.sleep(4)

        # Trova i due switch "Sì/no"
        switches = page.locator('input[role="switch"][aria-label="Sì/no"]').all()
        print(f"Trovati {len(switches)} switch Sì/no.")
        
        ad_b_box = page.locator(':text("Inserzione B - Offerta COD & Spedizione Gratis")').first.bounding_box()
        ad_a_box = page.locator(':text("Nuova inserzione Vendite")').first.bounding_box()
        print("Ad B y:", ad_b_box["y"] if ad_b_box else None)
        print("Ad A y:", ad_a_box["y"] if ad_a_box else None)

        # Lo switch per Ad A è quello con coordinata y più vicina ad Ad A
        ad_a_switch = None
        for i, s in enumerate(switches):
            box = s.bounding_box()
            if box and ad_a_box and abs(box["y"] - ad_a_box["y"]) < 30:
                ad_a_switch = s
                print(f"Switch {i} corrisponde ad Ad A (y={box['y']}, checked={s.get_attribute('aria-checked')})")
                break
        
        if not ad_a_switch and len(switches) >= 2:
            ad_a_switch = switches[1]
            print("Fallback: uso switches[1] per Ad A")

        if ad_a_switch:
            # Clicchiamo lo switch
            print("Clicco sullo switch di Ad A...")
            ad_a_switch.click(force=True)
            time.sleep(3)
            page.screenshot(path="meta/after_pause_ad_a_click.png")

            # Verifica eventuale modale
            modals = page.locator('div[role="dialog"]')
            if modals.count() > 0:
                print("Modale presente dopo il click:")
                print(modals.inner_text()[:300])
                disattiva = modals.locator('button:has-text("Disattiva"), button:has-text("Conferma"), button:has-text("Continua")').first
                if disattiva.count() > 0:
                    disattiva.click()
                    time.sleep(3)

            # Controlla se c'è un pulsante "Rivedi e pubblica" o "Pubblica"
            pub_btn = page.locator('button:has-text("Rivedi e pubblica"), button:has-text("Pubblica 1")').first
            if pub_btn.count() > 0 and pub_btn.is_visible():
                print(f"Trovato pulsante: {pub_btn.inner_text()}, clicco...")
                pub_btn.click()
                time.sleep(4)

            # Ricarica/aggiorna tabella
            time.sleep(2)
            ref = page.locator('[aria-label="Aggiorna dati tabella"]').first
            if ref.count() > 0:
                ref.click()
                time.sleep(4)

            page.screenshot(path="meta/final_status_after_pause.png")
            print("Screenshot finale salvato in meta/final_status_after_pause.png")

            # Verifica stato finale degli switch
            switches_after = page.locator('input[role="switch"][aria-label="Sì/no"]').all()
            for i, s in enumerate(switches_after):
                box = s.bounding_box()
                checked = s.get_attribute("aria-checked")
                print(f"Stato finale Switch {i}: y={box['y'] if box else None}, checked={checked}")

            # Dump del testo della tabella
            body_txt = page.locator("body").inner_text()
            with open("meta/pause_verified_dump.txt", "w", encoding="utf-8") as f:
                f.write(body_txt)

    finally:
        context.close()

if __name__ == "__main__":
    run()

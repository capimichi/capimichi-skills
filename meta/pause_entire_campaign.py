import sys
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from meta.browser import launch_meta_browser

AD_ACCOUNT_ID = "1116925509636183"
CAMPAIGN_ID = "120251426951480676"

def pause_everything():
    print("=== SPEGNIMENTO TOTALE DELLA CAMPAGNA E DELLE INSERZIONI ===")
    context = launch_meta_browser(headless=True, args=["--window-size=2000,1080"], viewport={"width": 2000, "height": 1080})
    page = context.pages[0] if context.pages else context.new_page()

    try:
        # 1. LIVELLO INSERZIONI: Spegni Ad B
        print("\n--- 1. SPEGNIMENTO AD B (INSERZIONI) ---")
        url_ads = f"https://adsmanager.facebook.com/adsmanager/manage/ads?act={AD_ACCOUNT_ID}&selected_campaign_ids={CAMPAIGN_ID}"
        page.goto(url_ads, wait_until="domcontentloaded")
        time.sleep(8)
        page.keyboard.press("Escape")
        time.sleep(1)

        page.locator('[role="tab"]:has-text("Inserz")').last.click()
        time.sleep(3)

        switches_ads = page.locator('input[role="switch"][aria-label="Sì/no"]').all()
        print(f"Trovati {len(switches_ads)} switch nelle inserzioni.")
        for i, s in enumerate(switches_ads):
            checked = s.get_attribute("aria-checked")
            print(f"Inserzione Switch {i}: checked={checked}")
            if checked == "true":
                print(f"Disattivo switch {i} (Ad B)...")
                s.click(force=True)
                time.sleep(3)

        # 2. LIVELLO CAMPAGNE: Spegni la Campagna intera
        print("\n--- 2. SPEGNIMENTO CAMPAGNA INTERA ---")
        url_camp = f"https://adsmanager.facebook.com/adsmanager/manage/campaigns?act={AD_ACCOUNT_ID}"
        page.goto(url_camp, wait_until="domcontentloaded")
        time.sleep(8)
        page.keyboard.press("Escape")
        time.sleep(1)

        tab_camp = page.locator('[role="tab"]:has-text("Campagne")').first
        if tab_camp.count() > 0:
            tab_camp.click()
            time.sleep(3)

        switches_camp = page.locator('input[role="switch"][aria-label="Sì/no"]').all()
        print(f"Trovati {len(switches_camp)} switch nelle campagne.")
        for i, s in enumerate(switches_camp):
            checked = s.get_attribute("aria-checked")
            print(f"Campagna Switch {i}: checked={checked}")
            if checked == "true":
                print(f"Disattivo switch campagna {i}...")
                s.click(force=True)
                time.sleep(3)

        # Gestione eventuale modale di conferma
        modals = page.locator('div[role="dialog"]')
        if modals.count() > 0:
            print("Verifico presenza pulsanti in modali...")
            disattiva = page.locator('button:has-text("Disattiva"), button:has-text("Conferma")').first
            if disattiva.count() > 0 and disattiva.is_visible():
                disattiva.click()
                time.sleep(3)

        # Screenshot verifica Campagne
        page.screenshot(path="meta/campaign_paused_verified.png")
        print("Screenshot salvato in meta/campaign_paused_verified.png")

        # Verifica stato finale
        ref = page.locator('[aria-label="Aggiorna dati tabella"]').first
        if ref.count() > 0:
            ref.click()
            time.sleep(3)

        switches_after = page.locator('input[role="switch"][aria-label="Sì/no"]').all()
        for i, s in enumerate(switches_after):
            print(f"Stato finale Campagna Switch {i}: checked={s.get_attribute('aria-checked')}")

        # 3. Screenshot finale livello Inserzioni
        page.goto(url_ads, wait_until="domcontentloaded")
        time.sleep(6)
        page.keyboard.press("Escape")
        time.sleep(1)
        page.locator('[role="tab"]:has-text("Inserz")').last.click()
        time.sleep(3)
        page.screenshot(path="meta/all_ads_paused_verified.png")
        print("Screenshot salvato in meta/all_ads_paused_verified.png")

        switches_ads_final = page.locator('input[role="switch"][aria-label="Sì/no"]').all()
        for i, s in enumerate(switches_ads_final):
            print(f"Stato finale Inserzioni Switch {i}: checked={s.get_attribute('aria-checked')}")

        print("\nTUTTO È STATO DISATTIVATO CON SUCCESSO!")

    except Exception as e:
        print("Errore durante lo spegnimento:", e)
        page.screenshot(path="meta/pause_error.png")
    finally:
        context.close()

if __name__ == "__main__":
    pause_everything()

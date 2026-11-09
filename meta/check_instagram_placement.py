import sys
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from meta.browser import launch_meta_browser

AD_ACCOUNT_ID = "1116925509636183"

def run():
    print("=" * 60)
    print("VERIFICA POSIZIONAMENTI E IDENTITA INSTAGRAM")
    print("=" * 60)

    context = launch_meta_browser(headless=True)
    page = context.pages[0] if context.pages else context.new_page()

    try:
        # 1. Ispeziona a livello Inserzione
        url_ad = f"https://adsmanager.facebook.com/adsmanager/manage/ads?act={AD_ACCOUNT_ID}&selected_campaign_ids=120251426951480676&treenav=true"
        page.goto(url_ad, wait_until="domcontentloaded")
        time.sleep(5)

        # Tab Inserzioni
        page.get_by_role("tab", name="Inserzioni per 1 Campagna", exact=True).click()
        time.sleep(3)

        # Clicca Modifica inserzione
        mod = page.locator('div[role="row"]').nth(1).locator('button:has-text("Modifica")').first
        if mod.count() == 0:
            chk = page.locator('div[role="row"]').nth(1).locator('input[type="checkbox"]').first
            chk.click(force=True)
            time.sleep(1)
            mod = page.locator('button:has-text("Modifica")').first
        
        if mod.count() > 0:
            mod.click()
            time.sleep(4)

            # Cerca testo relativo a Instagram nel pannello di destra
            body_txt = page.locator('div[role="region"], form, body').first.inner_text()
            lines = [l.strip() for l in body_txt.splitlines() if "instagram" in l.lower()]
            print("Menzioni di Instagram nel livello Inserzione:")
            for l in lines[:10]:
                print(f"  - {l}")

        # 2. Ispeziona a livello Gruppo di Inserzioni (Posizionamenti)
        print("\nIspezione Posizionamenti nel Gruppo di Inserzioni...")
        page.get_by_role("tab", name="Gruppi di inserzioni per 1", exact=False).first.click()
        time.sleep(3)
        mod_adset = page.locator('div[role="row"]').nth(1).locator('button:has-text("Modifica")').first
        if mod_adset.count() == 0:
            page.locator('div[role="row"]').nth(1).locator('input[type="checkbox"]').first.click(force=True)
            time.sleep(1)
            mod_adset = page.locator('button:has-text("Modifica")').first

        if mod_adset.count() > 0:
            mod_adset.click()
            time.sleep(4)
            adset_txt = page.locator('body').inner_text()
            has_advantage = "posizionamenti advantage+" in adset_txt.lower() or "posizionamenti automatici" in adset_txt.lower()
            print(f"Posizionamenti Advantage+ (Include Instagram): {has_advantage}")

    finally:
        context.close()

if __name__ == "__main__":
    run()

import sys
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from meta.paths import get_cache_dir
from meta.browser import launch_meta_browser

AD_ACCOUNT_ID = "1116925509636183"

def pause():
    cache_dir = get_cache_dir()
    print("=" * 60)
    print("DISATTIVAZIONE CAMPAGNA RIKRESTIN (PAUSA IMMEDIATA)")
    print("=" * 60)

    context = launch_meta_browser(headless=True)
    page = context.pages[0] if context.pages else context.new_page()

    try:
        url = f"https://adsmanager.facebook.com/adsmanager/manage/campaigns?act={AD_ACCOUNT_ID}"
        print(f"Navigazione a: {url}")
        page.goto(url, wait_until="networkidle")
        time.sleep(5)

        # Clicca sulla tab "Campagne" se non già attiva
        camp_tab = page.locator('div[role="tab"]:has-text("Campagne"), button:has-text("Campagne")').first
        if camp_tab.count() > 0:
            camp_tab.click()
            time.sleep(2)

        # Cerca la riga di Rikrestin
        print("Ricerca riga 'Rikrestin 2x49 - Test Vendite'...")
        # Cerchiamo lo switch nella riga di Rikrestin
        row = page.locator('div[role="row"]:has-text("Rikrestin")').first
        if row.count() > 0:
            print("Riga Rikrestin trovata!")
            switch = row.locator('input[type="checkbox"][role="switch"], div[role="switch"], button[role="switch"]').first
            if switch.count() == 0:
                # Prova semplicemente lo switch o input checkbox dentro la cella No/Sì
                switch = row.locator('div[role="checkbox"], input[role="switch"], [aria-label*="Attiva"], [aria-label*="Disattiva"]').first
            
            if switch.count() > 0:
                print(f"Switch trovato! Stato aria-checked: {switch.get_attribute('aria-checked')}")
                switch.click()
                print("Cliccato per spegnere lo switch!")
                time.sleep(3)
            else:
                # Fallback: cerca qualsiasi switch attivo nella riga
                print("Cerco qualsiasi elemento interattivo switch nella riga...")
                switches = row.locator('input, button, [role="button"]').all()
                for s in switches:
                    if s.get_attribute('role') == 'switch' or 'switch' in (s.get_attribute('class') or ''):
                        s.click()
                        time.sleep(2)
                        break
        else:
            print("Riga Rikrestin non trovata direttamente per testo. Cerco tutti gli switch attivi...")
            all_switches = page.locator('[role="switch"][aria-checked="true"]').all()
            print(f"Trovati {len(all_switches)} switch attivi.")
            for s in all_switches:
                s.click()
                time.sleep(1)

        time.sleep(3)
        # Salva screenshot di conferma
        confirm_shot = cache_dir / "campaign_paused_confirm.png"
        page.screenshot(path=str(confirm_shot))
        print(f"Screenshot di conferma salvato: {confirm_shot}")

        # Stampa testo righe
        rows = page.locator('div[role="row"]').all()
        for i, r in enumerate(rows):
            txt = r.inner_text().strip().replace('\n', ' | ')
            if 'Rikrestin' in txt:
                print(f"Stato aggiornato Rikrestin: {txt}")

    finally:
        context.close()

if __name__ == "__main__":
    pause()

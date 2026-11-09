import sys
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from meta.browser import launch_meta_browser

AD_ACCOUNT_ID = "1116925509636183"
URL = f"https://adsmanager.facebook.com/adsmanager/manage/campaigns?act={AD_ACCOUNT_ID}"

def run():
    print("=" * 60)
    print("AVVIO CONFIGURAZIONE GUIDATA META ADS (HEADLESS=FALSE)")
    print("=" * 60)

    context = launch_meta_browser(headless=False)
    page = context.pages[0] if context.pages else context.new_page()

    try:
        print("1. Apertura Ads Manager...")
        page.goto(URL, wait_until="networkidle")
        time.sleep(4)

        # Seleziona la campagna Rikrestin
        print("2. Apertura bozza campagna Rikrestin...")
        row_camp = page.locator('text="Rikrestin 2x49 - Test Vendite"').first
        if row_camp.count() > 0:
            row_camp.click()
            time.sleep(3)
        else:
            print("Cerco la riga nella tabella...")
            # Clicca sulla prima riga di bozza
            first_row = page.locator('div[role="row"]:has-text("Vendite"), tr:has-text("Vendite")').first
            if first_row.count() > 0:
                first_row.locator('input[type="checkbox"]').first.click(force=True)
                time.sleep(1)
                page.locator('button:has-text("Modifica"), div[role="button"]:has-text("Modifica")').first.click()
                time.sleep(3)

        # Ora andiamo sul Gruppo di Inserzioni
        print("3. Navigazione a Gruppo di Inserzioni...")
        # Clicca sull'icona a 4 quadratini nel menu laterale o nel breadcrumb
        adset_tab = page.locator('div[role="treeitem"]:has-text("Gruppo di"), [data-testid="adset-tab"], div[role="tab"]:has-text("Gruppi di inserzioni")').first
        if adset_tab.count() > 0:
            adset_tab.click()
            time.sleep(3)

        print("Pannello gruppo di inserzioni aperto. Cerco pixel e destinazione...")
        time.sleep(2)

        # Cerco la sezione Pixel / Dataset
        # Cerco dropdown o testo con Dataset / Pixel
        pixel_dropdown = page.locator('div:has-text("Pixel"), div:has-text("Set di dati"), div:has-text("Dataset")').filter(has=page.locator('div[role="button"], input, select'))
        print("Pixel dropdown candidati:", pixel_dropdown.count())

        # Cerco input budget per impostare 5.00
        budget_inputs = page.locator('input[type="text"]').filter(has_text="").all()
        for inp in budget_inputs:
            val = inp.input_value()
            pl = inp.get_attribute('placeholder') or ''
            # Se ha un valore numerico come 20 o 20,00 o placeholder €
            if any(c in val for c in ['20', '10', '15', '50']) or '€' in pl:
                print(f"Trovato campo budget con valore attuale: {val}")
                inp.fill("5,00")
                time.sleep(1)
                break

        print("\nPronto per la configurazione! Mantengo il browser aperto per procedere insieme.")
        while True:
            time.sleep(2)
            if not context.pages or all(p.is_closed() for p in context.pages):
                break

    except KeyboardInterrupt:
        pass
    except Exception as e:
        print(f"Info: {e}")
    finally:
        try:
            context.close()
        except Exception:
            pass

if __name__ == "__main__":
    run()

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
        url = f"https://adsmanager.facebook.com/adsmanager/manage/ads?act={AD_ACCOUNT_ID}&selected_campaign_ids=120251426951480676&treenav=true"
        page.goto(url, wait_until="networkidle")
        time.sleep(5)

        # Clicca sulla tab Inserzioni per 1 Campagna
        tab = page.get_by_role("tab", name="Inserzioni per 1 Campagna", exact=True)
        if tab.count() > 0:
            tab.click()
            time.sleep(3)

        # Hover sulla riga per cliccare Modifica o Grafici
        row = page.locator('div[role="row"]').nth(1)
        row.hover()
        time.sleep(1)

        # Clicca su Modifica per verificare il testo e il link salvato
        mod = page.locator('button:has-text("Modifica")').first
        if mod.count() > 0:
            mod.click()
            time.sleep(4)

        page.screenshot(path=str(PROJECT_ROOT / "meta" / "published_ad_inspect.png"))
        
        # Verifica presenza link naturalesostenibile
        body_text = page.locator('body').inner_text()
        has_domain = "naturalesostenibile.pagead.online" in body_text
        has_cta = "Scopri di più" in body_text or "Ordina ora" in body_text or "Acquista ora" in body_text
        print(f"Verifica Dominio 'naturalesostenibile.pagead.online' presente: {has_domain}")
        print(f"Verifica CTA presente: {has_cta}")

    finally:
        context.close()

if __name__ == "__main__":
    run()

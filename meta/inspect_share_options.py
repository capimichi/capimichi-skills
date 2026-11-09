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
        url = f"https://adsmanager.facebook.com/adsmanager/manage/campaigns?act={AD_ACCOUNT_ID}"
        page.goto(url, wait_until="domcontentloaded")
        time.sleep(5)

        # Clicca sulla campagna Rikrestin
        page.locator('text="Rikrestin 2x49 - Test Vendite"').first.click()
        time.sleep(3)

        # Tab Inserzioni
        page.get_by_role("tab", name="Inserzioni per 1 Campagna", exact=True).click()
        time.sleep(3)

        # Seleziona riga
        chk = page.locator('div[role="row"]').nth(1).locator('input[type="checkbox"]').first
        if chk.count() > 0:
            chk.click(force=True)
            time.sleep(1)

        # Clicca Anteprima
        page.locator('button:has-text("Anteprima"), div[role="button"]:has-text("Anteprima")').first.click()
        time.sleep(4)

        # Clicca Condividi
        share = page.locator('button:has-text("Condividi"), div[role="button"]:has-text("Condividi")').first
        share.click()
        time.sleep(2)

        # Cerca tutte le opzioni nel menu Condividi
        menu_items = page.locator('div[role="menuitem"], div[role="option"], a').all()
        for m in menu_items:
            t = m.inner_text().strip().replace('\n', ' | ')
            h = m.get_attribute('href')
            if 'Facebook' in t or 'link' in t or 'comment' in t:
                print(f"Opzione: {t} -> href={h}")

        # Clicchiamo su 'Post di Facebook con commenti'
        post_comments = page.locator('text="Post di Facebook con commenti"').first
        if post_comments.count() > 0:
            print("Clicco su 'Post di Facebook con commenti'...")
            # Spesso apre una nuova scheda o popup con il link diretto al post
            with context.expect_page(timeout=10000) as new_page_info:
                post_comments.click()
            new_page = new_page_info.value
            new_page.wait_until("domcontentloaded")
            time.sleep(4)
            print(f"URL DIRETTO POST CON COMMENTI: {new_page.url}")
            new_page.close()

    except Exception as e:
        print(f"Info / Exception: {e}")
    finally:
        context.close()

if __name__ == "__main__":
    run()

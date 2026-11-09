import sys
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from worldfilia.paths import get_cache_dir
from worldfilia.browser import launch_worldfilia_browser

CAMPAIGN_ID = 5540
PIXEL_ID = "763646865919553"

PIXEL_CODE = f"""<!-- Meta Pixel Code for Rikrestin 2x49 (Naturale e sostenibile) -->
<script>
!function(f,b,e,v,n,t,s)
{{if(f.fbq)return;n=f.fbq=function(){{n.callMethod?
n.callMethod.apply(n,arguments):n.queue.push(arguments)}};
if(!f._fbq)f._fbq=n;n.push=n;n.loaded=!0;n.version='2.0';
n.queue=[];t=b.createElement(e);t.async=!0;
t.src=v;s=b.getElementsByTagName(e)[0];
s.parentNode.insertBefore(t,s)}}(window, document,'script',
'https://connect.facebook.net/en_US/fbevents.js');
fbq('init', '{PIXEL_ID}');
fbq('track', 'PageView');
fbq('track', 'Purchase', {{
  value: Number('[[commission]]') || 24.00,
  currency: 'EUR'
}});
</script>
<noscript>
 <img height="1" width="1" style="display:none"
 src="https://www.facebook.com/tr?id={PIXEL_ID}&ev=Purchase&noscript=1"/>
</noscript>
"""

def set_campaign_pixel(campaign_id: int = CAMPAIGN_ID, headless: bool = True):
    cache_dir = get_cache_dir()
    print("=" * 60)
    print(f"IMPOSTAZIONE PIXEL META ({PIXEL_ID}) SU WORLDFILIA")
    print(f"Campagna: {campaign_id} (Rikrestin 2x49)")
    print("=" * 60)

    context = launch_worldfilia_browser(headless=headless)
    page = context.pages[0] if context.pages else context.new_page()

    try:
        url = f"https://portal.worldfilia.net/publisher/campaigns/{campaign_id}"
        print(f"1. Navigazione a: {url}")
        page.goto(url, wait_until="domcontentloaded")
        time.sleep(4)

        # Gestione eventuale popup notifiche
        no_thanks = page.locator("text=No thanks")
        if no_thanks.count() > 0:
            no_thanks.first.click()
            time.sleep(1)

        # Clicca sul tab POSTBACKS/PIXELS
        print("2. Apertura tab POSTBACKS/PIXELS...")
        page.locator("text=POSTBACKS/PIXELS").first.click()
        time.sleep(2)

        # Clicca sulla card ON SALE
        print("3. Apertura modale ON SALE...")
        page.locator("text=ON SALE").first.click()
        time.sleep(2)

        # Inserimento codice tramite CodeMirror
        print("4. Inserimento codice Meta Pixel...")
        page.evaluate(
            """(code) => {
                const cmElement = document.querySelector('.CodeMirror');
                if (cmElement && cmElement.CodeMirror) {
                    cmElement.CodeMirror.setValue(code);
                    return true;
                }
                return false;
            }""",
            PIXEL_CODE
        )
        time.sleep(1)

        # Screenshot prima di confermare
        page.screenshot(path=str(cache_dir / "worldfilia_pixel_inserted.png"))

        # Clicca su Conferma
        print("5. Salvataggio impostazioni...")
        confirm_btn = page.locator('button:has-text("Conferma")').first
        confirm_btn.click()
        time.sleep(3)

        # Screenshot dopo il salvataggio
        page.screenshot(path=str(cache_dir / "worldfilia_pixel_saved.png"))
        print("Pixel salvato con successo su Worldfilia!")

    except Exception as e:
        print(f"Errore durante l'inserimento del pixel: {e}")
    finally:
        context.close()

if __name__ == "__main__":
    is_headless = "--no-headless" not in sys.argv
    set_campaign_pixel(headless=is_headless)

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

CLICK_PIXEL_CODE = f"""<!-- Meta Pixel Code for Rikrestin 2x49 ON CLICK (ViewContent) -->
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
fbq('track', 'ViewContent', {{
  content_name: 'Rikrestin 2x49',
  content_category: 'Capelli',
  value: 49.99,
  currency: 'EUR'
}});
</script>
<noscript>
 <img height="1" width="1" style="display:none"
 src="https://www.facebook.com/tr?id={PIXEL_ID}&ev=ViewContent&noscript=1"/>
</noscript>
"""

def set_click_pixel(campaign_id: int = CAMPAIGN_ID, headless: bool = True):
    cache_dir = get_cache_dir()
    print("=" * 60)
    print(f"IMPOSTAZIONE PIXEL META ON CLICK ({PIXEL_ID}) SU WORLDFILIA")
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

        # Clicca sulla card ON CLICK
        print("3. Apertura modale ON CLICK...")
        page.locator("text=ON CLICK").first.click()
        time.sleep(2)

        # Inserimento codice tramite CodeMirror
        print("4. Inserimento codice Meta Pixel ViewContent...")
        page.evaluate(
            """(code) => {
                const cmElement = document.querySelector('.CodeMirror');
                if (cmElement && cmElement.CodeMirror) {
                    cmElement.CodeMirror.setValue(code);
                    return true;
                }
                return false;
            }""",
            CLICK_PIXEL_CODE
        )
        time.sleep(1)

        # Clicca su Conferma
        print("5. Salvataggio impostazioni ON CLICK...")
        confirm_btn = page.locator('button:has-text("Conferma")').first
        confirm_btn.click()
        time.sleep(3)

        # Screenshot dopo il salvataggio
        screenshot_path = cache_dir / "worldfilia_click_pixel_saved.png"
        page.screenshot(path=str(screenshot_path))
        print(f"Pixel ON CLICK salvato con successo! Screenshot in: {screenshot_path}")

    except Exception as e:
        print(f"Errore durante l'inserimento del pixel ON CLICK: {e}")
    finally:
        context.close()

if __name__ == "__main__":
    is_headless = "--no-headless" not in sys.argv
    set_click_pixel(headless=is_headless)

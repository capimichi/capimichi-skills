"""
Worldfilia Pixel Management Commands (via CloakBrowser).
"""

import time
import click
from pathlib import Path


@click.group(name="pixel", help="Gestione e iniezione Meta Pixel sulle campagne Worldfilia via browser.")
def pixel_group():
    pass


@pixel_group.command(name="set-sale", help="Imposta il codice Pixel (evento Purchase) nella sezione ON SALE di una campagna.")
@click.argument("campaign_id", type=int)
@click.argument("pixel_id")
@click.option("--value", default="24.00", help="Valore predefinito conversione (default: 24.00).")
@click.option("--visible", is_flag=True, default=False, help="Mostra il browser durante l'operazione.")
def set_sale_pixel(campaign_id: int, pixel_id: str, value: str, visible: bool):
    from worldfilia.paths import get_cache_dir
    from worldfilia.browser import launch_worldfilia_browser

    code = f"""<!-- Meta Pixel Code for Campaign #{campaign_id} (Purchase) -->
<script>
!function(f,b,e,v,n,t,s)
{{if(f.fbq)return;n=f.fbq=function(){{n.callMethod?
n.callMethod.apply(n,arguments):n.queue.push(arguments)}};
if(!f._fbq)f._fbq=n;n.push=n;n.loaded=!0;n.version='2.0';
n.queue=[];t=b.createElement(e);t.async=!0;
t.src=v;s=b.getElementsByTagName(e)[0];
s.parentNode.insertBefore(t,s)}}(window, document,'script',
'https://connect.facebook.net/en_US/fbevents.js');
fbq('init', '{pixel_id}');
fbq('track', 'PageView');
fbq('track', 'Purchase', {{
  value: Number('[[commission]]') || {value},
  currency: 'EUR'
}});
</script>
<noscript>
 <img height="1" width="1" style="display:none"
 src="https://www.facebook.com/tr?id={pixel_id}&ev=Purchase&noscript=1"/>
</noscript>
"""

    cache_dir = get_cache_dir()
    click.echo(f"Impostazione pixel ON SALE ({pixel_id}) sulla campagna #{campaign_id}...")
    context = launch_worldfilia_browser(headless=not visible)
    page = context.pages[0] if context.pages else context.new_page()

    try:
        url = f"https://portal.worldfilia.net/publisher/campaigns/{campaign_id}"
        page.goto(url, wait_until="domcontentloaded")
        time.sleep(4)

        no_thanks = page.locator("text=No thanks")
        if no_thanks.count() > 0:
            no_thanks.first.click()
            time.sleep(1)

        page.locator("text=POSTBACKS/PIXELS").first.click()
        time.sleep(2)

        page.locator("text=ON SALE").first.click()
        time.sleep(2)

        page.evaluate(
            """(c) => {
                const cmElement = document.querySelector('.CodeMirror');
                if (cmElement && cmElement.CodeMirror) {
                    cmElement.CodeMirror.setValue(c);
                    return true;
                }
                return false;
            }""",
            code
        )
        time.sleep(1)

        confirm_btn = page.locator('button:has-text("Conferma")').first
        confirm_btn.click()
        time.sleep(3)
        page.screenshot(path=str(cache_dir / f"worldfilia_pixel_{campaign_id}_saved.png"))
        click.echo("✅ Pixel salvato con successo!")
    finally:
        context.close()


@pixel_group.command(name="set-click", help="Imposta il codice Pixel (evento ViewContent) nella sezione ON CLICK di una campagna.")
@click.argument("campaign_id", type=int)
@click.argument("pixel_id")
@click.option("--product-name", default="Prodotto", help="Nome prodotto per evento ViewContent.")
@click.option("--value", default="49.99", help="Valore stimato carrello/click.")
@click.option("--visible", is_flag=True, default=False, help="Mostra il browser durante l'operazione.")
def set_click_pixel(campaign_id: int, pixel_id: str, product_name: str, value: str, visible: bool):
    from worldfilia.paths import get_cache_dir
    from worldfilia.browser import launch_worldfilia_browser

    code = f"""<!-- Meta Pixel Code for Campaign #{campaign_id} ON CLICK (ViewContent) -->
<script>
!function(f,b,e,v,n,t,s)
{{if(f.fbq)return;n=f.fbq=function(){{n.callMethod?
n.callMethod.apply(n,arguments):n.queue.push(arguments)}};
if(!f._fbq)f._fbq=n;n.push=n;n.loaded=!0;n.version='2.0';
n.queue=[];t=b.createElement(e);t.async=!0;
t.src=v;s=b.getElementsByTagName(e)[0];
s.parentNode.insertBefore(t,s)}}(window, document,'script',
'https://connect.facebook.net/en_US/fbevents.js');
fbq('init', '{pixel_id}');
fbq('track', 'PageView');
fbq('track', 'ViewContent', {{
  content_name: '{product_name}',
  value: {value},
  currency: 'EUR'
}});
</script>
<noscript>
 <img height="1" width="1" style="display:none"
 src="https://www.facebook.com/tr?id={pixel_id}&ev=ViewContent&noscript=1"/>
</noscript>
"""

    cache_dir = get_cache_dir()
    click.echo(f"Impostazione pixel ON CLICK ({pixel_id}) sulla campagna #{campaign_id}...")
    context = launch_worldfilia_browser(headless=not visible)
    page = context.pages[0] if context.pages else context.new_page()

    try:
        url = f"https://portal.worldfilia.net/publisher/campaigns/{campaign_id}"
        page.goto(url, wait_until="domcontentloaded")
        time.sleep(4)

        no_thanks = page.locator("text=No thanks")
        if no_thanks.count() > 0:
            no_thanks.first.click()
            time.sleep(1)

        page.locator("text=POSTBACKS/PIXELS").first.click()
        time.sleep(2)

        page.locator("text=ON CLICK").first.click()
        time.sleep(2)

        page.evaluate(
            """(c) => {
                const cmElement = document.querySelector('.CodeMirror');
                if (cmElement && cmElement.CodeMirror) {
                    cmElement.CodeMirror.setValue(c);
                    return true;
                }
                return false;
            }""",
            code
        )
        time.sleep(1)

        confirm_btn = page.locator('button:has-text("Conferma")').first
        confirm_btn.click()
        time.sleep(3)
        page.screenshot(path=str(cache_dir / f"worldfilia_click_pixel_{campaign_id}_saved.png"))
        click.echo("✅ Pixel ON CLICK salvato con successo!")
    finally:
        context.close()

import sys
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from worldfilia.paths import get_cache_dir
from worldfilia.browser import launch_worldfilia_browser
from meta.browser import launch_meta_browser

CAMPAIGN_ID = 5540

def execute_simulation():
    cache_dir = get_cache_dir()
    print("=" * 60)
    print("TEST COMPLETO PIXEL META: ON CLICK + ON SALE")
    print(f"Campagna: {CAMPAIGN_ID} (Rikrestin 2x49)")
    print("=" * 60)

    wf_context = launch_worldfilia_browser(headless=True)
    page = wf_context.pages[0] if wf_context.pages else wf_context.new_page()

    click_test_url = ""
    sale_test_url = ""

    try:
        url = f"https://portal.worldfilia.net/publisher/campaigns/{CAMPAIGN_ID}"
        print(f"1. Connessione a Worldfilia: {url}")
        page.goto(url, wait_until="domcontentloaded")
        time.sleep(4)

        no_thanks = page.locator("text=No thanks")
        if no_thanks.count() > 0:
            no_thanks.first.click()
            time.sleep(1)

        page.locator("text=POSTBACKS/PIXELS").first.click()
        time.sleep(2)

        # 1. Recupero Test Link ON CLICK
        print("\nRecupero link di test per ON CLICK...")
        test_btns = page.locator('button:has-text("TEST")').all()
        test_btns[0].click()
        time.sleep(2)

        link_click = page.locator('text=https://affiliatenetwork.link').first
        if link_click.count() > 0:
            click_test_url = link_click.inner_text().strip()
            print(f"-> URL ON CLICK: {click_test_url}")

        page.locator('button:has-text("ANNULLA"), button:has-text("Annulla")').first.click()
        time.sleep(1)

        # 2. Recupero Test Link ON SALE
        print("\nRecupero link di test per ON SALE...")
        test_btns = page.locator('button:has-text("TEST")').all()
        test_btns[1].click()
        time.sleep(2)

        # Compila l'input [[commission]] con 24.00 per simulare la vendita reale
        comm_input = page.locator('input[type="text"], input:not([readonly])').all()
        for inp in comm_input:
            try:
                inp.fill("24.00")
            except Exception:
                pass
        time.sleep(1)

        link_sale = page.locator('text=https://affiliatenetwork.link').first
        if link_sale.count() > 0:
            sale_test_url = link_sale.inner_text().strip()
            print(f"-> URL ON SALE con commissione 24.00: {sale_test_url}")

        page.locator('button:has-text("ANNULLA"), button:has-text("Annulla")').first.click()
        time.sleep(1)

        # 3. Esecuzione dei Test
        tests = [
            ("ON CLICK (ViewContent)", click_test_url),
            ("ON SALE (Purchase)", sale_test_url)
        ]

        for label, test_url in tests:
            if not test_url:
                print(f"[ERRORE] Nessun URL trovato per {label}")
                continue

            print(f"\n" + "-" * 50)
            print(f"LANCIO SIMULAZIONE: {label}")
            print(f"URL: {test_url}")

            test_page = wf_context.new_page()
            fb_events_fired = []

            def handle_fb(req):
                if "facebook.com/tr" in req.url:
                    fb_events_fired.append(req.url)

            test_page.on("request", handle_fb)

            test_page.goto(test_url, wait_until="networkidle")
            time.sleep(4)

            print(f"Titolo pagina: {test_page.title()}")
            test_page.screenshot(path=str(cache_dir / f"sim_{label[:7].lower().replace(' ', '_')}.png"))

            print(f"Eventi Meta Pixel intercettati ({label}): {len(fb_events_fired)}")
            for ev in fb_events_fired:
                print(f"✓ Evento inviato a Meta: {ev}")

            test_page.close()

    finally:
        wf_context.close()

    # 4. Verifica finale su Meta Events Manager
    print("\n" + "=" * 60)
    print("VERIFICA SU META EVENTS MANAGER")
    print("=" * 60)
    meta_context = launch_meta_browser(headless=True)
    meta_page = meta_context.pages[0] if meta_context.pages else meta_context.new_page()

    try:
        em_url = "https://eventsmanager.facebook.com/events_manager2/overview?act=1116925509636183"
        print(f"Navigazione a: {em_url}")
        meta_page.goto(em_url, wait_until="domcontentloaded")
        time.sleep(8)

        screenshot_path = cache_dir / "meta_events_after_test.png"
        meta_page.screenshot(path=str(screenshot_path))
        print(f"Screenshot Events Manager salvato: {screenshot_path}")

        body_text = meta_page.inner_text("body")
        for line in [x.strip() for x in body_text.splitlines() if x.strip()][:35]:
            if any(k in line.lower() for k in ["dataset", "pixel", "eventi", "viewcontent", "purchase", "ricevut", "attivo", "modlily"]):
                print("Meta:", line)

    finally:
        meta_context.close()

if __name__ == "__main__":
    execute_simulation()

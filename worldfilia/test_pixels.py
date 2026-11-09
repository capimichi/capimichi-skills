import sys
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from worldfilia.paths import get_cache_dir
from worldfilia.browser import launch_worldfilia_browser

CAMPAIGN_ID = 5540

def run_pixel_tests(headless: bool = True):
    cache_dir = get_cache_dir()
    print("=" * 60)
    print("ESECUZIONE TEST PIXEL META SU WORLDFILIA")
    print(f"Campagna: {CAMPAIGN_ID} (Rikrestin 2x49)")
    print("=" * 60)

    context = launch_worldfilia_browser(headless=headless)
    page = context.pages[0] if context.pages else context.new_page()

    try:
        url = f"https://portal.worldfilia.net/publisher/campaigns/{CAMPAIGN_ID}"
        print(f"1. Navigazione a: {url}")
        page.goto(url, wait_until="domcontentloaded")
        time.sleep(4)

        no_thanks = page.locator("text=No thanks")
        if no_thanks.count() > 0:
            no_thanks.first.click()
            time.sleep(1)

        print("2. Apertura tab POSTBACKS/PIXELS...")
        page.locator("text=POSTBACKS/PIXELS").first.click()
        time.sleep(2)

        test_buttons = page.locator('button:has-text("TEST")').all()
        print(f"Trovati {len(test_buttons)} pulsanti TEST")

        # --- TEST 1: ON CLICK ---
        print("\n--- TEST 1: ON CLICK (ViewContent) ---")
        test_buttons[0].click()
        time.sleep(2)

        # Seleziona una landing nel dropdown se vuoto
        dropdown = page.locator('div[role="combobox"], select, input[role="combobox"]').first
        if dropdown.count() > 0:
            try:
                dropdown.click()
                time.sleep(1)
                opt = page.locator('div[role="option"], li[role="option"]').first
                if opt.count() > 0:
                    opt.click()
                    time.sleep(1)
            except Exception:
                pass

        # Estrai il test link
        link_el = page.locator('text=https://affiliatenetwork.link, input[value*="http"]').first
        test_click_url = ""
        if link_el.count() > 0:
            test_click_url = link_el.input_value() if link_el.get_attribute("value") else link_el.inner_text().strip()

        print(f"URL Test ON CLICK estratto: {test_click_url}")
        page.screenshot(path=str(cache_dir / "test_onclick_modal.png"))

        # Chiudi modale
        close_btn = page.locator('button:has-text("Annulla"), div[aria-label="Chiudi"], .modal-close').first
        if close_btn.count() > 0:
            close_btn.click()
            time.sleep(1)

        # --- TEST 2: ON SALE ---
        print("\n--- TEST 2: ON SALE (Purchase) ---")
        test_buttons[1].click()
        time.sleep(2)

        # Seleziona eventuale dropdown se presente
        dropdown_sale = page.locator('div[role="combobox"], select, input[role="combobox"]').first
        if dropdown_sale.count() > 0:
            try:
                dropdown_sale.click()
                time.sleep(1)
                opt = page.locator('div[role="option"], li[role="option"]').first
                if opt.count() > 0:
                    opt.click()
                    time.sleep(1)
            except Exception:
                pass

        link_el_sale = page.locator('text=https://affiliatenetwork.link, input[value*="http"]').first
        test_sale_url = ""
        if link_el_sale.count() > 0:
            test_sale_url = link_el_sale.input_value() if link_el_sale.get_attribute("value") else link_el_sale.inner_text().strip()

        print(f"URL Test ON SALE estratto: {test_sale_url}")
        page.screenshot(path=str(cache_dir / "test_onsale_modal.png"))

        # Chiudi modale
        close_btn = page.locator('button:has-text("Annulla"), div[aria-label="Chiudi"], .modal-close').first
        if close_btn.count() > 0:
            close_btn.click()
            time.sleep(1)

        # --- ESECUZIONE SIMULAZIONE ---
        urls_to_test = [
            ("ON CLICK", test_click_url),
            ("ON SALE", test_sale_url)
        ]

        for name, test_url in urls_to_test:
            if not test_url or not test_url.startswith("http"):
                print(f"[ATTENZIONE] URL non valido per {name}: '{test_url}'")
                continue

            print(f"\nEseguo simulazione per {name}: {test_url}")
            test_page = context.new_page()

            fb_events = []
            def track_fb(req):
                if "facebook.com/tr" in req.url:
                    fb_events.append(req.url)

            test_page.on("request", track_fb)

            test_page.goto(test_url, wait_until="networkidle")
            time.sleep(4)

            print(f"Titolo pagina {name}: {test_page.title()}")
            test_page.screenshot(path=str(cache_dir / f"result_{name.lower().replace(' ', '_')}.png"))

            print(f"Eventi Meta Pixel intercettati per {name}: {len(fb_events)}")
            for ev in fb_events:
                print("-> Evento inviato a Meta:", ev[:130])

            test_page.close()

    except Exception as e:
        print(f"Errore durante i test pixel: {e}")
    finally:
        context.close()

if __name__ == "__main__":
    is_headless = "--no-headless" not in sys.argv
    run_pixel_tests(headless=is_headless)

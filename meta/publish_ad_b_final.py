import sys
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from meta.browser import launch_meta_browser

AD_ACCOUNT_ID = "1116925509636183"
CAMPAIGN_ID = "120251426951480676"
IMAGE_PATH = PROJECT_ROOT / "meta" / "assets" / "rikrestin_ad_b_graphic.jpeg"

HEADLINE = "Offerta 2x49€: Paga in Contanti al Corriere 📦 Spedizione Gratis"
DESCRIPTION = "Consegna rapida 24/48h in tutta Italia con corriere espresso"

PRIMARY_TEXT = """Noti capelli deboli, diradamento o caduta nei cambi di stagione? 🌿

Dalla ricerca erboristica avanzata nasce RiKrestin Plus: la lozione spray naturale potenziata con Serenoa Repens, Fieno Greco e Arginina, per nutrire i bulbi e donare forza e corposità al fusto.

✨ Senza siliconi, non unge, rapido assorbimento.

📦 PROMOZIONE SPECIALE (2 FLACONI A 49,99€):
✅ Nessun pagamento anticipato: paghi in contanti al corriere
✅ Spedizione rapida e gratuita in tutta Italia
📞 Come funziona: compila il modulo sul sito e riceverai una breve chiamata dal nostro staff solo per confermare l'indirizzo prima della spedizione gratuita!"""

def run():
    print("=" * 60)
    print("CARICAMENTO ASSET E PUBBLICAZIONE AD B")
    print("=" * 60)

    context = launch_meta_browser(
        headless=True,
        args=["--window-size=2000,1080"],
        viewport={"width": 2000, "height": 1080}
    )
    page = context.pages[0] if context.pages else context.new_page()

    try:
        url = f"https://adsmanager.facebook.com/adsmanager/manage/ads?act={AD_ACCOUNT_ID}&selected_campaign_ids={CAMPAIGN_ID}"
        print(f"Navigo a: {url}")
        page.goto(url, wait_until="domcontentloaded")
        time.sleep(8)
        page.keyboard.press("Escape")
        time.sleep(2)

        # 1. Clicca bozza
        target = page.locator(':text("Inserzione B - Offerta COD"), :text("Inserzione senza nome"), :text("In bozza")').first
        target.click()
        time.sleep(2)

        # 2. Clicca Modifica nella toolbar
        page.mouse.click(490, 233)
        time.sleep(6)

        # 3. Assicura il nome corretto
        name_inp = page.locator('input[placeholder*="nome della tua inserzione"]').first
        if name_inp.count() > 0:
            val = name_inp.input_value()
            if not val or "Offerta" not in val:
                name_inp.fill("Inserzione B - Offerta COD & Spedizione Gratis")
                time.sleep(1)

        # 4. Scrolla al selettore multimediale
        page.mouse.move(500, 500)
        page.mouse.wheel(0, 900)
        time.sleep(2)

        # Clicca Aggiungi contenuto multimediale
        btn = page.locator('div[role="button"]:has-text("Aggiungi contenuto multimediale")').first
        if btn.count() > 0:
            btn.scroll_into_view_if_needed()
            time.sleep(1)
            btn.click(force=True)
            time.sleep(2)

            # Clicca Aggiungi un'immagine
            add_img = page.locator(':text("Aggiungi un\'immagine")').first
            if add_img.count() > 0:
                print("Clicco Aggiungi un'immagine...")
                add_img.click()
                time.sleep(5)

        page.screenshot(path=str(PROJECT_ROOT / "meta" / "modal_image_picker.png"))
        print("Screenshot salvato in meta/modal_image_picker.png")

        # 5. Cerca file input per caricare l'immagine
        file_input = page.locator('input[type="file"]').first
        if file_input.count() > 0:
            print("Carico immagine via file_input:", IMAGE_PATH)
            file_input.set_input_files(str(IMAGE_PATH))
            time.sleep(8)

        page.screenshot(path=str(PROJECT_ROOT / "meta" / "modal_image_uploaded.png"))
        print("Screenshot salvato in meta/modal_image_uploaded.png")

        # Clicca Avanti / Continua / Fine nel dialog di ritaglio
        for s in range(6):
            avanti = page.locator('div[role="dialog"] button:has-text("Avanti"), div[role="dialog"] div[role="button"]:has-text("Avanti"), div[role="dialog"] button:has-text("Continua")').first
            fine = page.locator('div[role="dialog"] button:has-text("Fine"), div[role="dialog"] div[role="button"]:has-text("Fine"), div[role="dialog"] button:has-text("Salva")').first
            if avanti.count() > 0 and avanti.is_visible():
                print(f"Step {s}: Clicco Avanti...")
                avanti.click()
                time.sleep(3)
            elif fine.count() > 0 and fine.is_visible():
                print(f"Step {s}: Clicco Fine...")
                fine.click()
                time.sleep(4)
                break
            else:
                time.sleep(1)

        page.screenshot(path=str(PROJECT_ROOT / "meta" / "after_image_confirmed.png"))
        print("Screenshot salvato in meta/after_image_confirmed.png")

        # 6. Aggiorna Testo principale, Titolo, Descrizione
        print("Aggiorno testi...")
        page.mouse.move(500, 500)
        page.mouse.wheel(0, 400)
        time.sleep(2)

        # Testo principale
        tbs = page.locator('div[role="textbox"]').all()
        for tb in tbs:
            txt = tb.inner_text().strip()
            if "Noti capelli" in txt or "erboristica" in txt:
                print("Aggiorno Testo principale...")
                tb.click()
                page.keyboard.press("Meta+A")
                page.keyboard.press("Backspace")
                tb.fill(PRIMARY_TEXT)
                time.sleep(2)
                break

        # Titolo e Descrizione
        inputs = page.locator('input[type="text"]').all()
        for inp in inputs:
            val = inp.input_value()
            if "Rikrestin Plus" in val or "Pagamento alla Consegna" in val:
                print("Aggiorno Titolo...")
                inp.click()
                page.keyboard.press("Meta+A")
                page.keyboard.press("Backspace")
                inp.fill(HEADLINE)
                time.sleep(1)
                break

        for inp in inputs:
            val = inp.input_value()
            if "Spedizione rapida" in val:
                print("Aggiorno Descrizione...")
                inp.click()
                page.keyboard.press("Meta+A")
                page.keyboard.press("Backspace")
                inp.fill(DESCRIPTION)
                time.sleep(1)
                break

        page.screenshot(path=str(PROJECT_ROOT / "meta" / "ad_b_configured_full.png"))
        print("Screenshot salvato in meta/ad_b_configured_full.png")

        # 7. Procedi alla pubblicazione
        print("Procedo con il click di pubblicazione...")
        pub_btn = page.locator('button:has-text("pubblicare"), div[role="button"]:has-text("pubblicare"), button:has-text("Pubblica"), div[role="button"]:has-text("Pubblica")').last
        if pub_btn.count() > 0:
            print("Clicco su pulsante:", pub_btn.inner_text().strip())
            pub_btn.click()
            time.sleep(8)

        page.screenshot(path=str(PROJECT_ROOT / "meta" / "pub_step1.png"))

        # Se c'è un dialog di conferma o "Esamina le bozze"
        dialog = page.locator('div[role="dialog"]').first
        if dialog.count() > 0 and dialog.is_visible():
            print("Dialog di pubblicazione presente:", dialog.inner_text()[:100])
            # Se c'è "Prova a pubblicare elementi con errori"
            force_chk = dialog.locator('input[type="checkbox"], :has-text("Prova a pubblicare")').first
            if force_chk.count() > 0:
                print("Spunto 'Prova a pubblicare elementi con errori'...")
                force_chk.click(force=True)
                time.sleep(2)

            # Clicca il pulsante verde o blu Pubblica dentro il dialog
            confirm_pub = dialog.locator('button:has-text("Pubblica"), div[role="button"]:has-text("Pubblica")').last
            if confirm_pub.count() > 0 and confirm_pub.is_enabled():
                print("Clicco Pubblica nel dialog...")
                confirm_pub.click()
                time.sleep(15)

        page.screenshot(path=str(PROJECT_ROOT / "meta" / "final_publish_result.png"))
        print("Screenshot finale salvato in meta/final_publish_result.png")

    finally:
        context.close()

if __name__ == "__main__":
    run()

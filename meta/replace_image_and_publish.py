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
    print("SOSTITUZIONE IMMAGINE E PUBBLICAZIONE AD B")
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

        # Clicca target bozza
        target = page.locator(':text("Inserzione B - Offerta COD"), :text("Inserzione senza nome"), :text("In bozza")').first
        target.click()
        time.sleep(2)

        # Clicca Modifica nella toolbar
        page.mouse.click(490, 233)
        time.sleep(6)

        # Assicura il nome corretto
        name_inp = page.locator('input[placeholder*="nome della tua inserzione"]').first
        if name_inp.count() > 0:
            val = name_inp.input_value()
            if not val or "Offerta" not in val:
                name_inp.fill("Inserzione B - Offerta COD & Spedizione Gratis")
                time.sleep(1)

        # Scrolla giù nel pannello centrale
        page.mouse.move(500, 500)
        page.mouse.wheel(0, 700)
        time.sleep(2)

        # Cerca Aggiungi contenuto multimediale o Sostituisci o Modifica
        add_btn = page.locator('div[role="button"]:has-text("Aggiungi contenuto multimediale")').first
        if add_btn.count() > 0:
            print("Clicco su 'Aggiungi contenuto multimediale'...")
            add_btn.click()
            time.sleep(2)
            page.screenshot(path=str(PROJECT_ROOT / "meta" / "media_menu_opened.png"))

            # Sottomenu "Aggiungi immagine"
            add_img_item = page.locator('div[role="menuitem"]:has-text("immagine"), span:has-text("Aggiungi immagine")').first
            if add_img_item.count() > 0:
                print("Clicco su 'Aggiungi immagine'...")
                add_img_item.click()
                time.sleep(4)

        page.screenshot(path=str(PROJECT_ROOT / "meta" / "upload_modal_ready.png"))
        print("Screenshot salvato in meta/upload_modal_ready.png")

        # Cerca file input
        file_inputs = page.locator('input[type="file"]').all()
        print(f"File inputs trovati: {len(file_inputs)}")
        for fi in file_inputs:
            print("Carico immagine su input:", IMAGE_PATH)
            fi.set_input_files(str(IMAGE_PATH))
            time.sleep(8)
            break

        page.screenshot(path=str(PROJECT_ROOT / "meta" / "after_file_set.png"))
        print("Screenshot salvato in meta/after_file_set.png")

        # Gestisci i pulsanti Avanti / Fine / Salva del modal
        for step in range(5):
            avanti = page.locator('div[role="dialog"] button:has-text("Avanti"), div[role="dialog"] div[role="button"]:has-text("Avanti"), div[role="dialog"] button:has-text("Continua")').first
            fine = page.locator('div[role="dialog"] button:has-text("Fine"), div[role="dialog"] div[role="button"]:has-text("Fine"), div[role="dialog"] button:has-text("Salva")').first
            if avanti.count() > 0 and avanti.is_visible():
                print(f"[{step}] Clicco Avanti...")
                avanti.click()
                time.sleep(3)
            elif fine.count() > 0 and fine.is_visible():
                print(f"[{step}] Clicco Fine...")
                fine.click()
                time.sleep(4)
                break
            else:
                time.sleep(1)

        page.screenshot(path=str(PROJECT_ROOT / "meta" / "media_uploaded_and_confirmed.png"))
        print("Screenshot salvato in meta/media_uploaded_and_confirmed.png")

        # Ora aggiorniamo Testo principale, Titolo, Descrizione
        print("Aggiorno Testo principale, Titolo e Descrizione...")
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

        # Titolo
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

        # Descrizione
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

        page.screenshot(path=str(PROJECT_ROOT / "meta" / "ad_b_ready_for_publish.png"))
        print("Screenshot salvato in meta/ad_b_ready_for_publish.png")

        # Clicca "Visualizza l'anteprima per pubblicare" o "Pubblica"
        print("Procedo alla pubblicazione...")
        pub_btn = page.locator('button:has-text("pubblicare"), div[role="button"]:has-text("pubblicare"), button:has-text("Pubblica"), div[role="button"]:has-text("Pubblica")').last
        if pub_btn.count() > 0:
            print("Clicco pulsante di pubblicazione:", pub_btn.inner_text().strip())
            pub_btn.click()
            time.sleep(10)

            # Se si apre un modal di conferma pubblicazione
            confirm_pub = page.locator('div[role="dialog"] button:has-text("Pubblica"), div[role="dialog"] div[role="button"]:has-text("Pubblica")').last
            if confirm_pub.count() > 0 and confirm_pub.is_visible():
                print("Confermo pubblicazione nel dialog...")
                confirm_pub.click()
                time.sleep(15)

        page.screenshot(path=str(PROJECT_ROOT / "meta" / "published_result_final.png"))
        print("Screenshot finale salvato in meta/published_result_final.png")

    finally:
        context.close()

if __name__ == "__main__":
    run()

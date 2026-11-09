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

AD_NAME = "Inserzione B - Offerta COD & Spedizione Gratis"
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
    print("DUPLICAZIONE E SETUP INSERZIONE B")
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
        time.sleep(6)
        page.keyboard.press("Escape")
        time.sleep(1)

        # 1. Seleziona la riga dell'inserzione attiva
        boxes = page.locator('input[type="checkbox"]').all()
        print(f"Checkbox trovate: {len(boxes)}")
        if len(boxes) > 1:
            print("Seleziono riga inserzione...")
            boxes[1].click(force=True)
            time.sleep(1)

        # 2. Clicca su Duplica
        dup_btn = page.locator('button:has-text("Duplica"), div[role="button"]:has-text("Duplica")').first
        if dup_btn.count() > 0:
            print("Clicco su Duplica...")
            dup_btn.click()
            time.sleep(3)
            page.screenshot(path=str(PROJECT_ROOT / "meta" / "step1_duplicate_modal.png"))

            # Conferma duplicazione nel dialog
            confirm_dup = page.locator('button:has-text("Duplica")').last
            if confirm_dup.count() > 0:
                print("Confermo duplicazione...")
                confirm_dup.click()
                time.sleep(8)

        page.screenshot(path=str(PROJECT_ROOT / "meta" / "step2_editor_duplicated.png"))
        print("Editor inserzione duplicata aperto")

        # 3. Aggiorna il Nome dell'inserzione
        name_input = page.locator('input[placeholder*="Nome"], input[value*="Copia"], input[value*="Nuova inserzione"]').first
        if name_input.count() > 0:
            print("Aggiorno nome inserzione...")
            name_input.click()
            page.keyboard.press("Meta+A")
            page.keyboard.press("Backspace")
            name_input.fill(AD_NAME)
            time.sleep(1)

        # 4. Sostituisci Immagine
        print("Cerco pulsante per sostituire immagine...")
        # Cerca 'Modifica elemento multimediale' o 'Sostituisci' o 'Aggiungi elementi multimediali'
        edit_media_btn = page.locator('button:has-text("Modifica elemento multimediale"), div[role="button"]:has-text("Modifica elemento multimediale"), button:has-text("Modifica gruppo"), button:has-text("Sostituisci")').first
        if edit_media_btn.count() > 0:
            print("Clicco Modifica elemento multimediale...")
            edit_media_btn.click()
            time.sleep(2)
            replace_opt = page.locator('text="Sostituisci elemento multimediale", text="Sostituisci", div[role="menuitem"]:has-text("Sostituisci")').first
            if replace_opt.count() > 0:
                replace_opt.click()
                time.sleep(3)
        else:
            # In alternativa, cerca cestino per eliminare l'elemento o pulsante Modifica
            clear_btn = page.locator('button[aria-label*="Elimina elemento multimediale"], button:has-text("Elimina tutto")').first
            if clear_btn.count() > 0:
                clear_btn.click()
                time.sleep(2)

        page.screenshot(path=str(PROJECT_ROOT / "meta" / "step3_media_replace.png"))

        # Carica il nuovo file rikrestin_ad_b_graphic.jpeg
        file_input = page.locator('input[type="file"]').first
        if file_input.count() > 0:
            print("Carico nuova immagine via file input...")
            file_input.set_input_files(str(IMAGE_PATH))
            time.sleep(6)
            # Clicca Avanti/Fine
            avanti = page.locator('button:has-text("Avanti"), button:has-text("Continua")').first
            if avanti.count() > 0:
                avanti.click()
                time.sleep(2)
            fine = page.locator('button:has-text("Fine"), button:has-text("Salva")').first
            if fine.count() > 0:
                fine.click()
                time.sleep(3)

        page.screenshot(path=str(PROJECT_ROOT / "meta" / "step4_media_loaded.png"))

        # 5. Aggiorna Testo Principale
        print("Aggiorno Testo Principale...")
        textboxes = page.locator('div[role="textbox"], textarea').all()
        for tb in textboxes:
            p = (tb.get_attribute("placeholder") or "").lower()
            a = (tb.get_attribute("aria-label") or "").lower()
            if "testo" in p or "testo" in a or "principale" in a:
                tb.click()
                page.keyboard.press("Meta+A")
                page.keyboard.press("Backspace")
                tb.fill(PRIMARY_TEXT)
                print("Testo principale aggiornato!")
                time.sleep(2)
                break

        # 6. Aggiorna Titolo (Headline)
        print("Aggiorno Titolo...")
        inputs = page.locator('input[type="text"]').all()
        for inp in inputs:
            p = (inp.get_attribute("placeholder") or "").lower()
            a = (inp.get_attribute("aria-label") or "").lower()
            if "titolo" in p or "titolo" in a:
                inp.click()
                page.keyboard.press("Meta+A")
                page.keyboard.press("Backspace")
                inp.fill(HEADLINE)
                print("Titolo aggiornato!")
                time.sleep(1)
                break

        # 7. Aggiorna Descrizione
        print("Aggiorno Descrizione...")
        for inp in inputs:
            p = (inp.get_attribute("placeholder") or "").lower()
            a = (inp.get_attribute("aria-label") or "").lower()
            if "descrizione" in p or "descrizione" in a:
                inp.click()
                page.keyboard.press("Meta+A")
                page.keyboard.press("Backspace")
                inp.fill(DESCRIPTION)
                print("Descrizione aggiornata!")
                time.sleep(1)
                break

        page.screenshot(path=str(PROJECT_ROOT / "meta" / "step5_ready_to_publish.png"))

        # 8. Clicca Pubblica
        print("Clicco su Pubblica...")
        pub_btn = page.locator('button:has-text("Pubblica")').filter(has_text="Pubblica").last
        if pub_btn.count() > 0:
            pub_btn.click()
            print("Pubblicazione avviata, attendo 15s...")
            time.sleep(15)

        page.screenshot(path=str(PROJECT_ROOT / "meta" / "step6_published_result.png"))
        print("Fatto! Screenshot finale salvato in meta/step6_published_result.png")

    finally:
        context.close()

if __name__ == "__main__":
    run()

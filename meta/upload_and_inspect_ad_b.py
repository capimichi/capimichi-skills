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
    print("CARICAMENTO IMMAGINE E MODIFICA TESTI INSERZIONE B")
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

        # 1. Seleziona bozza
        copia_target = page.locator(':text("Nuova inserzione Vendite - Copia")').first
        if copia_target.count() > 0:
            copia_target.click()
            time.sleep(2)

        # 2. Clicca Modifica nella toolbar
        mod_candidates = page.locator(':text("Modifica")').all()
        for idx, m in enumerate(mod_candidates):
            if m.is_visible():
                box = m.bounding_box()
                if box and box['y'] > 180 and box['y'] < 400 and box['width'] > 20:
                    print(f"Clicco Modifica toolbar a ({box['x'] + box['width']/2}, {box['y'] + box['height']/2})")
                    page.mouse.click(box['x'] + box['width']/2, box['y'] + box['height']/2)
                    time.sleep(6)
                    break

        page.screenshot(path=str(PROJECT_ROOT / "meta" / "step1_editor_ready.png"))
        print("Editor aperto, screenshot salvato in meta/step1_editor_ready.png")

        # 3. Rinomina
        print("Rinomino inserzione...")
        name_input = page.locator('input[value*="Copia"], input[value*="Nuova inserzione"]').first
        if name_input.count() > 0:
            name_input.click()
            page.keyboard.press("Meta+A")
            page.keyboard.press("Backspace")
            name_input.fill(AD_NAME)
            time.sleep(1)

        # 4. Clicca Seleziona immagine
        sel_img_btn = page.locator('button:has-text("Seleziona immagine"), div[role="button"]:has-text("Seleziona immagine")').first
        if sel_img_btn.count() > 0 and sel_img_btn.is_visible():
            print("Clicco Seleziona immagine nel pannello errori...")
            sel_img_btn.click()
            time.sleep(4)
        else:
            # Scrolla il pannello centrale per trovare Aggiungi contenuto multimediale
            print("Cerco pulsante multimediale con scroll...")
            page.mouse.move(500, 500)
            page.mouse.wheel(0, 600)
            time.sleep(2)
            btn = page.locator('div[role="button"]:has-text("Aggiungi contenuto multimediale")').first
            if btn.count() > 0:
                btn.click()
                time.sleep(2)
                page.locator('text="Aggiungi immagine"').first.click()
                time.sleep(4)

        page.screenshot(path=str(PROJECT_ROOT / "meta" / "step2_image_modal.png"))
        print("Screenshot salvato in meta/step2_image_modal.png")

        # 5. Cerca file input per caricamento
        file_inputs = page.locator('input[type="file"]').all()
        print(f"File inputs trovati: {len(file_inputs)}")
        for fi in file_inputs:
            try:
                print("Carico immagine via set_input_files...")
                fi.set_input_files(str(IMAGE_PATH))
                time.sleep(8)
                break
            except Exception as e:
                print("Errore set_input_files:", e)

        page.screenshot(path=str(PROJECT_ROOT / "meta" / "step3_image_uploaded.png"))
        print("Screenshot salvato in meta/step3_image_uploaded.png")

        # 6. Gestisci i pulsanti del modal immagine (Avanti, Salva, Fine, Continua)
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

        page.screenshot(path=str(PROJECT_ROOT / "meta" / "step4_media_confirmed.png"))
        print("Screenshot salvato in meta/step4_media_confirmed.png")

    finally:
        context.close()

if __name__ == "__main__":
    run()

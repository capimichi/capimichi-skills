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
    print("APERTURA E CONFIGURAZIONE INSERZIONE B")
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

        # Clicca sul testo del nome dell'inserzione in bozza
        cell = page.locator('text="Nuova inserzione Vendite - Copia"').first
        if cell.count() > 0:
            print("Clicco su 'Nuova inserzione Vendite - Copia'...")
            cell.click()
            time.sleep(6)
        else:
            print("Cella non trovata col testo esatto, cerco con :has-text('Copia')...")
            cell2 = page.locator(':has-text("Copia")').first
            cell2.click()
            time.sleep(6)

        page.screenshot(path=str(PROJECT_ROOT / "meta" / "ad_b_editor_step1.png"))
        print("Screenshot salvato in meta/ad_b_editor_step1.png")

        # 1. Rinomina inserzione
        print("1. Modifica nome inserzione...")
        name_input = page.locator('input[placeholder*="Nome"], input[value*="Copia"], input[value*="Nuova inserzione"]').first
        if name_input.count() > 0:
            name_input.click()
            page.keyboard.press("Meta+A")
            page.keyboard.press("Backspace")
            name_input.fill(AD_NAME)
            time.sleep(1)
            print(f"Nome aggiornato a: '{AD_NAME}'")

        # 2. Cerca pulsanti multimediali
        print("2. Ispezione opzioni multimediali...")
        media_buttons = page.locator('button:has-text("Modifica"), div[role="button"]:has-text("Modifica"), button:has-text("Sostituisci"), div[role="button"]:has-text("Sostituisci")').all()
        for b in media_buttons:
            t = b.inner_text().strip()
            if any(k in t.lower() for k in ["elemento", "multimediale", "gruppo", "immagine", "sostituisci"]):
                print(f"Pulsante multimediale trovato: '{t}' -> clicco...")
                b.click()
                time.sleep(2)
                break

        page.screenshot(path=str(PROJECT_ROOT / "meta" / "ad_b_editor_step2_media.png"))

        # Cerca file input
        file_input = page.locator('input[type="file"]').first
        if file_input.count() > 0:
            print("Carico nuova immagine:", IMAGE_PATH)
            file_input.set_input_files(str(IMAGE_PATH))
            time.sleep(6)
            avanti = page.locator('button:has-text("Avanti"), div[role="button"]:has-text("Avanti"), button:has-text("Continua")').first
            if avanti.count() > 0:
                avanti.click()
                time.sleep(2)
            fine = page.locator('button:has-text("Fine"), div[role="button"]:has-text("Fine"), button:has-text("Salva")').first
            if fine.count() > 0:
                fine.click()
                time.sleep(3)

        # 3. Testo principale
        print("3. Testo principale...")
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

        # 4. Titolo (Headline)
        print("4. Titolo...")
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

        # 5. Descrizione
        print("5. Descrizione...")
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

        page.screenshot(path=str(PROJECT_ROOT / "meta" / "ad_b_editor_step3_filled.png"))

        # 6. Pubblica
        print("6. Clicco su Pubblica...")
        pub_btn = page.locator('button:has-text("Pubblica"), div[role="button"]:has-text("Pubblica")').last
        if pub_btn.count() > 0:
            print("Pubblica trovato:", pub_btn.inner_text().strip())
            pub_btn.click()
            time.sleep(15)

        page.screenshot(path=str(PROJECT_ROOT / "meta" / "ad_b_published_final.png"))
        print("Screenshot finale salvato in meta/ad_b_published_final.png")

    finally:
        context.close()

if __name__ == "__main__":
    run()

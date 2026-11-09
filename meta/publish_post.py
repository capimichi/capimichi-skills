import sys
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from meta.paths import get_cache_dir
from meta.browser import launch_meta_browser

ASSET_ID = "918101574729792"
IMAGE_PATH = PROJECT_ROOT / "meta" / "assets" / "rikrestin_hero.jpeg"
COMPOSER_URL = f"https://business.facebook.com/latest/composer?asset_id={ASSET_ID}"

POST_TEXT = """Noti capelli deboli, diradamento o caduta nei cambi di stagione? 🌿

Spesso la causa principale è l’assopimento dei follicoli piliferi dovuto a stress e microcircolo rallentato.

Dalla ricerca erboristica avanzata nasce RiKrestin Plus: la lozione spray naturale potenziata con:
🌱 Serenoa Repens: contrasta l'indebolimento alla radice
🌿 Fieno Greco: stimola e nutre i bulbi silenti
💧 Arginina & Pantenolo: donano forza, corposità e spessore al fusto

✨ Senza siliconi, non unge, rapido assorbimento.

📦 Offerta Speciale per la Community:
2 Confezioni a soli 49,99€ con:
✅ Pagamento in contanti alla consegna (COD)
✅ Spedizione rapida e gratuita in tutta Italia

👉 Scopri di più e ordina in 30 secondi:
https://backend.worldfilia.net/landing/ntm/rikrestin_2x49/1?ref=e75d64c2cffa
"""

def publish_post(headless: bool = False):
    print("=" * 60)
    print("PUBBLICAZIONE POST SU 'NATURALE E SOSTENIBILE'")
    print(f"Immagine: {IMAGE_PATH}")
    print("=" * 60)

    context = launch_meta_browser(headless=headless)
    page = context.pages[0] if context.pages else context.new_page()

    try:
        print(f"1. Navigazione al Composer di Meta Business Suite: {COMPOSER_URL}")
        page.goto(COMPOSER_URL, wait_until="domcontentloaded")
        print("Attendo caricamento del Composer...")
        time.sleep(6)

        # Se c'è un dialog/tutorial di benvenuto, chiudilo
        close_dialog = page.locator('div[aria-label="Chiudi"], button:has-text("Chiudi"), button:has-text("Avanti")')
        if close_dialog.count() > 0:
            try:
                close_dialog.first.click()
                time.sleep(1)
            except Exception:
                pass

        # 2. Caricamento Immagine
        print("2. Caricamento immagine...")
        file_input = page.locator('input[type="file"]')
        if file_input.count() > 0:
            file_input.first.set_input_files(str(IMAGE_PATH))
            print("File inviato al selettore file!")
        else:
            # Prova a cercare il pulsante 'Aggiungi foto'
            add_photo = page.locator('text=Aggiungi foto').first
            if add_photo.count() > 0:
                with page.expect_file_chooser() as fc_info:
                    add_photo.click()
                file_chooser = fc_info.value
                file_chooser.set_files(str(IMAGE_PATH))
                print("Foto caricata tramite file chooser!")

        print("Attendo rendering dell'anteprima dell'immagine...")
        time.sleep(5)

        # 3. Inserimento Testo
        print("3. Inserimento testo del post...")
        # Il box di testo in Meta Business Suite è tipicamente un div[role="textbox"] o contenteditable
        textbox = page.locator('div[role="textbox"], div[contenteditable="true"]').first
        if textbox.count() > 0:
            textbox.click()
            time.sleep(1)
            # Usa paste / fill o insert_text
            page.keyboard.insert_text(POST_TEXT.strip())
            print("Testo inserito con successo!")
        else:
            print("Cerco textarea alternativa...")
            textarea = page.locator('textarea').first
            if textarea.count() > 0:
                textarea.fill(POST_TEXT.strip())

        print("Attendo elaborazione dell'anteprima...")
        time.sleep(4)

        screenshot_path = get_cache_dir() / "post_preview.png"
        page.screenshot(path=str(screenshot_path))
        print(f"Screenshot anteprima salvato in: {screenshot_path}")

        print("\n" + "=" * 60)
        print("POST PRONTO E VISIBILE NELLA FINESTRA DEL BROWSER!")
        print("Puoi verificare l'anteprima e premere 'Pubblica' direttamente nella finestra,")
        print("oppure premere [INVIO] nel terminale quando sei pronto.")
        print("=" * 60)

        # Manteniamo la finestra aperta finché l'utente non interagisce
        while True:
            time.sleep(2)
            if not context.pages or all(p.is_closed() for p in context.pages):
                break

    except Exception as e:
        print(f"Errore durante la pubblicazione: {e}")
    finally:
        try:
            context.close()
        except Exception:
            pass
        print("Browser chiuso.")

if __name__ == "__main__":
    is_headless = "--headless" in sys.argv
    publish_post(headless=is_headless)

import sys
import time
import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from meta.browser import launch_meta_browser

AD_ACCOUNT_ID = "1116925509636183"
CAMPAIGN_ID = "120251426951480676"

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
    print("AVVIO SELEZIONE E PUBBLICAZIONE AD B")
    print("=" * 60)

    context = launch_meta_browser(headless=True, args=["--window-size=2000,1080"], viewport={"width": 2000, "height": 1080})
    page = context.pages[0] if context.pages else context.new_page()

    try:
        page.goto(f"https://adsmanager.facebook.com/adsmanager/manage/ads?act={AD_ACCOUNT_ID}&selected_campaign_ids={CAMPAIGN_ID}", wait_until="domcontentloaded")
        time.sleep(8)
        page.keyboard.press("Escape")
        time.sleep(1)

        # Tab Inserzioni
        page.locator('[role="tab"]:has-text("Inserz")').last.click()
        time.sleep(3)

        # Seleziona bozza
        page.locator(':text("Inserzione B - Offerta COD"), :text("Inserzione senza nome"), :text("In bozza")').first.click()
        time.sleep(2)

        # Modifica toolbar
        page.locator('div[role="toolbar"] button:has-text("Modifica"), div[role="toolbar"] div[role="button"]:has-text("Modifica")').first.click()
        time.sleep(6)

        # Scroll al blocco media
        page.evaluate("""() => {
            const container = Array.from(document.querySelectorAll('div')).find(el => el.scrollHeight > 3000 && el.clientHeight < 1000);
            if (container) container.scrollTop = 1500;
        }""")
        time.sleep(2)

        # Aggiungi contenuto multimediale
        add_btn = page.locator('div[role="button"]:has-text("Aggiungi contenuto multimediale"), button:has-text("Aggiungi contenuto multimediale")').first
        add_btn.click()
        time.sleep(2)

        # Clicca Aggiungi immagine dal menu a discesa
        menu_items = page.locator('div[role="menuitem"], div[role="button"]').all()
        for item in menu_items:
            t = item.inner_text().lower()
            if "immagine" in t and "video" not in t:
                print("Clicco voce menu:", item.inner_text())
                item.click()
                break
        time.sleep(5)

        # Trova la card con rikrestin_ad_b_graphic nel modal
        print("Cerco e clicco la card di rikrestin_ad...")
        click_success = page.evaluate("""() => {
            // Cerchiamo l'elemento che contiene 'rikrestin' o '1080 x 1080' sotto Immagini dell'account
            const dialogs = document.querySelectorAll('div[role="dialog"]');
            const dialog = dialogs[dialogs.length - 1];
            if (!dialog) return false;

            const matches = Array.from(dialog.querySelectorAll('*')).filter(el => 
                el.innerText && el.innerText.includes('rikrestin')
            );
            
            for (let el of matches) {
                // Troviamo il container cliccabile o l'immagine stessa
                const card = el.closest('div[role="button"], div[tabindex="0"], div[role="checkbox"]') || el;
                card.click();
                return { found: true, text: el.innerText };
            }
            return false;
        }""")
        print("Click result JS:", click_success)
        time.sleep(2)

        page.screenshot(path="meta/modal_after_card_click.png")

        # Se ancora non è selezionata, proviamo a cliccare per coordinate sulla prima card
        # Nella screenshot inspect_media_modal.png, la prima card è a x=150, y=340
        avanti_check = page.evaluate("""() => {
            const dialogs = document.querySelectorAll('div[role="dialog"]');
            const dialog = dialogs[dialogs.length - 1];
            const avanti = Array.from(dialog.querySelectorAll('button, div[role="button"]')).find(b => b.innerText && b.innerText.includes('Avanti'));
            return avanti ? avanti.getAttribute('aria-disabled') : 'not found';
        }""")
        print("Avanti aria-disabled:", avanti_check)

        if avanti_check == 'true':
            print("Tentativo click diretto su coordinate (150, 340)...")
            page.mouse.click(150, 340)
            time.sleep(2)
            page.screenshot(path="meta/modal_after_coords_click.png")

        # Clicca Avanti
        print("Clicco Avanti...")
        page.evaluate("""() => {
            const dialogs = document.querySelectorAll('div[role="dialog"]');
            const dialog = dialogs[dialogs.length - 1];
            const avanti = Array.from(dialog.querySelectorAll('button, div[role="button"]')).find(b => b.innerText && b.innerText.includes('Avanti'));
            if (avanti) avanti.click();
        }""")
        time.sleep(4)

        # Gestione wizard (Ritaglia -> Testo -> Generazione -> Miglioramenti -> Traduzione -> Fine)
        print("Avanzo nel wizard...")
        for step in range(8):
            page.screenshot(path=f"meta/wizard_progression_{step}.png")
            done = page.evaluate("""() => {
                const dialogs = document.querySelectorAll('div[role="dialog"]');
                const dialog = dialogs[dialogs.length - 1];
                if (!dialog) return 'no_dialog';

                const fine = Array.from(dialog.querySelectorAll('button, div[role="button"]')).find(b => 
                    b.innerText && (b.innerText.trim() === 'Fine' || b.innerText.trim() === 'Salva') && b.getAttribute('aria-disabled') !== 'true'
                );
                if (fine) {
                    fine.click();
                    return 'clicked_fine';
                }

                const avanti = Array.from(dialog.querySelectorAll('button, div[role="button"]')).find(b => 
                    b.innerText && (b.innerText.trim() === 'Avanti' || b.innerText.trim() === 'Continua') && b.getAttribute('aria-disabled') !== 'true'
                );
                if (avanti) {
                    avanti.click();
                    return 'clicked_avanti';
                }

                return 'waiting';
            }""")
            print(f"Wizard step {step}: {done}")
            if done == 'clicked_fine':
                time.sleep(5)
                break
            time.sleep(3)

        page.screenshot(path="meta/after_wizard_finished.png")
        print("Wizard terminato. Screenshot salvato in meta/after_wizard_finished.png")

        # Aggiornamento testi
        print("Scroll al blocco testi...")
        page.evaluate("""() => {
            const container = Array.from(document.querySelectorAll('div')).find(el => el.scrollHeight > 3000 && el.clientHeight < 1000);
            if (container) container.scrollTop = 2200;
        }""")
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

        page.screenshot(path="meta/ad_b_ready_to_publish.png")

        # Pubblica
        print("Clicco Pubblica...")
        pub_btn = page.locator('button:has-text("pubblicare"), div[role="button"]:has-text("pubblicare"), button:has-text("Pubblica"), div[role="button"]:has-text("Pubblica")').last
        if pub_btn.count() > 0:
            print("Pulsante:", pub_btn.inner_text().strip())
            pub_btn.click()
            time.sleep(8)

        # Gestione modal revisione / WhatsApp glitch
        dialog = page.locator('div[role="dialog"]').first
        if dialog.count() > 0 and dialog.is_visible():
            print("Modal revisione rilevato.")
            force_box = dialog.locator('input[type="checkbox"], :has-text("Prova a pubblicare")').first
            if force_box.count() > 0:
                print("Spunto Prova a pubblicare elementi con errori...")
                force_box.click(force=True)
                time.sleep(2)

            confirm_pub = dialog.locator('button:has-text("Pubblica"), div[role="button"]:has-text("Pubblica")').last
            if confirm_pub.count() > 0:
                print("Confermo Pubblica...")
                confirm_pub.click()
                time.sleep(15)

        page.screenshot(path="meta/final_published_state.png")
        print("OPERAZIONE COMPLETATA! Screenshot in meta/final_published_state.png")

    finally:
        context.close()

if __name__ == "__main__":
    run()

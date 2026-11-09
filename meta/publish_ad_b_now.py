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
    print("PUBBLICAZIONE DEFINITIVA INSERZIONE B")
    print("=" * 60)

    context = launch_meta_browser(
        headless=True,
        args=["--window-size=2000,1080"],
        viewport={"width": 2000, "height": 1080}
    )
    page = context.pages[0] if context.pages else context.new_page()

    try:
        url = f"https://adsmanager.facebook.com/adsmanager/manage/ads?act={AD_ACCOUNT_ID}&selected_campaign_ids={CAMPAIGN_ID}"
        print(f"1. Navigo a: {url}")
        page.goto(url, wait_until="domcontentloaded")
        time.sleep(8)
        page.keyboard.press("Escape")
        time.sleep(2)

        # Tab Inserzioni
        ads_tab = page.locator('[role="tab"]:has-text("Inserz")').last
        if ads_tab.count() > 0:
            print("2. Clicco tab Inserzioni...")
            ads_tab.click()
            time.sleep(3)

        # Seleziona bozza
        target = page.locator(':text("Inserzione B - Offerta COD"), :text("Inserzione senza nome"), :text("In bozza")').first
        print("3. Clicco bozza nella tabella...")
        target.click()
        time.sleep(2)

        # Modifica nella toolbar
        mod_btn = page.locator('div[role="toolbar"] button:has-text("Modifica"), div[role="toolbar"] div[role="button"]:has-text("Modifica")').first
        print("4. Clicco Modifica toolbar...")
        mod_btn.click()
        time.sleep(6)

        # Nome
        name_inp = page.locator('input[placeholder*="nome della tua inserzione"]').first
        if name_inp.count() > 0:
            print("5. Imposto nome inserzione...")
            name_inp.fill(AD_NAME)
            time.sleep(1)

        # Scroll al blocco multimediale
        print("6. Scroll al blocco multimediale...")
        page.evaluate("""() => {
            const container = Array.from(document.querySelectorAll('div')).find(el => el.scrollHeight > 3000 && el.clientHeight < 1000);
            if (container) container.scrollTop = 1500;
        }""")
        time.sleep(2)

        page.screenshot(path=str(PROJECT_ROOT / "meta" / "final_step6_media_view.png"))

        # Clicca Aggiungi contenuto multimediale
        add_btn = page.locator('div[role="button"]:has-text("Aggiungi contenuto multimediale"), button:has-text("Aggiungi contenuto multimediale")').first
        if add_btn.count() > 0 and add_btn.is_visible():
            print("7. Clicco 'Aggiungi contenuto multimediale'...")
            add_btn.click()
            time.sleep(2)

            add_img = page.locator(':text("Aggiungi un\'immagine"), :text("Aggiungi immagine")').first
            if add_img.count() > 0:
                print("8. Clicco 'Aggiungi un'immagine'...")
                add_img.click()
                time.sleep(5)

                # Caricamento file immagine
                fi = page.locator('input[type="file"]').first
                if fi.count() > 0:
                    print(f"9. Carico file immagine: {IMAGE_PATH}")
                    fi.set_input_files(str(IMAGE_PATH))
                    time.sleep(8)

                # Gestione wizard ritaglio
                print("10. Avanzo nel wizard immagine...")
                for s in range(6):
                    avanti = page.locator('div[role="dialog"] button:has-text("Avanti"), div[role="dialog"] div[role="button"]:has-text("Avanti"), div[role="dialog"] button:has-text("Continua")').first
                    fine = page.locator('div[role="dialog"] button:has-text("Fine"), div[role="dialog"] div[role="button"]:has-text("Fine"), div[role="dialog"] button:has-text("Salva")').first
                    if avanti.count() > 0 and avanti.is_visible():
                        print(f"    Passo {s}: Clicco Avanti...")
                        avanti.click()
                        time.sleep(3)
                    elif fine.count() > 0 and fine.is_visible():
                        print(f"    Passo {s}: Clicco Fine...")
                        fine.click()
                        time.sleep(4)
                        break
                    else:
                        time.sleep(1)

        page.screenshot(path=str(PROJECT_ROOT / "meta" / "final_step10_media_done.png"))

        # Scroll ai testi
        print("11. Scroll al blocco testi...")
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
                print("12. Aggiorno Testo principale...")
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
                print("13. Aggiorno Titolo...")
                inp.click()
                page.keyboard.press("Meta+A")
                page.keyboard.press("Backspace")
                inp.fill(HEADLINE)
                time.sleep(1)
                break

        for inp in inputs:
            val = inp.input_value()
            if "Spedizione rapida" in val:
                print("14. Aggiorno Descrizione...")
                inp.click()
                page.keyboard.press("Meta+A")
                page.keyboard.press("Backspace")
                inp.fill(DESCRIPTION)
                time.sleep(1)
                break

        page.screenshot(path=str(PROJECT_ROOT / "meta" / "final_step14_texts_done.png"))

        # 15. Pubblica
        print("15. Clicco pulsante di pubblicazione...")
        pub_btn = page.locator('button:has-text("pubblicare"), div[role="button"]:has-text("pubblicare"), button:has-text("Pubblica"), div[role="button"]:has-text("Pubblica")').last
        if pub_btn.count() > 0:
            print("Pulsante trovato:", pub_btn.inner_text().strip())
            pub_btn.click()
            time.sleep(8)

        # Gestione modal 'Esamina le bozze' se presente
        dialog = page.locator('div[role="dialog"]').first
        if dialog.count() > 0 and dialog.is_visible():
            print("16. Modal di revisione presente. Testo:", dialog.inner_text()[:120].replace('\n', ' '))
            force_box = dialog.locator('input[type="checkbox"], :has-text("Prova a pubblicare")').first
            if force_box.count() > 0:
                print("    Spunto 'Prova a pubblicare elementi con errori'...")
                force_box.click(force=True)
                time.sleep(2)

            confirm_pub = dialog.locator('button:has-text("Pubblica"), div[role="button"]:has-text("Pubblica")').last
            if confirm_pub.count() > 0:
                print("    Clicco Pubblica definitivo...")
                confirm_pub.click()
                time.sleep(15)

        page.screenshot(path=str(PROJECT_ROOT / "meta" / "final_ad_b_published.png"))
        print("Screenshot finale salvato in meta/final_ad_b_published.png")

    finally:
        context.close()

if __name__ == "__main__":
    run()

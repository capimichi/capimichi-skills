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
    print("PIPELINE COMPLETA: ASSET UPLOAD, COPY E PUBBLICAZIONE AD B")
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

        # 1. Assicura tab Inserzioni
        ads_tab = page.locator('[role="tab"]:has-text("Inserz")').last
        if ads_tab.count() > 0:
            print("Clicco tab Inserzioni...")
            ads_tab.click()
            time.sleep(3)

        # 2. Clicca sul testo del nome della bozza per selezionarla
        draft_link = page.locator(':text("Inserzione B - Offerta COD"), :text("Inserzione senza nome"), :text("In bozza")').first
        print("Clicco su riga bozza...")
        draft_link.click()
        time.sleep(2)

        # 3. Clicca Modifica nella toolbar
        mod_btn = page.locator('div[role="toolbar"] button:has-text("Modifica"), div[role="toolbar"] div[role="button"]:has-text("Modifica")').first
        print("Clicco Modifica toolbar...")
        mod_btn.click()
        time.sleep(6)

        page.screenshot(path=str(PROJECT_ROOT / "meta" / "p1_editor_opened.png"))
        print("Editor aperto, screenshot in meta/p1_editor_opened.png")

        # 4. Rinomina
        name_inp = page.locator('input[placeholder*="nome della tua inserzione"]').first
        if name_inp.count() > 0:
            name_inp.fill(AD_NAME)
            time.sleep(1)

        # 5. Cerca pulsanti multimediali
        # Scrolla il pannello centrale
        page.mouse.move(500, 500)
        page.mouse.wheel(0, 500)
        time.sleep(2)

        add_media = page.locator('div[role="button"]:has-text("Aggiungi contenuto multimediale"), button:has-text("Aggiungi contenuto multimediale")').first
        if add_media.count() > 0:
            print("Trovato pulsante Aggiungi contenuto multimediale! Clicco...")
            add_media.click(force=True)
            time.sleep(2)

            add_img_item = page.locator('div[role="menuitem"]:has-text("immagine"), span:has-text("Aggiungi immagine"), :text("Aggiungi un\'immagine")').first
            if add_img_item.count() > 0:
                print("Clicco su Aggiungi un'immagine...")
                add_img_item.click()
                time.sleep(5)

                # Carica immagine
                fi = page.locator('input[type="file"]').first
                if fi.count() > 0:
                    print("Carico file immagine:", IMAGE_PATH)
                    fi.set_input_files(str(IMAGE_PATH))
                    time.sleep(8)

                # Clicca Avanti / Fine nel wizard
                for s in range(6):
                    avanti = page.locator('div[role="dialog"] button:has-text("Avanti"), div[role="dialog"] div[role="button"]:has-text("Avanti"), div[role="dialog"] button:has-text("Continua")').first
                    fine = page.locator('div[role="dialog"] button:has-text("Fine"), div[role="dialog"] div[role="button"]:has-text("Fine"), div[role="dialog"] button:has-text("Salva")').first
                    if avanti.count() > 0 and avanti.is_visible():
                        print(f"Wizard {s}: Avanti...")
                        avanti.click()
                        time.sleep(3)
                    elif fine.count() > 0 and fine.is_visible():
                        print(f"Wizard {s}: Fine...")
                        fine.click()
                        time.sleep(4)
                        break
                    else:
                        time.sleep(1)

        page.screenshot(path=str(PROJECT_ROOT / "meta" / "p2_after_media.png"))
        print("Media configurato, screenshot in meta/p2_after_media.png")

        # 6. Aggiorna testi
        print("Aggiorno testi copy...")
        page.mouse.move(500, 500)
        page.mouse.wheel(0, 400)
        time.sleep(2)

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

        page.screenshot(path=str(PROJECT_ROOT / "meta" / "p3_texts_filled.png"))
        print("Testi aggiornati, screenshot in meta/p3_texts_filled.png")

        # 7. Pubblica
        print("Clicco su pulsante di pubblicazione...")
        pub_btn = page.locator('button:has-text("pubblicare"), div[role="button"]:has-text("pubblicare"), button:has-text("Pubblica"), div[role="button"]:has-text("Pubblica")').last
        if pub_btn.count() > 0:
            print("Trovato pulsante pubblicazione:", pub_btn.inner_text().strip())
            pub_btn.click()
            time.sleep(8)

        # Se compare il dialog 'Esamina le bozze'
        dialog = page.locator('div[role="dialog"]').first
        if dialog.count() > 0 and dialog.is_visible():
            print("Modal di revisione visibile:", dialog.inner_text()[:120].replace('\n', ' '))
            # Spunta 'Prova a pubblicare elementi con errori'
            force_box = dialog.locator('input[type="checkbox"], :has-text("Prova a pubblicare")').first
            if force_box.count() > 0:
                print("Spunto 'Prova a pubblicare elementi con errori'...")
                force_box.click(force=True)
                time.sleep(2)

            confirm_pub = dialog.locator('button:has-text("Pubblica"), div[role="button"]:has-text("Pubblica")').last
            if confirm_pub.count() > 0:
                print("Clicco Pubblica nel modal...")
                confirm_pub.click()
                time.sleep(15)

        page.screenshot(path=str(PROJECT_ROOT / "meta" / "p4_published_outcome.png"))
        print("Screenshot finale salvato in meta/p4_published_outcome.png")

    finally:
        context.close()

if __name__ == "__main__":
    run()

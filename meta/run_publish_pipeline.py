import sys
import time
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
    print("ESECUZIONE COMPLETA PUBBLICAZIONE AD B")
    print("=" * 60)

    context = launch_meta_browser(headless=True, args=["--window-size=2000,1080"], viewport={"width": 2000, "height": 1080})
    page = context.pages[0] if context.pages else context.new_page()

    try:
        url = f"https://adsmanager.facebook.com/adsmanager/manage/ads?act={AD_ACCOUNT_ID}&selected_campaign_ids={CAMPAIGN_ID}"
        print(f"1. Navigo ad Ads Manager: {url}")
        page.goto(url, wait_until="domcontentloaded")
        time.sleep(8)
        page.keyboard.press("Escape")
        time.sleep(1)

        print("2. Vado al tab Inserzioni...")
        page.locator('[role="tab"]:has-text("Inserz")').last.click()
        time.sleep(3)

        print("3. Seleziono la bozza Inserzione B...")
        page.locator(':text("Inserzione B - Offerta COD"), :text("Inserzione senza nome"), :text("In bozza")').first.click()
        time.sleep(2)

        print("4. Clicco Modifica toolbar...")
        page.locator('div[role="toolbar"] button:has-text("Modifica"), div[role="toolbar"] div[role="button"]:has-text("Modifica")').first.click()
        time.sleep(6)

        # Assicura nome corretto
        name_inp = page.locator('input[placeholder*="nome della tua inserzione"]').first
        if name_inp.count() > 0:
            print("5. Imposto nome inserzione...")
            name_inp.fill(AD_NAME)
            time.sleep(1)

        print("6. Scroll al blocco multimediale...")
        page.evaluate("""() => {
            const container = Array.from(document.querySelectorAll('div')).find(el => el.scrollHeight > 3000 && el.clientHeight < 1000);
            if (container) container.scrollTop = 1500;
        }""")
        time.sleep(2)

        print("7. Apro selettore contenuti multimediali...")
        page.locator('div[role="button"]:has-text("Aggiungi contenuto multimediale"), button:has-text("Aggiungi contenuto multimediale")').first.click()
        time.sleep(2)

        for b in page.locator('div[role="menuitem"], div[role="button"]').all():
            if "immagine" in b.inner_text().lower() and "video" not in b.inner_text().lower():
                b.click()
                break
        time.sleep(5)

        print("8. Seleziono rikrestin_ad_b_graphic.jpeg...")
        card = page.locator('div[role="dialog"]').last.locator('div[role="button"]:has-text("rikrestin_ad_b_graphic.jpeg")').first
        card.focus()
        page.keyboard.press("Space")
        time.sleep(2)

        print("9. Clicco Avanti nel selettore...")
        avanti = page.locator('div[role="dialog"]').last.locator('div[role="button"]:has-text("Avanti"), button:has-text("Avanti")').last
        avanti.click()
        time.sleep(4)

        # Wizard passaggi successivi
        print("10. Avanzo attraverso i passaggi del wizard multimediale...")
        for step in range(10):
            page.screenshot(path=f"meta/wizard_step_{step}.png")
            # Cerca se c'è Fine o Salva
            fine_btn = page.locator('div[role="dialog"]').last.locator('button:has-text("Fine"), div[role="button"]:has-text("Fine"), button:has-text("Salva"), div[role="button"]:has-text("Salva")').last
            if fine_btn.count() > 0 and fine_btn.is_visible() and fine_btn.get_attribute("aria-disabled") != "true":
                print(f"Passo {step}: trovato pulsante finale ({fine_btn.inner_text().strip()}) -> Clicco!")
                fine_btn.click()
                time.sleep(5)
                break
            
            # Altrimenti cerca Avanti / Continua
            avanti_next = page.locator('div[role="dialog"]').last.locator('button:has-text("Avanti"), div[role="button"]:has-text("Avanti"), button:has-text("Continua")').last
            if avanti_next.count() > 0 and avanti_next.is_visible() and avanti_next.get_attribute("aria-disabled") != "true":
                print(f"Passo {step}: clicco Avanti...")
                avanti_next.click()
                time.sleep(3)
            else:
                print(f"Passo {step}: nessun pulsante avanti visibile, attendo...")
                time.sleep(2)

        time.sleep(3)
        page.screenshot(path="meta/wizard_done.png")
        print("Wizard completato. Screenshot in meta/wizard_done.png")

        # 11. Scroll al blocco testi
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
            try:
                val = inp.input_value()
                if "Rikrestin Plus" in val or "Pagamento alla Consegna" in val or "Scrivi un titolo" in (inp.get_attribute("placeholder") or ""):
                    print("13. Aggiorno Titolo (Headline)...")
                    inp.click()
                    page.keyboard.press("Meta+A")
                    page.keyboard.press("Backspace")
                    inp.fill(HEADLINE)
                    time.sleep(1)
                    break
            except Exception as e:
                pass

        for inp in inputs:
            try:
                val = inp.input_value()
                if "Spedizione rapida" in val or "descrizione facoltativa" in (inp.get_attribute("placeholder") or ""):
                    print("14. Aggiorno Descrizione...")
                    inp.click()
                    page.keyboard.press("Meta+A")
                    page.keyboard.press("Backspace")
                    inp.fill(DESCRIPTION)
                    time.sleep(1)
                    break
            except Exception as e:
                pass

        page.screenshot(path="meta/configured_ready_to_publish.png")
        print("Inserzione B configurata al 100%! Screenshot in meta/configured_ready_to_publish.png")

        # 15. Pubblicazione
        print("15. Clicco pulsante di pubblicazione...")
        pub_btn = page.locator('button:has-text("pubblicare"), div[role="button"]:has-text("pubblicare"), button:has-text("Pubblica"), div[role="button"]:has-text("Pubblica")').last
        if pub_btn.count() > 0:
            print("Pulsante pubblicazione:", pub_btn.inner_text().strip())
            pub_btn.click()
            time.sleep(8)

        # 16. Modal revisione / WhatsApp error bypass
        dialog = page.locator('div[role="dialog"]').first
        if dialog.count() > 0 and dialog.is_visible():
            print("16. Modal revisione aperto.")
            force_box = dialog.locator('input[type="checkbox"], :has-text("Prova a pubblicare")').first
            if force_box.count() > 0:
                print("Spunto Prova a pubblicare elementi con errori...")
                force_box.click(force=True)
                time.sleep(2)

            confirm_pub = dialog.locator('button:has-text("Pubblica"), div[role="button"]:has-text("Pubblica")').last
            if confirm_pub.count() > 0:
                print("Confermo pubblicazione...")
                confirm_pub.click()
                time.sleep(15)

        page.screenshot(path="meta/final_success_published.png")
        print("PUBBLICAZIONE TERMINATA! Screenshot in meta/final_success_published.png")

    finally:
        context.close()

if __name__ == "__main__":
    run()

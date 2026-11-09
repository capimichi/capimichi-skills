import sys
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from meta.paths import get_cache_dir
from meta.browser import launch_meta_browser

AD_ACCOUNT_ID = "1116925509636183"
IMAGE_PATH = PROJECT_ROOT / "meta" / "assets" / "rikrestin_hero.jpeg"
DESTINATION_URL = "https://naturalesostenibile.pagead.online/landing/ntm/rikrestin_2x49/1/?ref=e75d64c2cffa"
DISPLAY_URL = "naturalesostenibile.pagead.online"

PRIMARY_TEXT = """Noti capelli deboli, diradamento o caduta nei cambi di stagione? 🌿

Dalla ricerca erboristica avanzata nasce RiKrestin Plus: la lozione spray naturale potenziata con:
🌱 Serenoa Repens: contrasta l'indebolimento alla radice
🌿 Fieno Greco: stimola e nutre i bulbi silenti
💧 Arginina & Pantenolo: donano forza, corposità e spessore al fusto

✨ Senza siliconi, non unge, rapido assorbimento.

📦 Offerta Speciale per la Community:
2 Confezioni a soli 49,99€ con:
✅ Pagamento in contanti alla consegna (COD)
✅ Spedizione rapida e gratuita in tutta Italia"""

HEADLINE = "Rikrestin Plus 2x49€ - Pagamento alla Consegna"
DESCRIPTION = "Spedizione rapida e gratuita in tutta Italia"

def run():
    print("=" * 60)
    print("FINALIZZAZIONE INSERZIONE NATIVA SU META ADS")
    print(f"URL: {DESTINATION_URL}")
    print("=" * 60)

    context = launch_meta_browser(headless=False)
    page = context.pages[0] if context.pages else context.new_page()

    try:
        url = f"https://adsmanager.facebook.com/adsmanager/manage/ads?act={AD_ACCOUNT_ID}&selected_campaign_ids=120251426951480676&treenav=true"
        print(f"1. Apertura: {url}")
        page.goto(url, wait_until="networkidle")
        time.sleep(5)

        # Chiudi 'Crea visualizzazione' se aperto
        page.mouse.click(908, 423)
        time.sleep(1)
        page.keyboard.press("Escape")
        time.sleep(1)

        # Seleziona riga e apri Modifica
        print("2. Apertura editor inserzione...")
        chk = page.locator('div[role="row"]').nth(1).locator('input[type="checkbox"]').first
        if chk.count() > 0:
            chk.click(force=True)
            time.sleep(1)

        mod_btn = page.locator('button:has-text("Modifica")').first
        mod_btn.click()
        time.sleep(4)

        # 3. Cambia Combobox 1 a "Crea inserzione"
        print("3. Selezione 'Crea inserzione'...")
        combo1 = page.locator('div[role="combobox"]:has-text("Usa post esistente")').first
        if combo1.count() > 0:
            combo1.click()
            time.sleep(1)
            crea_opt = page.locator('div[role="option"]:has-text("Crea inserzione"), text="Crea inserzione"').first
            if crea_opt.count() > 0:
                crea_opt.click()
                print("Selezionato 'Crea inserzione' con successo!")
                time.sleep(4)

        # 4. Aggiungi Immagine
        print("4. Selezione immagine...")
        add_media = page.locator('button:has-text("Aggiungi elementi multimediali"), div[role="button"]:has-text("Aggiungi elementi multimediali")').first
        if add_media.count() > 0:
            add_media.click()
            time.sleep(1)
            add_img = page.locator('text="Aggiungi immagine"').first
            if add_img.count() > 0:
                add_img.click()
                time.sleep(3)

                # Seleziona la miniatura dell'account
                thumb = page.locator('img[src*="scontent"]').first
                if thumb.count() > 0:
                    print("Seleziono thumbnail esistente...")
                    thumb.click()
                    time.sleep(2)
                else:
                    file_input = page.locator('input[type="file"]').first
                    if file_input.count() > 0:
                        file_input.set_input_files(str(IMAGE_PATH))
                        time.sleep(4)

                avanti = page.locator('button:has-text("Avanti"), button:has-text("Continua")').first
                if avanti.count() > 0:
                    avanti.click()
                    time.sleep(2)
                fine = page.locator('button:has-text("Fine"), button:has-text("Salva")').first
                if fine.count() > 0:
                    fine.click()
                    time.sleep(3)

        # 5. Inserimento Testo principale
        print("5. Testo principale...")
        # Cerchiamo il box per il testo principale
        textboxes = page.locator('div[role="textbox"], textarea').all()
        for tb in textboxes:
            placeholder = tb.get_attribute("placeholder") or ""
            aria = tb.get_attribute("aria-label") or ""
            if "testo" in placeholder.lower() or "testo" in aria.lower() or "principale" in aria.lower():
                tb.click()
                tb.fill(PRIMARY_TEXT)
                print("Testo principale inserito!")
                time.sleep(2)
                break

        # 6. Titolo (Headline)
        print("6. Titolo...")
        inputs = page.locator('input[type="text"]').all()
        for inp in inputs:
            p = (inp.get_attribute("placeholder") or "").lower()
            a = (inp.get_attribute("aria-label") or "").lower()
            if "titolo" in p or "titolo" in a:
                inp.click()
                inp.fill(HEADLINE)
                print("Titolo inserito!")
                time.sleep(1)
                break

        # 7. Descrizione
        print("7. Descrizione...")
        for inp in inputs:
            p = (inp.get_attribute("placeholder") or "").lower()
            a = (inp.get_attribute("aria-label") or "").lower()
            if "descrizione" in p or "descrizione" in a:
                inp.click()
                inp.fill(DESCRIPTION)
                print("Descrizione inserita!")
                time.sleep(1)
                break

        # 8. Destinazione: Sito Web URL
        print("8. URL del sito web...")
        url_inputs = page.locator('input[placeholder*="https://"], input[aria-label*="URL"]').all()
        for u in url_inputs:
            u.click()
            u.fill(DESTINATION_URL)
            print("URL di destinazione inserito!")
            time.sleep(1)

        # 9. Link visualizzato
        for inp in inputs:
            a = (inp.get_attribute("aria-label") or "").lower()
            p = (inp.get_attribute("placeholder") or "").lower()
            if "visualizzato" in a or "example.com" in p:
                inp.click()
                inp.fill(DISPLAY_URL)
                print("Link visualizzato inserito!")
                time.sleep(1)
                break

        # 10. Call to action
        print("9. Call to action...")
        cta = page.locator('div[role="combobox"]:has-text("Call to action"), div[role="combobox"]:has-text("Nessun pulsante"), div[role="combobox"]:has-text("Scopri di più")').first
        if cta.count() > 0:
            txt = cta.inner_text()
            if "Scopri di più" not in txt:
                cta.click()
                time.sleep(1)
                opt = page.locator('div[role="option"]:has-text("Scopri di più")').first
                if opt.count() > 0:
                    opt.click()
                    print("Pulsante 'Scopri di più' impostato!")
                    time.sleep(2)

        # Salva screenshot di verifica
        proof1 = PROJECT_ROOT / "meta" / "native_ad_setup_proof.png"
        page.screenshot(path=str(proof1))
        print("Screenshot configurazione:", proof1)

        # 11. Clicca Pubblica
        print("10. Pubblicazione inserzione...")
        pub_btn = page.locator('button:has-text("Pubblica")').filter(has_text="Pubblica").last
        if pub_btn.count() > 0:
            pub_btn.click()
            print("Pubblica cliccato! Attendo 12s per salvataggio...")
            time.sleep(12)

        # 12. Torna a livello Campagne e accendi lo switch della campagna
        print("11. Riattivazione campagna...")
        page.goto(f"https://adsmanager.facebook.com/adsmanager/manage/campaigns?act={AD_ACCOUNT_ID}", wait_until="networkidle")
        time.sleep(5)

        # Switch di Rikrestin
        cell = page.locator('text="Rikrestin 2x49 - Test Vendite"').first
        if cell.count() > 0:
            box = cell.bounding_box()
            if box:
                page.mouse.click(145.0, box['y'] + (box['height'] / 2))
                time.sleep(4)

        final_proof = PROJECT_ROOT / "meta" / "campaign_live_and_active.png"
        page.screenshot(path=str(final_proof))
        print("Screenshot finale salvato:", final_proof)

    finally:
        context.close()

if __name__ == "__main__":
    run()

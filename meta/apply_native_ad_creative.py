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
    cache_dir = get_cache_dir()
    print("=" * 60)
    print("APPLICAZIONE INSERZIONE NATIVA (HEADLESS=FALSE)")
    print("=" * 60)

    context = launch_meta_browser(headless=False)
    page = context.pages[0] if context.pages else context.new_page()

    try:
        url = f"https://adsmanager.facebook.com/adsmanager/manage/campaigns?act={AD_ACCOUNT_ID}"
        page.goto(url, wait_until="networkidle")
        time.sleep(5)

        # 1. Drilldown su Rikrestin
        print("1. Apertura campagna Rikrestin...")
        page.locator('text="Rikrestin 2x49 - Test Vendite"').first.click()
        time.sleep(3)

        # 2. Vai alla tab Inserzioni
        print("2. Tab Inserzioni...")
        ads_tab = page.locator('button:has-text("Inserzioni"), div[role="tab"]:has-text("Inserzioni")').first
        if ads_tab.count() > 0:
            ads_tab.click()
            time.sleep(4)

        # 3. Clicca Modifica
        print("3. Apertura editor inserzione...")
        chk = page.locator('div[role="row"] input[type="checkbox"]').all()
        if len(chk) >= 2:
            chk[1].click(force=True)
            time.sleep(1)

        mod_btn = page.locator('button:has-text("Modifica")').first
        if mod_btn.count() > 0:
            mod_btn.click()
            time.sleep(5)

        # 4. Nel pannello Modifica:
        # Passa da "Usa post esistente" a "Crea inserzione"
        print("4. Selezione 'Crea inserzione'...")
        # Cerca combobox o opzione "Usa post esistente"
        post_exist = page.locator('text="Usa post esistente"').first
        if post_exist.count() > 0:
            print("Trovato 'Usa post esistente', clicco per aprire opzioni...")
            post_exist.click()
            time.sleep(2)
            crea_opt = page.locator('div[role="option"]:has-text("Crea inserzione"), text="Crea inserzione"').first
            if crea_opt.count() > 0:
                print("Seleziono 'Crea inserzione'...")
                crea_opt.click()
                time.sleep(3)

        # 5. Caricamento / Selezione Media
        print("5. Gestione Elementi multimediali...")
        add_media = page.locator('button:has-text("Aggiungi elementi multimediali"), div[role="button"]:has-text("Aggiungi elementi multimediali")').first
        if add_media.count() > 0:
            add_media.click()
            time.sleep(1)
            add_img = page.locator('text="Aggiungi immagine"').first
            if add_img.count() > 0:
                add_img.click()
                time.sleep(3)
                # Nel modal di selezione immagine:
                # Controlla se la foto di Rikrestin è già presente nella libreria dell'account
                existing_thumb = page.locator('img[src*="scontent"]').first
                if existing_thumb.count() > 0:
                    print("Seleziono immagine già presente nell'account...")
                    existing_thumb.click()
                    time.sleep(2)
                    avanti_btn = page.locator('button:has-text("Avanti"), button:has-text("Continua")').first
                    if avanti_btn.count() > 0:
                        avanti_btn.click()
                        time.sleep(2)
                        fine_btn = page.locator('button:has-text("Fine"), button:has-text("Salva")').first
                        if fine_btn.count() > 0:
                            fine_btn.click()
                            time.sleep(3)
                else:
                    # Upload da file
                    print(f"Caricamento file {IMAGE_PATH}...")
                    file_input = page.locator('input[type="file"]').first
                    if file_input.count() > 0:
                        file_input.set_input_files(str(IMAGE_PATH))
                        time.sleep(5)
                        avanti_btn = page.locator('button:has-text("Avanti"), button:has-text("Continua")').first
                        if avanti_btn.count() > 0:
                            avanti_btn.click()
                            time.sleep(2)
                            fine_btn = page.locator('button:has-text("Fine"), button:has-text("Salva")').first
                            if fine_btn.count() > 0:
                                fine_btn.click()
                                time.sleep(3)

        # 6. Testo principale
        print("6. Inserimento Testo principale...")
        # Cerca textarea per il testo principale
        text_area = page.locator('textarea[placeholder*="testo"], div[role="textbox"][aria-label*="Testo principale"]').first
        if text_area.count() > 0:
            text_area.click()
            text_area.fill(PRIMARY_TEXT)
            time.sleep(2)

        # 7. Titolo (Headline)
        print("7. Inserimento Titolo...")
        headline_input = page.locator('input[placeholder*="titolo"], input[aria-label*="Titolo"]').first
        if headline_input.count() > 0:
            headline_input.click()
            headline_input.fill(HEADLINE)
            time.sleep(1)

        # 8. Descrizione
        print("8. Inserimento Descrizione...")
        desc_input = page.locator('input[placeholder*="descrizione"], input[aria-label*="Descrizione"]').first
        if desc_input.count() > 0:
            desc_input.click()
            desc_input.fill(DESCRIPTION)
            time.sleep(1)

        # 9. Destinazione: URL del sito web
        print("9. Inserimento URL del sito web...")
        url_input = page.locator('input[placeholder*="https://"], input[aria-label*="URL"]').first
        if url_input.count() > 0:
            url_input.click()
            url_input.fill(DESTINATION_URL)
            time.sleep(2)

        # 10. Link visualizzato
        disp_input = page.locator('input[aria-label*="Link visualizzato"], input[placeholder*="example.com"]').first
        if disp_input.count() > 0:
            disp_input.click()
            disp_input.fill(DISPLAY_URL)
            time.sleep(1)

        # 11. Call to Action (Pulsante)
        print("10. Selezione Call To Action: Scopri di più...")
        cta_combo = page.locator('div[role="combobox"]:has-text("Nessun pulsante"), div[role="combobox"]:has-text("Scopri di più"), div[role="combobox"]:has-text("Call to action")').first
        if cta_combo.count() > 0:
            txt = cta_combo.inner_text()
            if "Scopri di più" not in txt:
                cta_combo.click()
                time.sleep(1)
                opt = page.locator('div[role="option"]:has-text("Scopri di più"), text="Scopri di più"').first
                if opt.count() > 0:
                    opt.click()
                    time.sleep(2)

        # 12. Screenshot stato editor
        shot = cache_dir / "native_ad_configured.png"
        page.screenshot(path=str(shot))
        print("Screenshot salvato:", shot)

        # 13. Pubblica modifiche
        print("11. Clicco su Pubblica...")
        pub_btn = page.locator('button:has-text("Pubblica")').filter(has_text="Pubblica").last
        if pub_btn.count() > 0:
            pub_btn.click()
            print("Pubblica cliccato! Attendo 10s...")
            time.sleep(10)

        # 14. Riattiva la campagna
        print("12. Ritorno a livello Campagne per riattivazione...")
        page.goto(f"https://adsmanager.facebook.com/adsmanager/manage/campaigns?act={AD_ACCOUNT_ID}", wait_until="networkidle")
        time.sleep(5)

        # Accendi lo switch di Rikrestin
        cell = page.locator('text="Rikrestin 2x49 - Test Vendite"').first
        if cell.count() > 0:
            box = cell.bounding_box()
            if box:
                print(f"Clicco toggle switch a (145.0, {box['y'] + box['height']/2})...")
                page.mouse.click(145.0, box['y'] + (box['height'] / 2))
                time.sleep(4)

        final_shot = cache_dir / "campaign_reactivated_proof.png"
        page.screenshot(path=str(final_shot))
        print("Screenshot finale salvato:", final_shot)

    finally:
        context.close()

if __name__ == "__main__":
    run()

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
    context = launch_meta_browser(headless=False)
    page = context.pages[0] if context.pages else context.new_page()

    try:
        url = f"https://adsmanager.facebook.com/adsmanager/manage/campaigns?act={AD_ACCOUNT_ID}"
        print(f"1. Navigazione: {url}")
        page.goto(url, wait_until="networkidle")
        time.sleep(5)

        # Chiudi eventuali dialog
        page.keyboard.press("Escape")
        time.sleep(1)

        # 2. Clicca sulla campagna Rikrestin
        print("2. Apertura campagna...")
        page.locator('text="Rikrestin 2x49 - Test Vendite"').first.click()
        time.sleep(3)

        # 3. Clicca sulla tab esatta delle Inserzioni
        print("3. Clicco sulla tab Inserzioni...")
        page.get_by_role("tab", name="Inserzioni per 1 Campagna", exact=True).click()
        time.sleep(4)

        # 4. Seleziona la riga inserzione e clicca Modifica
        print("4. Selezione riga e apertura Modifica...")
        chk = page.locator('div[role="row"] input[type="checkbox"]').all()
        if len(chk) >= 2:
            chk[1].click(force=True)
            time.sleep(1)

        mod_btn = page.locator('button:has-text("Modifica")').first
        if mod_btn.count() > 0:
            mod_btn.click()
            time.sleep(4)

        # 5. Cambia Combobox 1 da 'Usa post esistente' a 'Crea inserzione'
        print("5. Cambio a 'Crea inserzione'...")
        combo = page.locator('div[role="combobox"]:has-text("Usa post esistente")').first
        if combo.count() > 0:
            combo.click()
            time.sleep(1)
            opt = page.locator('div[role="option"]:has-text("Crea inserzione")').first
            if opt.count() > 0:
                opt.click()
                print("Selezionato 'Crea inserzione'!")
                time.sleep(3)

        # 6. Aggiungi elemento multimediale / immagine
        print("6. Aggiunta immagine...")
        add_btn = page.locator('button:has-text("Aggiungi elementi multimediali"), div[role="button"]:has-text("Aggiungi elementi multimediali")').first
        if add_btn.count() > 0:
            add_btn.click()
            time.sleep(1)
            add_img = page.locator('text="Aggiungi immagine"').first
            if add_img.count() > 0:
                add_img.click()
                time.sleep(3)

                # Se c'è già l'immagine nella galleria, cliccala
                img_thumb = page.locator('img[src*="scontent"]').first
                if img_thumb.count() > 0:
                    print("Selezione immagine esistente...")
                    img_thumb.click()
                    time.sleep(2)
                else:
                    # Carica file
                    file_input = page.locator('input[type="file"]').first
                    if file_input.count() > 0:
                        file_input.set_input_files(str(IMAGE_PATH))
                        time.sleep(5)

                # Clicca Avanti/Continua e Fine
                avanti = page.locator('button:has-text("Avanti"), button:has-text("Continua")').first
                if avanti.count() > 0:
                    avanti.click()
                    time.sleep(2)
                fine = page.locator('button:has-text("Fine"), button:has-text("Salva")').first
                if fine.count() > 0:
                    fine.click()
                    time.sleep(3)

        # 7. Testo principale
        print("7. Compilazione Testo principale...")
        textarea = page.locator('textarea[placeholder*="testo"], div[role="textbox"]').first
        if textarea.count() > 0:
            textarea.click()
            textarea.fill(PRIMARY_TEXT)
            time.sleep(2)

        # 8. Titolo
        print("8. Compilazione Titolo...")
        headline = page.locator('input[placeholder*="titolo"], input[aria-label*="Titolo"]').first
        if headline.count() > 0:
            headline.click()
            headline.fill(HEADLINE)
            time.sleep(1)

        # 9. Descrizione
        print("9. Compilazione Descrizione...")
        desc = page.locator('input[placeholder*="descrizione"], input[aria-label*="Descrizione"]').first
        if desc.count() > 0:
            desc.click()
            desc.fill(DESCRIPTION)
            time.sleep(1)

        # 10. URL del sito web
        print("10. Compilazione URL sito web...")
        url_in = page.locator('input[placeholder*="https://"], input[aria-label*="URL"]').first
        if url_in.count() > 0:
            url_in.click()
            url_in.fill(DESTINATION_URL)
            time.sleep(2)

        # 11. Link visualizzato
        disp_in = page.locator('input[aria-label*="Link visualizzato"], input[placeholder*="example.com"]').first
        if disp_in.count() > 0:
            disp_in.click()
            disp_in.fill(DISPLAY_URL)
            time.sleep(1)

        # 12. Call to action
        print("11. Selezione Call to action 'Scopri di più'...")
        cta = page.locator('div[role="combobox"]:has-text("Nessun pulsante"), div[role="combobox"]:has-text("Call to action")').first
        if cta.count() > 0:
            cta.click()
            time.sleep(1)
            opt_cta = page.locator('div[role="option"]:has-text("Scopri di più")').first
            if opt_cta.count() > 0:
                opt_cta.click()
                time.sleep(2)

        # 13. Salva screenshot configurazione completata
        shot_done = PROJECT_ROOT / "meta" / "ad_configured_final.png"
        page.screenshot(path=str(shot_done))
        print(f"Screenshot salvato in {shot_done}")

        # 14. Clicca Pubblica
        print("12. Pubblicazione modifiche...")
        pub_btn = page.locator('button:has-text("Pubblica")').filter(has_text="Pubblica").last
        if pub_btn.count() > 0:
            pub_btn.click()
            print("Pubblica cliccato! Attendo 10s...")
            time.sleep(10)

        # 15. Riattiva campagna
        print("13. Ritorno a livello Campagne per riattivazione switch...")
        page.goto(f"https://adsmanager.facebook.com/adsmanager/manage/campaigns?act={AD_ACCOUNT_ID}", wait_until="networkidle")
        time.sleep(4)

        cell = page.locator('text="Rikrestin 2x49 - Test Vendite"').first
        if cell.count() > 0:
            box = cell.bounding_box()
            if box:
                page.mouse.click(145.0, box['y'] + (box['height'] / 2))
                time.sleep(4)

        confirm_shot = PROJECT_ROOT / "meta" / "campaign_active_verified.png"
        page.screenshot(path=str(confirm_shot))
        print(f"Screenshot finale salvato in {confirm_shot}")

    finally:
        context.close()

if __name__ == "__main__":
    run()

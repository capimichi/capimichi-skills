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
    print("FIX & PUBLISH AD B")
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

        # 1. Controlla se c'è un modal con "Correggi l'errore"
        fix_err_btn = page.locator('text="Correggi l\'errore"').first
        if fix_err_btn.count() > 0 and fix_err_btn.is_visible():
            print("Modal errore presente! Clicco su 'Correggi l'errore'...")
            fix_err_btn.click()
            time.sleep(6)
        else:
            print("Nessun modal 'Correggi l'errore' visibile. Verifico selettori tabella...")
            page.keyboard.press("Escape")
            time.sleep(1)
            # Seleziona la riga della bozza
            boxes = page.locator('input[type="checkbox"]').all()
            print(f"Trovate {len(boxes)} checkbox.")
            if len(boxes) > 1:
                # Se la prima riga non è selezionata, selezionala
                if not boxes[1].is_checked():
                    print("Spunto checkbox riga 1...")
                    boxes[1].click(force=True)
                    time.sleep(1)
            
            # Clicca Modifica
            mod_btn = page.locator('button:has-text("Modifica"), div[role="button"]:has-text("Modifica")').first
            if mod_btn.count() > 0 and mod_btn.is_visible():
                print("Clicco pulsante Modifica...")
                mod_btn.click()
                time.sleep(6)

        page.screenshot(path=str(PROJECT_ROOT / "meta" / "editor_after_open.png"))
        print("Screenshot salvato in meta/editor_after_open.png")

        # Dump degli elementi e testi nel pannello
        panel_text = page.locator('body').inner_text()
        with open(PROJECT_ROOT / "meta" / "editor_text_dump.txt", "w", encoding="utf-8") as f:
            f.write(panel_text)

        # Cerchiamo input e bottoni rilevanti
        print("\n--- Analisi campi ed errori nell'editor ---")
        lines = [l.strip() for l in panel_text.split('\n') if l.strip()]
        for l in lines:
            if any(w in l.lower() for w in ["errore", "obbligatorio", "multimediale", "immagine", "sostituisci", "creativit"]):
                print("   Found line:", l)

    finally:
        context.close()

if __name__ == "__main__":
    run()

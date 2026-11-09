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

📦 Offerta Speciale Limitata:
2 Confezioni a soli 49,99€ con:
✅ Pagamento in contanti alla consegna (COD)
✅ Spedizione rapida e gratuita in tutta Italia"""

HEADLINE = "Rikrestin Plus 2x49€ - Pagamento alla Consegna"
DESCRIPTION = "Spedizione rapida e gratuita in tutta Italia"

def setup():
    cache_dir = get_cache_dir()
    print("=" * 60)
    print("CONFIGURAZIONE INSERZIONE NATIVA (HEADLESS=FALSE)")
    print(f"URL Destinazione: {DESTINATION_URL}")
    print("=" * 60)

    context = launch_meta_browser(headless=False)
    page = context.pages[0] if context.pages else context.new_page()

    try:
        # Apri direttamente il livello Inserzioni per l'account
        url = f"https://adsmanager.facebook.com/adsmanager/manage/ads?act={AD_ACCOUNT_ID}"
        print(f"Navigazione a: {url}")
        page.goto(url, wait_until="networkidle")
        time.sleep(5)

        # Chiudi pannelli laterali "Crea visualizzazione" se aperti
        close_btn = page.locator('button[aria-label="Chiudi"], div[aria-label="Chiudi"]').all()
        for b in close_btn:
            try:
                b.click()
                time.sleep(1)
            except Exception:
                pass

        # Cerca la riga dell'inserzione relativa a Rikrestin
        print("Ricerca inserzione Rikrestin...")
        ad_row = page.locator('div[role="row"]:has-text("Rikrestin")').first
        if ad_row.count() > 0:
            print("Riga inserzione Rikrestin trovata!")
            # Hover sulla riga per far apparire i tasti azione
            ad_row.hover()
            time.sleep(1)
            modifica_btn = ad_row.locator('button:has-text("Modifica"), div[role="button"]:has-text("Modifica")').first
            if modifica_btn.count() > 0:
                print("Click su Modifica inserzione...")
                modifica_btn.click()
                time.sleep(4)
            else:
                # Seleziona checkbox della riga e clicca Modifica in alto
                chk = ad_row.locator('input[type="checkbox"]').first
                chk.click(force=True)
                time.sleep(1)
                top_mod = page.locator('button:has-text("Modifica"), div[role="button"]:has-text("Modifica")').filter(has_text="Modifica").first
                top_mod.click()
                time.sleep(4)
        else:
            print("Nessuna riga specifica con 'Rikrestin' nel testo; controllo tutte le righe...")
            rows = page.locator('div[role="row"]').all()
            for r in rows:
                print("Riga:", r.inner_text().strip().replace('\n', ' | ')[:120])

        shot_editor = cache_dir / "ad_editor_opened.png"
        page.screenshot(path=str(shot_editor))
        print("Screenshot editor salvato:", shot_editor)

        # Ispezione campi nell'editor
        print("Attendo 10s per permettere visualizzazione...")
        time.sleep(10)

    finally:
        context.close()

if __name__ == "__main__":
    setup()

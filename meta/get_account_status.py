import sys
import time
from pathlib import Path
from bs4 import BeautifulSoup

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from meta.paths import get_cache_dir
from meta.browser import launch_meta_browser

AD_ACCOUNT_ID = "1116925509636183"
BILLING_URL = f"https://business.facebook.com/billing_hub/payment_settings?act={AD_ACCOUNT_ID}"
ADSMANAGER_BILLING_URL = f"https://adsmanager.facebook.com/adsmanager/billing/payment_settings?act={AD_ACCOUNT_ID}"

def inspect_billing(headless: bool = True):
    cache_dir = get_cache_dir()
    print("=" * 60)
    print("VERIFICA STATO ACCOUNT E METODI DI PAGAMENTO META")
    print(f"Ad Account ID: {AD_ACCOUNT_ID}")
    print("=" * 60)

    context = launch_meta_browser(headless=headless)
    page = context.pages[0] if context.pages else context.new_page()

    try:
        print(f"1. Navigazione verso: {BILLING_URL}")
        page.goto(BILLING_URL, wait_until="domcontentloaded")
        print("Attendo caricamento interfaccia di fatturazione...")
        time.sleep(8)

        # Se fa redirect o non carica, proviamo l'alternativa adsmanager
        print(f"URL attuale: {page.url}")
        if "login" in page.url:
            print("[ATTENZIONE] È stato richiesto il login! Riprova con login.py")
            return

        # Screenshot
        screenshot_path = cache_dir / "meta_billing.png"
        page.screenshot(path=str(screenshot_path))
        print(f"Screenshot salvato: {screenshot_path}")

        # Estraiamo il testo e proviamo a individuare carte / metodi di pagamento
        content = page.content()
        (cache_dir / "meta_billing.html").write_text(content, encoding="utf-8")

        soup = BeautifulSoup(content, "html.parser")
        
        # Testo visibile
        body_text = page.inner_text("body")
        print("\n--- ANALISI TESTO SEZIONE FATTURAZIONE ---")
        lines = [line.strip() for line in body_text.splitlines() if line.strip()]
        
        # Cerca parole chiave relative ai pagamenti
        keywords = ["carta", "visa", "mastercard", "scad", "pagamento", "sald", "debito", "limite", "fattur", "metod", "iban", "paypal", "eur", "€", "aggiorna", "rifiut", "disattiv"]
        relevant_lines = []
        for line in lines:
            if any(kw in line.lower() for kw in keywords):
                if line not in relevant_lines:
                    relevant_lines.append(line)

        for line in relevant_lines[:35]:
            print(f"- {line}")

    except Exception as e:
        print(f"Errore durante l'ispezione: {e}")
    finally:
        context.close()

if __name__ == "__main__":
    is_headless = "--no-headless" not in sys.argv
    inspect_billing(headless=is_headless)

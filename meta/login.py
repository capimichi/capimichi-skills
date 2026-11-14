import os
import sys
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from meta.paths import get_browser_session_dir, get_home_dir
from meta.browser import launch_meta_browser

def load_credentials_from_zshrc():
    """Legge le credenziali da .zshrc.local se non presenti nell'ambiente attuale."""
    email = os.environ.get("META_EMAIL")
    password = os.environ.get("META_PASSWORD")
    if email and password:
        return email, password

    zshrc_local = get_home_dir() / ".zshrc.local"
    if zshrc_local.exists():
        for line in zshrc_local.read_text().splitlines():
            line = line.strip()
            if line.startswith("export META_EMAIL="):
                email = line.split("=", 1)[1].strip("'\"")
            elif line.startswith("export META_PASSWORD="):
                password = line.split("=", 1)[1].strip("'\"")

    return email, password

def main():
    email, password = load_credentials_from_zshrc()
    profile_dir = get_browser_session_dir()

    print("=" * 60, flush=True)
    print("META / FACEBOOK - LOGIN & SALVATAGGIO SESSIONE BROWSER (XDG)", flush=True)
    print("=" * 60, flush=True)
    print(f"Directory sessione persistente: {profile_dir}", flush=True)
    print(f"Account: {email if email else 'Non configurato'}", flush=True)
    print("-" * 60, flush=True)

    context = launch_meta_browser(headless=False)
    page = context.pages[0] if context.pages else context.new_page()

    print("Apertura di Facebook (https://www.facebook.com/)...", flush=True)
    page.goto("https://www.facebook.com/", wait_until="domcontentloaded")
    time.sleep(2)

    # Gestione banner cookie se presente
    try:
        cookie_btn = page.locator('button:has-text("Consenti"), button:has-text("Accetta"), button:has-text("Allow")').first
        if cookie_btn.is_visible():
            cookie_btn.click()
            time.sleep(1)
    except Exception:
        pass

    # Compilazione credenziali
    try:
        email_el = page.locator('input[name="email"], input[type="email"], #email').first
        pass_el = page.locator('input[name="pass"], input[type="password"], #pass').first

        if email_el.count() > 0 and email:
            print(f"Compilazione automatica username ({email})...", flush=True)
            email_el.click()
            email_el.fill(email)
            time.sleep(0.5)

            if pass_el.count() > 0 and password:
                print("Compilazione automatica password...", flush=True)
                pass_el.click()
                pass_el.fill(password)
                time.sleep(0.5)

            print("Credenziali inserite con successo!", flush=True)
            
            # Clicca su Accedi
            submit_btn = page.locator('button[name="login"], input[type="submit"], button[type="submit"]').first
            if submit_btn.count() > 0:
                print("Click su pulsante Accedi in corso...", flush=True)
                submit_btn.click()
                time.sleep(3)
    except Exception as e:
        print(f"Errore durante la compilazione: {e}", flush=True)

    print("\n[ISTRUZIONI]", flush=True)
    print("1. Nella finestra del browser, premi Accedi se le credenziali sono inserite.", flush=True)
    print("2. Completa eventuali verifiche (2FA, codice SMS/email o approvazione checkpoint).", flush=True)
    print("3. Quando sei dentro Facebook o Meta Business Suite, torna qui in chat.", flush=True)
    print("-" * 60, flush=True)

    try:
        input("\nIn attesa di conferma...")
    except (KeyboardInterrupt, EOFError):
        print("\nInterruzione rilevata.", flush=True)

    # Navigazione facoltativa per verificare Business Suite
    print("\nVerifica accesso a Meta Business Suite...", flush=True)
    try:
        page.goto("https://business.facebook.com/", wait_until="domcontentloaded")
        time.sleep(3)
        print(f"URL attuale: {page.url}", flush=True)
        print(f"Titolo: {page.title()}", flush=True)
    except Exception as e:
        print(f"Nota: {e}", flush=True)

    print("\nChiusura del browser e salvataggio della sessione...", flush=True)
    context.close()
    print("Sessione Meta salvata con successo in:", flush=True)
    print(f"  {profile_dir}", flush=True)

if __name__ == "__main__":
    main()

import sys
import time
from pathlib import Path

# Assicura che la root del progetto sia nel sys.path per importare worldfilia
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from worldfilia.paths import get_browser_session_dir, get_credentials, get_totp_code
from worldfilia.browser import launch_worldfilia_browser

LOGIN_URL = "https://portal.worldfilia.net/"
PUBLISHER_URL = "https://portal.worldfilia.net/publisher"


def attempt_automated_login(page, credentials: dict) -> bool:
    """
    Tenta il login automatico compilando username, password e 2FA/TOTP se presenti.
    """
    username = credentials.get("username")
    password = credentials.get("password")

    if not username or not password:
        return False

    print(f"\n🔑 Credenziali rilevate dalle variabili d'ambiente per l'utente: {username}")
    print("🤖 Compilazione automatica del modulo di login...")

    try:
        # Attesa della comparsa dei campi login
        page.wait_for_selector('input[name="username"]', timeout=10000)
        page.fill('input[name="username"]', username)
        page.fill('input[name="password"]', password)
        page.click('button[type="submit"]')
        print("  ✓ Username e password inviati.")
    except Exception as e:
        print(f"  ⚠️ Errore durante l'inserimento credenziali: {e}")
        return False

    # Verifica se siamo già stati reindirizzati o se serve 2FA
    time.sleep(3)
    if "publisher" in page.url:
        print("  ✅ Accesso completato direttamente (sessione già attiva o 2FA non richiesto)!")
        return True

    # Controllo eventuale richiesta codice 2FA
    print("⏳ Verifica presenza richiesta 2FA / Codice OTP...")
    totp_input_selectors = [
        'input[name="code"]',
        'input[name="otp"]',
        'input[name="totp"]',
        'input[placeholder*="Codice" i]',
        'input[placeholder*="Code" i]',
        'input[type="tel"]',
        'input[type="number"]'
    ]

    otp_input = None
    for selector in totp_input_selectors:
        try:
            elem = page.query_selector(selector)
            if elem and elem.is_visible():
                otp_input = selector
                break
        except Exception:
            continue

    if otp_input:
        print(f"  🔐 Rilevato campo codice 2FA ({otp_input}).")
        code = get_totp_code(credentials.get("totp_secret"))
        if code:
            print(f"  ⚡ Codice 2FA/TOTP calcolato automaticamente: {code}")
            try:
                page.fill(otp_input, code)
                # Prova a cliccare submit se presente
                submit_btn = page.query_selector('button[type="submit"]')
                if submit_btn:
                    submit_btn.click()
                time.sleep(3)
            except Exception as e:
                print(f"  ⚠️ Errore inserimento 2FA automatico: {e}")
        else:
            print("  ⚠️ Impossibile generare automaticamente il codice 2FA (WORLDFILIA_TOTP_SECRET non definita).")
            print("     Inserisci il codice manualmente nel browser o nel terminale.")

    return True


def main():
    profile_dir = get_browser_session_dir()
    credentials = get_credentials()

    is_headless = "--headless" in sys.argv

    print("=" * 60)
    print("WORLDFILIA - LOGIN & GESTIONE SESSIONE BROWSER (XDG + ENV)")
    print("=" * 60)
    print(f"Directory sessione persistente (XDG): {profile_dir}")
    print(f"Apertura del browser su: {LOGIN_URL}")
    print("-" * 60)

    if not credentials.get("username") or not credentials.get("password"):
        print("⚠️ Variabili WORLDFILIA_USERNAME e WORLDFILIA_PASSWORD non impostate!")
        print("💡 Esportale nel tuo ambiente prima di eseguire lo script.")
        print("-" * 60)

    context = launch_worldfilia_browser(headless=is_headless)
    page = context.pages[0] if context.pages else context.new_page()

    try:
        page.goto(LOGIN_URL, wait_until="domcontentloaded")
        time.sleep(3)

        # Se siamo già dentro la dashboard, la sessione è già valida!
        if "publisher" in page.url:
            print("\n🎉 Sei già autenticato su Worldfilia!")
            print(f"URL: {page.url}")
        else:
            # Tenta il login automatico con le credenziali d'ambiente
            attempted = attempt_automated_login(page, credentials)

            # Se non siamo in headless o se serve intervento manuale
            if not is_headless and "publisher" not in page.url:
                print("\n[ISTRUZIONI]")
                print("1. Se necessario, completa la verifica 2FA nel browser.")
                print("2. Una volta visualizzata la dashboard (/publisher), premi [INVIO] qui sotto.")
                print("-" * 60, flush=True)
                try:
                    input("\nIn attesa di conferma [INVIO]...")
                except (KeyboardInterrupt, EOFError):
                    print("\nInterruzione rilevata.", flush=True)

            # Verifica finale
            time.sleep(2)
            if "publisher" in page.url:
                print("\n✅ Accesso verificato con successo!")
            else:
                print(f"\n⚠️ URL finale: {page.url}")

    finally:
        print("\nChiusura del browser e salvataggio della sessione...")
        context.close()
        print("Sessione salvata con successo in:")
        print(f"  {profile_dir}")
        print("Gli script della skill possono ora operare in modalità headless con questa sessione.")


if __name__ == "__main__":
    main()

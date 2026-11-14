#!/usr/bin/env python3
"""
Script per il login interattivo su Amazon.it.
Apre una finestra di CloakBrowser (headless=False) per permettere all'utente di effettuare
l'accesso manualmente (comprese credenziali, 2FA, SMS, passkey o controlli di sicurezza).
La sessione e tutti i cookie vengono salvati in modo persistente nella directory XDG.
"""

import os
import select
import sys
import time
from pathlib import Path

CURRENT_DIR = Path(__file__).resolve().parent
if str(CURRENT_DIR) not in sys.path:
    sys.path.insert(0, str(CURRENT_DIR))

from browser import (
    AMAZON_BASE_URL,
    accept_cookies_if_present,
    check_amazon_login,
    launch_amazon_browser,
    save_session_state,
    take_screenshot,
)
from paths import get_browser_session_dir, get_storage_state_path


def main():
    profile_dir = get_browser_session_dir()
    state_file = get_storage_state_path()

    print("=" * 70)
    print("🛒 AMAZON BROWSER - LOGIN MANUALE & PERSISTENZA SESSIONE")
    print("=" * 70)
    print(f"📁 Directory profilo XDG:   {profile_dir}")
    print(f"💾 File stato autenticazione: {state_file}")
    print("-" * 70)
    print("Avvio del browser stealth (CloakBrowser) in corso...")

    try:
        context = launch_amazon_browser(headless=False)
    except Exception as e:
        print(f"\n❌ Errore durante l'avvio del browser: {e}")
        print("Assicurati di avere le dipendenze installate (cloakbrowser, playwright).")
        sys.exit(1)

    page = context.new_page()

    # Naviga direttamente alla pagina di sign-in di Amazon.it
    login_url = (
        f"{AMAZON_BASE_URL}/ap/signin?"
        "_encoding=UTF8&openid.assoc_handle=itflex&openid.claimed_id="
        "http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0%2Fidentifier_select&"
        "openid.identity=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0%2Fidentifier_select&"
        "openid.mode=checkid_setup&openid.ns=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0&"
        f"openid.return_to={AMAZON_BASE_URL}%2F%3Fref_%3Dnav_signin"
    )

    print(f"Navigazione su Amazon.it per autenticazione...")
    try:
        page.goto(login_url, wait_until="domcontentloaded", timeout=30000)
    except Exception as e:
        print(f"[AVVISO] Navigazione diretta alla signin non riuscita ({e}), vado alla homepage...")
        page.goto(AMAZON_BASE_URL, wait_until="domcontentloaded")

    # Gestisci eventuale cookie banner
    time.sleep(1)
    accept_cookies_if_present(page)

    print("\n" + "=" * 70)
    print("👉 ISTRUZIONI OPERATIVE:")
    print("1. Nella finestra del browser che si è appena aperta, effettua il login")
    print("   con le tue credenziali Amazon (e conferma eventuale OTP / 2FA / App).")
    print("2. Lo script rileverà automaticamente quando il login è andato a buon fine.")
    print("3. In alternativa, puoi premere [INVIO] qui nel terminale appena hai finito.")
    print("=" * 70 + "\n")

    auto_detected = False
    start_time = time.time()
    max_wait_seconds = 600  # 10 minuti di timeout massimo

    try:
        while time.time() - start_time < max_wait_seconds:
            # Controllo non bloccante su input utente da console
            rlist, _, _ = select.select([sys.stdin], [], [], 1.5)
            if rlist:
                sys.stdin.readline()
                print("\n[UTENTE] Ricevuto INVIO da console.")
                break

            try:
                current_url = page.url
                # Se non siamo più nella pagina di signin o ap/cvf/mfa
                if "signin" not in current_url and "openid" not in current_url and "ap/cvf" not in current_url:
                    status = check_amazon_login(page)
                    if status["is_logged_in"]:
                        print(f"\n✅ ACCESSO RILEVATO CON SUCCESSO! ({status['user_greeting']})")
                        auto_detected = True
                        print("Attendo 3 secondi per finalizzare la sincronizzazione dei cookie...")
                        time.sleep(3)
                        break
            except Exception:
                # La pagina potrebbe essere nel mezzo di un redirect
                pass

    except KeyboardInterrupt:
        print("\n[INTERRUZIONE] Operazione interrotta da tastiera.")

    # Verifica finale stato login
    try:
        accept_cookies_if_present(page)
        status = check_amazon_login(page)
        print("-" * 70)
        print(f"Stato autenticazione finale: {status['user_greeting']}")
        print(f"URL corrente: {page.url}")
    except Exception as e:
        print(f"[AVVISO] Errore verifica finale: {e}")

    # Salva storage state e screenshot di conferma
    print("\nSalvataggio sessione...")
    try:
        save_session_state(context)
        take_screenshot(page, "amazon_login_success.png")
    except Exception as e:
        print(f"[WARN] Errore esportazione stato: {e}")

    # Chiusura pulita del context persistente
    try:
        context.close()
        print("Browser chiuso correttamente.")
    except Exception as e:
        print(f"[WARN] Errore chiusura browser: {e}")

    print("\n" + "=" * 70)
    print("🎉 CONFIGURAZIONE SESSIONE COMPLETATA")
    print(f"La tua sessione Amazon è stata salvata in:")
    print(f"  📁 {profile_dir}")
    print(f"  💾 {state_file}")
    print("Gli script di automazione (search, ordini, carrello) utilizzeranno")
    print("automaticamente questa sessione anche in modalità headless!")
    print("=" * 70)


if __name__ == "__main__":
    main()

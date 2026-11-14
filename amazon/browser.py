"""
Modulo per l'avvio e la gestione del browser virtuale stealth (CloakBrowser) per Amazon.
Garantisce la persistenza del profilo browser e della sessione nella directory XDG.
"""

import sys
from pathlib import Path
from typing import Any, Dict, Optional

# Aggiunge la directory corrente al sys.path se eseguito come script isolato
CURRENT_DIR = Path(__file__).resolve().parent
if str(CURRENT_DIR) not in sys.path:
    sys.path.insert(0, str(CURRENT_DIR))

try:
    from cloakbrowser import launch_persistent_context
except ImportError:
    raise ImportError(
        "CloakBrowser non è installato nell'ambiente virtuale corrente. "
        "Installa CloakBrowser (es. con pip install cloakbrowser) o attiva l'ambiente ~/.venv."
    )

from paths import get_browser_session_dir, get_screenshots_dir, get_storage_state_path

AMAZON_BASE_URL = "https://www.amazon.it"


def cleanup_stale_locks(profile_dir: Path):
    """Rimuove eventuali lock orfani di Chromium se il processo precedente è terminato."""
    lock_file = profile_dir / "SingletonLock"
    if lock_file.is_symlink() or lock_file.exists():
        try:
            target = os.readlink(lock_file)
            pid_str = target.split("-")[-1]
            if pid_str.isdigit():
                pid = int(pid_str)
                try:
                    os.kill(pid, 0)
                    # Il processo è ancora vivo
                    return
                except OSError:
                    # Il processo non esiste più, possiamo rimuovere i lock
                    pass
            lock_file.unlink(missing_ok=True)
            (profile_dir / "SingletonCookie").unlink(missing_ok=True)
            (profile_dir / "SingletonSocket").unlink(missing_ok=True)
        except Exception:
            pass


def launch_amazon_browser(headless: bool = False, **kwargs: Any):
    """
    Avvia CloakBrowser riutilizzando la sessione persistente salvata in XDG_DATA_HOME/amazon/browser_session.

    Args:
        headless: Se True, avvia il browser in modalità invisibile. Di default False per interazioni/debug.
        **kwargs: Argomenti addizionali inoltrati a launch_persistent_context.

    Returns:
        Un'istanza di BrowserContext persistente di Playwright gestita da CloakBrowser.
    """
    profile_dir = get_browser_session_dir()
    cleanup_stale_locks(profile_dir)

    custom_args = kwargs.pop("args", None) or []
    default_args = [
        "--window-size=1280,850",
        "--window-position=60,40",
        "--disable-blink-features=AutomationControlled",
        "--lang=it-IT",
    ]
    for arg in default_args:
        prefix = arg.split("=")[0]
        if not any(a.startswith(prefix) for a in custom_args):
            custom_args.append(arg)

    # Su macOS CloakBrowser può forzare un viewport 1920x1080 che tronca la finestra se non adattato.
    # Impostando viewport=None il browser si adatta naturalmente alle dimensioni della finestra.
    if "viewport" not in kwargs:
        kwargs["viewport"] = None

    if "locale" not in kwargs:
        kwargs["locale"] = "it-IT"

    if "timezone" not in kwargs:
        kwargs["timezone"] = "Europe/Rome"

    context = launch_persistent_context(
        user_data_dir=profile_dir,
        headless=headless,
        stealth_args=True,
        args=custom_args,
        **kwargs,
    )
    return context


def accept_cookies_if_present(page, timeout_ms: int = 3000) -> bool:
    """
    Rileva e accetta il banner del consenso cookie di Amazon (GDPR) se presente a schermo.

    Returns:
        True se il banner è stato trovato e accettato, False altrimenti.
    """
    selectors = [
        "#sp-cc-accept",
        "input#sp-cc-accept",
        "input[name='acceptCookies']",
        "button[name='acceptCookies']",
        "#sp-cc-rejectall-link",  # alternativa
    ]
    for selector in selectors:
        try:
            btn = page.locator(selector).first
            if btn.is_visible(timeout=timeout_ms):
                btn.click()
                page.wait_for_timeout(800)
                return True
        except Exception:
            continue
    return False


def check_amazon_login(page) -> Dict[str, Any]:
    """
    Verifica se l'utente è attualmente autenticato su Amazon.

    Controlla il testo dell'header di benvenuto ("Ciao, <Nome>" vs "Ciao, accedi")
    ed elementi associati all'account utente.
    """
    try:
        greeting_elem = page.locator("#nav-link-accountList-nav-line-1").first
        if greeting_elem.is_visible(timeout=3000):
            text = greeting_elem.inner_text().strip()
            # In italiano non autenticato è tipicamente "Ciao, accedi" o "Hello, sign in"
            is_logged = not any(
                keyword in text.lower()
                for keyword in ["accedi", "sign in", "identificati", "login"]
            ) and len(text) > 0

            return {
                "is_logged_in": is_logged,
                "user_greeting": text,
                "details": f"Header di stato: '{text}'",
            }
    except Exception as e:
        pass

    # Controllo alternativo tramite presenza di link al signout
    try:
        signout_elem = page.locator("a[href*='sign-out'], #nav-item-signout").first
        if signout_elem.count() > 0:
            return {
                "is_logged_in": True,
                "user_greeting": "Utente loggato",
                "details": "Rilevato pulsante di disconnessione / profilo attivo",
            }
    except Exception:
        pass

    return {
        "is_logged_in": False,
        "user_greeting": "Non autenticato",
        "details": "Nessun indicatore di sessione attiva trovato",
    }


def save_session_state(context) -> Path:
    """
    Esporta e salva lo stato di autenticazione e i cookie correnti nel file JSON XDG.
    """
    state_path = get_storage_state_path()
    try:
        context.storage_state(path=str(state_path))
    except Exception as e:
        print(f"[WARN] Impossibile salvare storage_state.json: {e}")
    return state_path


def take_screenshot(page, filename: str = "amazon_debug.png") -> Path:
    """
    Cattura uno screenshot della pagina corrente e lo salva nella directory di cache XDG.
    """
    screenshots_dir = get_screenshots_dir()
    filepath = screenshots_dir / filename
    try:
        page.screenshot(path=str(filepath), full_page=False)
        print(f"[SCREENSHOT] Salvato in: {filepath}")
    except Exception as e:
        print(f"[WARN] Errore salvataggio screenshot: {e}")
    return filepath

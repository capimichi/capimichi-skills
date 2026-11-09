import os
import subprocess
from pathlib import Path

TARGET_HOME = Path.home() if Path.home().exists() else Path("/Users/michele")

def get_home_dir() -> Path:
    """Restituisce la home directory dell'utente."""
    return TARGET_HOME

def get_data_dir() -> Path:
    """Restituisce la directory base dei dati secondo XDG_DATA_HOME (default: ~/.local/share/worldfilia)."""
    xdg_data = os.environ.get("WORLDFILIA_DATA_DIR") or os.environ.get("XDG_DATA_HOME")
    base = Path(xdg_data) if xdg_data else get_home_dir() / ".local" / "share"
    path = base / "worldfilia"
    path.mkdir(parents=True, exist_ok=True)
    return path

def get_browser_session_dir() -> Path:
    """Restituisce la directory per la sessione persistente del browser CloakBrowser."""
    path = get_data_dir() / "browser_session"
    path.mkdir(parents=True, exist_ok=True)
    return path

def get_cache_dir() -> Path:
    """Restituisce la directory di cache secondo XDG_CACHE_HOME (default: ~/.cache/worldfilia)."""
    xdg_cache = os.environ.get("XDG_CACHE_HOME")
    base = Path(xdg_cache) if xdg_cache else get_home_dir() / ".cache"
    path = base / "worldfilia"
    path.mkdir(parents=True, exist_ok=True)
    return path

def get_credentials() -> dict:
    """
    Recupera le credenziali Worldfilia dalle variabili d'ambiente:
    WORLDFILIA_USERNAME, WORLDFILIA_PASSWORD, WORLDFILIA_API_KEY, WORLDFILIA_TOTP_SECRET.
    """
    username = os.environ.get("WORLDFILIA_USERNAME") or os.environ.get("WORLDFILIA_EMAIL") or ""
    password = os.environ.get("WORLDFILIA_PASSWORD") or ""
    totp_secret = os.environ.get("WORLDFILIA_TOTP_SECRET") or os.environ.get("WORLDFILIA_2FA_SECRET") or ""
    api_key = os.environ.get("WORLDFILIA_API_KEY") or os.environ.get("WORLDFILIA_TOKEN") or ""
    return {
        "username": username,
        "password": password,
        "totp_secret": totp_secret,
        "api_key": api_key,
    }

def get_totp_code(secret: str | None = None) -> str | None:
    """
    Genera il codice 2FA (TOTP a 6 cifre) usando la chiave segreta presente in WORLDFILIA_TOTP_SECRET tramite pyotp.
    """
    sec = secret or os.environ.get("WORLDFILIA_TOTP_SECRET") or os.environ.get("WORLDFILIA_2FA_SECRET")
    if sec:
        try:
            import pyotp
            try:
                totp = pyotp.parse_uri(sec.strip())
            except Exception:
                totp = pyotp.TOTP(sec.strip())
            code = totp.now()
            if code and len(code) == 6:
                return code
        except Exception as e:
            print(f"[AUTH] Errore calcolo TOTP da secret con pyotp: {e}")

    return None


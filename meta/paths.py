import os
from pathlib import Path

TARGET_HOME = Path("/Users/michele")

def get_home_dir() -> Path:
    """Restituisce la home directory dell'utente (/Users/michele)."""
    return TARGET_HOME

def get_data_dir() -> Path:
    """Restituisce la directory base dei dati secondo XDG_DATA_HOME (default: /Users/michele/.local/share/meta)."""
    xdg_data = os.environ.get("META_DATA_DIR")
    base = Path(xdg_data) if xdg_data else get_home_dir() / ".local" / "share"
    path = base / "meta"
    path.mkdir(parents=True, exist_ok=True)
    return path

def get_browser_session_dir() -> Path:
    """Restituisce la directory per la sessione persistente del browser CloakBrowser."""
    path = get_data_dir() / "browser_session"
    path.mkdir(parents=True, exist_ok=True)
    return path

def get_cache_dir() -> Path:
    """Restituisce la directory di cache secondo XDG_CACHE_HOME (default: /Users/michele/.cache/meta)."""
    xdg_cache = os.environ.get("XDG_CACHE_HOME")
    base = Path(xdg_cache) if xdg_cache else get_home_dir() / ".cache"
    path = base / "meta"
    path.mkdir(parents=True, exist_ok=True)
    return path

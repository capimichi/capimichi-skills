import os
from pathlib import Path


def get_home_dir() -> Path:
    """Restituisce la home directory dell'utente risolta dinamicamente."""
    home_env = os.environ.get("USER_HOME") or os.environ.get("HOME")
    if home_env:
        return Path(home_env)
    return Path.home()


def get_data_dir() -> Path:
    """Restituisce la directory base dei dati secondo XDG_DATA_HOME (default: ~/.local/share/meta)."""
    xdg_data = os.environ.get("META_DATA_DIR") or os.environ.get("XDG_DATA_HOME")
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
    """Restituisce la directory di cache secondo XDG_CACHE_HOME (default: ~/.cache/meta)."""
    xdg_cache = os.environ.get("XDG_CACHE_HOME")
    base = Path(xdg_cache) if xdg_cache else get_home_dir() / ".cache"
    path = base / "meta"
    path.mkdir(parents=True, exist_ok=True)
    return path

"""
Gestione dei percorsi e conformità alle specifiche XDG Base Directory per Amazon Automation.
"""

import os
from pathlib import Path

def get_home_dir() -> Path:
    """Restituisce la home directory dell'utente risolta dinamicamente."""
    home_env = os.environ.get("USER_HOME") or os.environ.get("HOME")
    if home_env:
        return Path(home_env)
    return Path.home()


def get_data_dir() -> Path:
    """
    Restituisce la directory base dei dati secondo le specifiche XDG Base Directory.
    Priorità: AMAZON_DATA_DIR -> XDG_DATA_HOME/amazon -> ~/.local/share/amazon.
    """
    override = os.environ.get("AMAZON_DATA_DIR")
    if override:
        path = Path(override)
    else:
        xdg_data = os.environ.get("XDG_DATA_HOME")
        base = Path(xdg_data) if xdg_data else get_home_dir() / ".local" / "share"
        path = base / "amazon"

    path.mkdir(parents=True, exist_ok=True)
    return path


def get_browser_session_dir() -> Path:
    """
    Restituisce la directory per la sessione persistente del browser (CloakBrowser / Chromium).
    Mantiene cookie, localStorage, IndexedDB e sessione di login.
    Priorità: AMAZON_BROWSER_PROFILE -> get_data_dir() / "browser_session".
    """
    override = os.environ.get("AMAZON_BROWSER_PROFILE")
    if override:
        path = Path(override)
    else:
        path = get_data_dir() / "browser_session"

    path.mkdir(parents=True, exist_ok=True)
    return path


def get_storage_state_path() -> Path:
    """
    Restituisce il percorso del file JSON con lo stato di autenticazione e cookie esportati.
    Utile per caricamenti veloci e condivisione contesti.
    """
    return get_data_dir() / "storage_state.json"


def get_config_dir() -> Path:
    """
    Restituisce la directory di configurazione secondo XDG_CONFIG_HOME.
    Default: ~/.config/amazon.
    """
    xdg_config = os.environ.get("XDG_CONFIG_HOME")
    base = Path(xdg_config) if xdg_config else get_home_dir() / ".config"
    path = base / "amazon"
    path.mkdir(parents=True, exist_ok=True)
    return path


def get_cache_dir() -> Path:
    """
    Restituisce la directory di cache secondo XDG_CACHE_HOME.
    Default: ~/.cache/amazon.
    """
    xdg_cache = os.environ.get("XDG_CACHE_HOME")
    base = Path(xdg_cache) if xdg_cache else get_home_dir() / ".cache"
    path = base / "amazon"
    path.mkdir(parents=True, exist_ok=True)
    return path


def get_screenshots_dir() -> Path:
    """
    Restituisce la directory per il salvataggio di screenshot di debug o ispezione.
    Default: ~/.cache/amazon/screenshots.
    """
    path = get_cache_dir() / "screenshots"
    path.mkdir(parents=True, exist_ok=True)
    return path

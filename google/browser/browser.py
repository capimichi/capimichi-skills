#!/usr/bin/env python3
"""
Google & Generic Web CloakBrowser Engine.
Gestisce l'avvio del browser persistente stealth, la gestione dei cookie e i percorsi XDG.
"""

import os
import sys
import time
from pathlib import Path
from typing import Any, Optional


def get_home_dir() -> Path:
    """Restituisce la home directory dell'utente risolta dinamicamente."""
    home_env = os.environ.get("USER_HOME") or os.environ.get("HOME")
    if home_env:
        return Path(home_env)
    return Path.home()


def get_profile_dir() -> Path:
    """Restituisce la directory del profilo persistente secondo lo standard XDG."""
    xdg_data = os.environ.get("XDG_DATA_HOME")
    base = Path(xdg_data) if xdg_data else get_home_dir() / ".local" / "share"
    profile_dir = base / "browser-profiles" / "google"
    profile_dir.mkdir(parents=True, exist_ok=True)
    return profile_dir


def get_cache_dir() -> Path:
    """Restituisce la directory di cache e screenshot secondo lo standard XDG."""
    xdg_cache = os.environ.get("XDG_CACHE_HOME")
    base = Path(xdg_cache) if xdg_cache else get_home_dir() / ".cache"
    cache_dir = base / "google-browser"
    cache_dir.mkdir(parents=True, exist_ok=True)
    return cache_dir


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
                    return  # Il processo è ancora in esecuzione
                except OSError:
                    pass  # Processo terminato, sblocca
            lock_file.unlink(missing_ok=True)
            (profile_dir / "SingletonCookie").unlink(missing_ok=True)
            (profile_dir / "SingletonSocket").unlink(missing_ok=True)
        except Exception:
            pass


def launch_browser(headless: bool = True, **kwargs: Any):
    """
    Avvia CloakBrowser riutilizzando la sessione persistente salvata in ~/.local/share/browser-profiles/google.
    """
    try:
        from cloakbrowser import launch_persistent_context
    except ImportError:
        sys.exit(
            "Errore: modulo 'cloakbrowser' non trovato. "
            "Installa CloakBrowser eseguendo: pip install cloakbrowser"
        )

    profile_dir = get_profile_dir()
    cleanup_stale_locks(profile_dir)

    custom_args = kwargs.pop("args", None) or []
    default_args = [
        "--window-size=1280,850",
        "--window-position=60,40",
        "--lang=it-IT",
    ]
    for arg in default_args:
        prefix = arg.split("=")[0]
        if not any(a.startswith(prefix) for a in custom_args):
            custom_args.append(arg)

    # Su macOS viewport=None adatta la visualizzazione alle reali dimensioni della finestra
    if "viewport" not in kwargs:
        kwargs["viewport"] = None

    context = launch_persistent_context(
        user_data_dir=str(profile_dir),
        headless=headless,
        stealth_args=True,
        args=custom_args,
        **kwargs
    )
    return context


def accept_google_cookies(page) -> bool:
    """Rileva e accetta il banner del consenso cookie di Google se presente."""
    try:
        # Selettori standard di Google per il pulsante 'Accetta tutto'
        selectors = [
            "#L2AGLb",  # Bottone principale 'Accetta tutto' su google.it / google.com
            "button:has-text('Accetta tutto')",
            "button:has-text('Accept all')",
            "button:has-text('Accetto')",
            "button:has-text('I agree')",
            "form[action*='consent'] button",
            "[aria-modal='true'] button:last-child"
        ]
        for sel in selectors:
            btn = page.locator(sel)
            if btn.count() > 0 and btn.first.is_visible():
                btn.first.click()
                page.wait_for_timeout(1000)
                return True
    except Exception:
        pass
    return False

import os
from pathlib import Path
from typing import Any
from cloakbrowser import launch_persistent_context
from worldfilia.paths import get_browser_session_dir

def launch_worldfilia_browser(headless: bool = False, **kwargs: Any):
    """
    Avvia CloakBrowser riutilizzando la sessione persistente salvata in XDG_DATA_HOME/worldfilia/browser_session.
    Configura dimensioni finestra e viewport responsive per adattarsi allo schermo.
    """
    profile_dir = str(get_browser_session_dir())

    custom_args = kwargs.pop("args", None) or []
    default_args = ["--window-size=1240,800", "--window-position=50,30"]
    for arg in default_args:
        prefix = arg.split("=")[0]
        if not any(a.startswith(prefix) for a in custom_args):
            custom_args.append(arg)

    # CloakBrowser di default forza un viewport virtuale 1920x1080 che su Mac tronca la visualizzazione.
    # Passando viewport=None diciamo a CloakBrowser di usare la reale dimensione della finestra dell'OS!
    if "viewport" not in kwargs:
        kwargs["viewport"] = None

    return launch_persistent_context(
        user_data_dir=profile_dir,
        headless=headless,
        stealth_args=True,
        args=custom_args,
        **kwargs
    )


"""
Amazon Virtual Browser Automation Skill.
Conforme alle specifiche XDG per la persistenza della sessione e dei dati browser.
"""

from .browser import (
    AMAZON_BASE_URL,
    accept_cookies_if_present,
    check_amazon_login,
    launch_amazon_browser,
    save_session_state,
    take_screenshot,
)
from .paths import (
    get_browser_session_dir,
    get_cache_dir,
    get_config_dir,
    get_data_dir,
    get_screenshots_dir,
    get_storage_state_path,
)

__all__ = [
    "AMAZON_BASE_URL",
    "launch_amazon_browser",
    "check_amazon_login",
    "accept_cookies_if_present",
    "save_session_state",
    "take_screenshot",
    "get_data_dir",
    "get_browser_session_dir",
    "get_storage_state_path",
    "get_config_dir",
    "get_cache_dir",
    "get_screenshots_dir",
]

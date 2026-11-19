#!/usr/bin/env python3
"""
Monochrome.tf Client Helper with CloakBrowser.
"""

import os
import sys
import time
import json
from pathlib import Path

BASE_URL = "https://monochrome.tf"


def get_profile_dir() -> str:
    xdg_data = os.environ.get("XDG_DATA_HOME") or os.path.expanduser("~/.local/share")
    return os.path.join(xdg_data, "browser-profiles", "monochrome")


def configure_download_prefs(profile_dir: str, dest_dir: str):
    pref_path = os.path.join(profile_dir, "Default", "Preferences")
    os.makedirs(os.path.dirname(pref_path), exist_ok=True)

    prefs = {}
    if os.path.exists(pref_path):
        try:
            with open(pref_path, "r", encoding="utf-8") as f:
                prefs = json.load(f)
        except Exception:
            pass

    if "download" not in prefs:
        prefs["download"] = {}

    prefs["download"]["prompt_for_download"] = False
    prefs["download"]["directory_upgrade"] = True
    prefs["download"]["default_directory"] = dest_dir

    try:
        with open(pref_path, "w", encoding="utf-8") as f:
            json.dump(prefs, f, indent=4)
    except Exception:
        pass


def search_albums(query: str, headless: bool = False) -> list:
    try:
        from cloakbrowser import launch_persistent_context
    except ImportError:
        sys.exit("Errore: modulo 'cloakbrowser' non trovato. Esegui: pip install cloakbrowser")

    profile_dir = get_profile_dir()
    context = launch_persistent_context(profile_dir, headless=headless)
    page = context.new_page()
    page.set_viewport_size({"width": 1280, "height": 800})

    results = []
    try:
        page.goto(BASE_URL)
        page.wait_for_timeout(4000)

        search_input = page.locator("#search-input")
        search_input.wait_for(state="visible", timeout=10000)
        search_input.fill(query)
        search_input.press("Enter")
        page.wait_for_timeout(2500)

        albums_tab = page.locator('button[data-tab="albums"]').first
        if albums_tab.count() > 0:
            albums_tab.click()
            page.wait_for_timeout(2500)

        cards = page.locator("#search-albums-container .card")
        count = cards.count()
        for i in range(count):
            card = cards.nth(i)
            title_el = card.locator(".title, h3, h4, .album-title").first
            artist_el = card.locator(".artist, .subtitle, p").first
            link_el = card.locator("a[href*='/album/']").first

            title = title_el.inner_text().strip() if title_el.count() > 0 else ""
            artist = artist_el.inner_text().strip() if artist_el.count() > 0 else ""
            href = link_el.get_attribute("href") if link_el.count() > 0 else ""

            if not title and not href:
                continue

            full_url = f"{BASE_URL}{href}" if href.startswith("/") else href
            album_id = href.rstrip("/").split("/")[-1] if href else ""

            results.append({
                "id": album_id,
                "title": title,
                "artist": artist,
                "url": full_url
            })
    finally:
        context.close()

    return results


def download_album(album_url_or_id: str, output_dir: str = "~/Downloads", headless: bool = False, timeout_sec: int = 180) -> str:
    try:
        from cloakbrowser import launch_persistent_context
    except ImportError:
        sys.exit("Errore: modulo 'cloakbrowser' non trovato. Esegui: pip install cloakbrowser")

    dest_dir = os.path.expanduser(output_dir)
    os.makedirs(dest_dir, exist_ok=True)

    profile_dir = get_profile_dir()
    configure_download_prefs(profile_dir, dest_dir)

    target_url = album_url_or_id if album_url_or_id.startswith("http") else f"{BASE_URL}/album/{album_url_or_id}"

    context = launch_persistent_context(profile_dir, headless=headless)
    page = context.new_page()
    page.set_viewport_size({"width": 1280, "height": 800})

    downloads = []
    page.on("download", lambda d: downloads.append(d))

    def handle_dialog(dialog):
        val = dialog.default_value if dialog.default_value else "album"
        dialog.accept(val)

    page.on("dialog", handle_dialog)

    saved_file = None
    try:
        page.goto(target_url)
        page.wait_for_timeout(5000)

        download_btn = page.locator("#download-album-btn")
        if download_btn.count() == 0:
            raise RuntimeError("Pulsante #download-album-btn non trovato nella pagina.")

        download_btn.click()

        start_time = time.time()
        while time.time() - start_time < timeout_sec:
            page.wait_for_timeout(1000)
            if downloads:
                dl = downloads[0]
                dest_path = os.path.join(dest_dir, dl.suggested_filename)
                dl.save_as(dest_path)
                saved_file = dest_path
                break
    finally:
        context.close()

    if not saved_file:
        raise TimeoutError(f"Timeout di {timeout_sec}s superato senza avvio del download.")

    return saved_file

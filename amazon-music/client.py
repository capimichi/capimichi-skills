#!/usr/bin/env python3
"""
Amazon Music Client Helper with CloakBrowser.
"""

import os
import sys
from pathlib import Path

def get_profile_dir() -> str:
    xdg_data = os.environ.get("XDG_DATA_HOME") or os.path.expanduser("~/.local/share")
    return os.path.join(xdg_data, "browser-profiles", "amazon-music")


def launch_context(headless: bool = True):
    try:
        from cloakbrowser import launch_persistent_context
    except ImportError:
        sys.exit("Errore: modulo 'cloakbrowser' non trovato. Installa le dipendenze richieste eseguendo: pip install cloakbrowser")

    profile_dir = get_profile_dir()
    os.makedirs(profile_dir, exist_ok=True)
    return launch_persistent_context(profile_dir, headless=headless)


def login_manual():
    profile_dir = get_profile_dir()
    print(f"Avvio del browser con il profilo in: {profile_dir}")
    context = launch_context(headless=False)
    page = context.new_page()

    print("Navigazione su https://music.amazon.it/...")
    page.goto("https://music.amazon.it/")

    print("\n[ATTENZIONE] Effettua il login nella finestra del browser che si è aperta.")
    print("Una volta effettuato l'accesso con successo, premi INVIO qui per chiudere e salvare la sessione.")
    sys.stdin.read(1)
    print("Chiusura del browser e salvataggio della sessione...")
    context.close()


def search_music(query: str, headless: bool = True) -> list:
    context = launch_context(headless=headless)
    page = context.new_page()
    page.set_viewport_size({"width": 1280, "height": 800})

    results = []
    try:
        page.goto("https://music.amazon.it/")
        page.wait_for_timeout(6000)

        search_input = page.locator("#navbarSearchInput")
        try:
            search_input.wait_for(state="visible", timeout=15000)
        except Exception:
            pass

        search_input.focus()
        search_input.fill(query)
        search_input.press("Enter")
        page.wait_for_timeout(5000)

        shovelers = page.query_selector_all("music-shoveler")
        for shoveler in shovelers:
            shoveler_type = shoveler.get_attribute("primary-text") or ""

            h_items = shoveler.query_selector_all("music-horizontal-item")
            for item in h_items:
                title = item.get_attribute("primary-text") or ""
                artist = item.get_attribute("secondary-text") or ""
                href = item.get_attribute("primary-href") or ""
                full_url = f"https://music.amazon.it{href}" if href else ""
                results.append({
                    "type": "horizontal",
                    "section": shoveler_type,
                    "title": title,
                    "artist": artist,
                    "url": full_url
                })

            v_items = shoveler.query_selector_all("music-vertical-item")
            for item in v_items:
                title = item.get_attribute("primary-text") or ""
                artist = item.get_attribute("secondary-text") or ""
                href = item.get_attribute("primary-href") or ""
                full_url = f"https://music.amazon.it{href}" if href else ""
                results.append({
                    "type": "vertical",
                    "section": shoveler_type,
                    "title": title,
                    "artist": artist,
                    "url": full_url
                })
    finally:
        context.close()

    return results


def inspect_album_tracks(album_url: str, headless: bool = True) -> list:
    context = launch_context(headless=headless)
    page = context.new_page()
    page.set_viewport_size({"width": 1280, "height": 800})

    tracks = []
    try:
        page.goto(album_url)
        page.wait_for_timeout(6000)

        all_music_elements = page.query_selector_all("music-image-row, music-horizontal-item")
        for el in all_music_elements:
            title = el.get_attribute("primary-text") or ""
            artist = el.get_attribute("secondary-text") or ""
            href = el.get_attribute("primary-href") or ""
            if href and ("trackAsin" in href or "/tracks/" in href):
                tracks.append({
                    "title": title,
                    "artist": artist,
                    "url": f"https://music.amazon.it{href}" if href.startswith("/") else href
                })
    finally:
        context.close()

    return tracks

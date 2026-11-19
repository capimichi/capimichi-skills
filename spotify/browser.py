#!/usr/bin/env python3
"""
Spotify Web Scraper / Browser Automation via CloakBrowser.
"""

import os
import sys

try:
    from cloakbrowser import launch_persistent_context
except ImportError:
    sys.exit(
        "Errore: modulo 'cloakbrowser' non trovato. "
        "Verifica che cloakbrowser sia installato nel tuo ambiente Python."
    )


def search_spotify(query: str, headless: bool = True):
    print(f"Esecuzione ricerca pubblica su Spotify per: '{query}'...")
    url = f"https://open.spotify.com/search/{query.replace(' ', '%20')}"

    xdg_data = os.environ.get("XDG_DATA_HOME") or os.path.expanduser("~/.local/share")
    profile_dir = os.path.join(xdg_data, "browser-profiles", "spotify")

    context = launch_persistent_context(profile_dir, headless=headless)
    try:
        page = context.new_page()
        page.set_viewport_size({"width": 1280, "height": 800})

        page.goto(url)
        print("Pagina caricata. Attesa caricamento dei risultati (5s)...")
        page.wait_for_timeout(5000)

        # Screenshot di verifica in cache
        xdg_cache = os.environ.get("XDG_CACHE_HOME") or os.path.expanduser("~/.cache")
        artifact_dir = os.environ.get("ARTIFACT_DIR") or os.path.join(xdg_cache, "spotify")
        os.makedirs(artifact_dir, exist_ok=True)
        screenshot_path = os.path.join(artifact_dir, "spotify_search_result.png")
        page.screenshot(path=screenshot_path)
        print(f"Screenshot salvato in: {screenshot_path}\n")

        results = {
            "top_result": None,
            "tracks": [],
            "albums": [],
            "artists": []
        }

        # 1. RISULTATO PIÙ RILEVANTE
        top_card = page.locator("[data-testid='top-result-card']")
        if top_card.count() > 0:
            card_text = top_card.first.inner_text().strip().split("\n")
            card_link = top_card.locator("a").first
            href = card_link.get_attribute("href") if card_link.count() > 0 else ""
            results["top_result"] = {
                "text": " | ".join(card_text),
                "url": f"https://open.spotify.com{href}" if href else ""
            }

        # 2. BRANI TROVATI
        rows = page.locator("[role='row']").all()
        for row in rows:
            track_el = row.locator("a[href*='/track/']")
            if track_el.count() > 0:
                title = track_el.first.inner_text().strip()
                href = track_el.first.get_attribute("href") or ""
                artist_els = row.locator("a[href*='/artist/']").all()
                artists = [a.inner_text().strip() for a in artist_els]

                duration = "N/D"
                row_text_parts = row.inner_text().strip().split("\n")
                for part in row_text_parts:
                    part_s = part.strip()
                    if ":" in part_s and len(part_s) <= 5 and part_s.replace(":", "").isdigit():
                        duration = part_s
                        break

                results["tracks"].append({
                    "title": title,
                    "artists": artists,
                    "duration": duration,
                    "url": f"https://open.spotify.com{href}"
                })

        # 3. ALBUM TROVATI
        seen_albums = set()
        album_links = page.locator("a[href*='/album/']").all()
        for link in album_links:
            href = link.get_attribute("href") or ""
            clean_href = href.split("?")[0]
            if clean_href not in seen_albums:
                seen_albums.add(clean_href)
                text_lines = [line.strip() for line in link.inner_text().strip().split("\n") if line.strip()]
                if text_lines:
                    results["albums"].append({
                        "name": " - ".join(text_lines),
                        "url": f"https://open.spotify.com{clean_href}"
                    })

        # 4. ARTISTI TROVATI
        seen_artists = set()
        artist_links = page.locator("a[href*='/artist/']").all()
        for link in artist_links:
            href = link.get_attribute("href") or ""
            clean_href = href.split("?")[0]
            if clean_href not in seen_artists:
                seen_artists.add(clean_href)
                text_lines = [line.strip() for line in link.inner_text().strip().split("\n") if line.strip() and line.strip() != "Artista"]
                if text_lines:
                    results["artists"].append({
                        "name": " - ".join(text_lines),
                        "url": f"https://open.spotify.com{clean_href}"
                    })

        return results

    finally:
        context.close()
        print("Connessione browser chiusa.")

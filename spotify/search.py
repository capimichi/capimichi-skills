import os
import sys
from cloakbrowser import launch_persistent_context

def main():
    query = "Sergio Mendes Funky Bahia"
    if len(sys.argv) > 1:
        query = " ".join(sys.argv[1:])
        
    print(f"Esecuzione ricerca pubblica su Spotify per: '{query}'...")
    url = f"https://open.spotify.com/search/{query.replace(' ', '%20')}"
    
    profile_dir = os.path.join(os.environ.get('XDG_DATA_HOME', os.path.expanduser('~/.local/share')), 'browser-profiles', 'spotify')
    context = launch_persistent_context(profile_dir, headless=True)
    try:
        page = context.new_page()
        page.set_viewport_size({"width": 1280, "height": 800})
        
        page.goto(url)
        print("Pagina caricata. Attesa caricamento dei risultati (5s)...")
        page.wait_for_timeout(5000)
        
        # Screenshot di verifica
        artifact_dir = os.environ.get("ARTIFACT_DIR") or os.path.expanduser("~/.cache/spotify")
        os.makedirs(artifact_dir, exist_ok=True)
        screenshot_path = os.path.join(artifact_dir, "spotify_search_result.png")
        page.screenshot(path=screenshot_path)
        print(f"Screenshot salvato in: {screenshot_path}\n")
        
        # 1. RISULTATO PIÙ RILEVANTE (Top Result Card)
        print("=== RISULTATO PIÙ RILEVANTE ===")
        top_card = page.locator("[data-testid='top-result-card']")
        if top_card.count() > 0:
            card_text = top_card.first.inner_text().strip().split("\n")
            # Troviamo il link all'interno della top card
            card_link = top_card.locator("a").first
            href = card_link.get_attribute("href") if card_link.count() > 0 else "N/D"
            print("  Testo:", " | ".join(card_text))
            print(f"  Link: https://open.spotify.com{href}")
        else:
            print("  Nessun risultato rilevante in evidenza.")
        print("-" * 50)
        
        # 2. BRANI TROVATI
        print("\n=== BRANI TROVATI ===")
        rows = page.locator("[role='row']").all()
        track_count = 0
        for row in rows:
            track_el = row.locator("a[href*='/track/']")
            if track_el.count() > 0:
                track_count += 1
                title = track_el.first.inner_text().strip()
                href = track_el.first.get_attribute("href")
                
                # Artisti
                artist_els = row.locator("a[href*='/artist/']").all()
                artists = [a.inner_text().strip() for a in artist_els]
                
                # Durata (cerchiamo elementi di testo che contengono ":" come "3:45")
                duration = "N/D"
                row_text_parts = row.inner_text().strip().split("\n")
                for part in row_text_parts:
                    part_s = part.strip()
                    if ":" in part_s and len(part_s) <= 5 and part_s.replace(":", "").isdigit():
                        duration = part_s
                        break
                        
                print(f"[{track_count}] {title}")
                print(f"    Artisti: {', '.join(artists)}")
                print(f"    Durata: {duration}")
                print(f"    Link: https://open.spotify.com{href}")
                print("    " + "." * 30)
        if track_count == 0:
            print("  Nessun brano trovato.")
        print("-" * 50)
        
        # 3. ALBUM TROVATI
        print("\n=== ALBUM TROVATI ===")
        seen_albums = set()
        album_links = page.locator("a[href*='/album/']").all()
        album_count = 0
        for link in album_links:
            href = link.get_attribute("href")
            clean_href = href.split("?")[0]
            if clean_href not in seen_albums:
                seen_albums.add(clean_href)
                # Otteniamo il testo, rimuovendo "Album" o duplicati dal testo del link
                text_lines = [line.strip() for line in link.inner_text().strip().split("\n") if line.strip()]
                if text_lines:
                    album_count += 1
                    print(f"[{album_count}] {' - '.join(text_lines)} -> https://open.spotify.com{clean_href}")
        if album_count == 0:
            print("  Nessun album trovato.")
        print("-" * 50)
        
        # 4. ARTISTI TROVATI
        print("\n=== ARTISTI TROVATI ===")
        seen_artists = set()
        artist_links = page.locator("a[href*='/artist/']").all()
        artist_count = 0
        for link in artist_links:
            href = link.get_attribute("href")
            clean_href = href.split("?")[0]
            if clean_href not in seen_artists:
                seen_artists.add(clean_href)
                text_lines = [line.strip() for line in link.inner_text().strip().split("\n") if line.strip() and line.strip() != "Artista"]
                if text_lines:
                    artist_count += 1
                    print(f"[{artist_count}] {' - '.join(text_lines)} -> https://open.spotify.com{clean_href}")
        if artist_count == 0:
            print("  Nessun artista trovato.")
        print("-" * 50)
        
    except Exception as e:
        print(f"Si è verificato un errore durante la ricerca: {e}")
    finally:
        context.close()
        print("Connessione chiusa.")

if __name__ == "__main__":
    main()

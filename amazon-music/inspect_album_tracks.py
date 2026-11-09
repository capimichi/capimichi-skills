import os
import sys
from cloakbrowser import launch_persistent_context

def inspect_album_tracks(album_url):
    profile_dir = os.path.join(os.environ.get('XDG_DATA_HOME', os.path.expanduser('~/.local/share')), 'browser-profiles', 'amazon-music')
    context = launch_persistent_context(profile_dir, headless=False)
    page = context.new_page()
    page.set_viewport_size({"width": 1280, "height": 800})
    
    print(f"Apertura pagina album: {album_url}")
    page.goto(album_url)
    page.wait_for_timeout(6000)
    
    # Cerchiamo tutti i track items nella pagina dell'album
    items = page.query_selector_all("music-image-row, music-horizontal-item, music-list-item, music-text-row")
    print(f"Trovati {len(items)} elementi totali. Ispezione:")
    
    tracks = []
    # In una pagina album di Amazon Music, le tracce sono spesso dentro music-image-row o music-horizontal-item o simili
    all_music_elements = page.query_selector_all("music-image-row, music-horizontal-item")
    for el in all_music_elements:
        title = el.get_attribute("primary-text") or ""
        artist = el.get_attribute("secondary-text") or ""
        href = el.get_attribute("primary-href") or ""
        if href and ("trackAsin" in href or "/tracks/" in href):
            tracks.append({"title": title, "artist": artist, "href": href})
            
    print(f"Tracce estratte con link/ASIN: {len(tracks)}")
    for i, t in enumerate(tracks[:10], 1):
        print(f"  {i}. {t['title']} ({t['artist']}) -> {t['href']}")
        
    context.close()
    return tracks

if __name__ == "__main__":
    url = sys.argv[1] if len(sys.argv) > 1 else "https://music.amazon.it/albums/B01F2UC01E"
    inspect_album_tracks(url)

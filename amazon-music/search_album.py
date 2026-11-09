import os
import sys
from cloakbrowser import launch_persistent_context

def search_album(query):
    profile_dir = os.path.join(os.environ.get('XDG_DATA_HOME', os.path.expanduser('~/.local/share')), 'browser-profiles', 'amazon-music')
    print(f"Caricamento sessione browser da: {profile_dir}")
    
    context = launch_persistent_context(profile_dir, headless=False)
    page = context.new_page()
    page.set_viewport_size({"width": 1280, "height": 800})
    
    print("Navigazione su https://music.amazon.it/...")
    page.goto("https://music.amazon.it/")
    page.wait_for_timeout(6000)
    
    print(f"Esecuzione ricerca per: '{query}'...")
    search_input = page.locator("#navbarSearchInput")
    try:
        search_input.wait_for(state="visible", timeout=15000)
    except Exception:
        print("Campo di ricerca non trovato direttamente, attendo...")
    
    search_input.focus()
    search_input.fill(query)
    search_input.press("Enter")
    
    print("In attesa dei risultati (5s)...")
    page.wait_for_timeout(5000)
    
    # Parsing risultati
    results = []
    shovelers = page.query_selector_all("music-shoveler")
    for shoveler in shovelers:
        shoveler_type = shoveler.get_attribute("primary-text") or ""
        
        h_items = shoveler.query_selector_all("music-horizontal-item")
        for item in h_items:
            title = item.get_attribute("primary-text") or ""
            artist = item.get_attribute("secondary-text") or ""
            href = item.get_attribute("primary-href") or ""
            full_url = f"https://music.amazon.it{href}" if href else ""
            results.append({"type": "horizontal", "section": shoveler_type, "title": title, "artist": artist, "url": full_url})
            
        v_items = shoveler.query_selector_all("music-vertical-item")
        for item in v_items:
            title = item.get_attribute("primary-text") or ""
            artist = item.get_attribute("secondary-text") or ""
            href = item.get_attribute("primary-href") or ""
            full_url = f"https://music.amazon.it{href}" if href else ""
            results.append({"type": "vertical", "section": shoveler_type, "title": title, "artist": artist, "url": full_url})
            
    context.close()
    return results

if __name__ == "__main__":
    query = sys.argv[1] if len(sys.argv) > 1 else "Articolo 31 J-Ax & Friends"
    results = search_album(query)
    print(f"\n--- Risultati trovati ({len(results)}) ---")
    for r in results:
        print(f"[{r['section']}] ({r['type']}) {r['title']} - {r['artist']} -> {r['url']}")

import os
import sys
from cloakbrowser import launch_persistent_context

def main():
    profile_dir = os.path.join(os.environ.get('XDG_DATA_HOME', os.path.expanduser('~/.local/share')), 'browser-profiles', 'amazon-music')
    print(f"Caricamento sessione da: {profile_dir}")
    
    # Avviamo in modalità non-headless per mostrare il browser
    context = launch_persistent_context(profile_dir, headless=False)
    page = context.new_page()
    
    # Impostiamo una dimensione della finestra grande per vedere bene i risultati
    page.set_viewport_size({"width": 1280, "height": 800})
    
    print("Navigazione su https://music.amazon.it/...")
    page.goto("https://music.amazon.it/")
    page.wait_for_timeout(7000)
    
    query = sys.argv[1] if len(sys.argv) > 1 else "Pinguini Tattici Nucleari"
    print(f"Esecuzione della ricerca per: '{query}'...")
    
    # Cerca il campo di input
    search_input = page.locator("#navbarSearchInput")
    search_input.focus()
    search_input.fill(query)
    search_input.press("Enter")
    
    print("In attesa dei risultati (4s)...")
    page.wait_for_timeout(4000)
    
    # Salvataggio screenshot per verifica visiva
    artifact_dir = "/Users/michele/.gemini/antigravity-cli/brain/cbd7b104-03bd-4eeb-866d-e9875c7239ce"
    os.makedirs(artifact_dir, exist_ok=True)
    screenshot_path = os.path.join(artifact_dir, "search_result.png")
    page.screenshot(path=screenshot_path)
    print(f"Screenshot salvato in: {screenshot_path}")
    
    # Parsing degli shoveler
    print("\n--- Analisi Risultati ---")
    shovelers = page.query_selector_all("music-shoveler")
    if not shovelers:
        print("Nessun 'music-shoveler' trovato nella pagina.")
    else:
        for idx, shoveler in enumerate(shovelers, 1):
            shoveler_type = shoveler.get_attribute("primary-text")
            print(f"\n[{idx}] Sezione Shoveler: {shoveler_type}")
            
            h_items = shoveler.query_selector_all("music-horizontal-item")
            v_items = shoveler.query_selector_all("music-vertical-item")
            
            if not h_items and not v_items:
                print("  Nessun elemento orizzontale o verticale trovato in questa sezione.")
                
            for item in h_items:
                title = item.get_attribute("primary-text")
                artist = item.get_attribute("secondary-text") or ""
                href = item.get_attribute("primary-href")
                print(f"  - [Orizzontale] Title: {title} | Artist: {artist} | Href: {href}")
                
            for item in v_items:
                title = item.get_attribute("primary-text")
                artist = item.get_attribute("secondary-text") or ""
                href = item.get_attribute("primary-href")
                print(f"  - [Verticale] Title: {title} | Artist: {artist} | Href: {href}")
                
    print("\nRicerca completata! Premi INVIO per chiudere il browser...")
    sys.stdin.read(1)
    context.close()

if __name__ == "__main__":
    main()

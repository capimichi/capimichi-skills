import os
from cloakbrowser import launch_persistent_context

def main():
    profile_dir = os.path.join(os.environ.get('XDG_DATA_HOME', os.path.expanduser('~/.local/share')), 'browser-profiles', 'lucida')
    context = launch_persistent_context(profile_dir, headless=False)
    page = context.new_page()
    page.set_viewport_size({"width": 1280, "height": 800})
    
    print("Navigazione su https://lucida.to/...")
    page.goto("https://lucida.to/")
    
    print("Attesa input #download...")
    page.wait_for_selector("#download", timeout=60000)
    
    track_url = "https://music.amazon.it/albums/B0GZKWGZV4?trackAsin=B0GZKYQZS6"
    print(f"Inserimento URL: {track_url}")
    page.locator("#download").fill(track_url)
    
    print("Clic su #go...")
    page.locator("#go").click()
    
    print("Attesa di 20 secondi per l'apparizione del pulsante...")
    page.wait_for_timeout(20000)
    
    print("\n--- Analisi degli elementi interattivi (button e a) presenti nella pagina ---")
    
    # Seleziona tutti i pulsanti e link
    interactive_elements = page.query_selector_all("button, a")
    for idx, elem in enumerate(interactive_elements, 1):
        tag_name = elem.evaluate("el => el.tagName.toLowerCase()")
        class_name = elem.evaluate("el => el.className")
        id_name = elem.evaluate("el => el.id")
        text_content = elem.evaluate("el => el.textContent").strip()
        outer_html = elem.evaluate("el => el.outerHTML")
        
        # Filtriamo per mostrare solo cose interessanti (evitiamo link vuoti o di navigazione standard)
        if text_content or class_name or id_name:
            print(f"\n[{idx}] Elemento <{tag_name}>:")
            print(f"  ID: '{id_name}'")
            print(f"  Classe: '{class_name}'")
            print(f"  Testo: '{text_content}'")
            print(f"  HTML: {outer_html[:300]}...")
            
    context.close()

if __name__ == "__main__":
    main()

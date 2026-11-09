import os
from cloakbrowser import launch_persistent_context

def main():
    profile_dir = os.path.join(os.environ.get('XDG_DATA_HOME', os.path.expanduser('~/.local/share')), 'browser-profiles', 'amazon-music')
    context = launch_persistent_context(profile_dir, headless=True)
    page = context.new_page()
    page.set_viewport_size({"width": 1280, "height": 800})
    
    print("Navigazione su https://music.amazon.it/...")
    page.goto("https://music.amazon.it/")
    page.wait_for_timeout(7000)
    
    # Esegui la ricerca
    query = "Pinguini Tattici Nucleari"
    search_input = page.locator("#navbarSearchInput")
    search_input.focus()
    search_input.fill(query)
    search_input.press("Enter")
    page.wait_for_timeout(4000)
    
    # Analizziamo gli shoveler
    shovelers = page.query_selector_all("music-shoveler")
    for idx, shoveler in enumerate(shovelers, 1):
        shoveler_type = shoveler.get_attribute("primary-text")
        print(f"\n[{idx}] Shoveler: {shoveler_type}")
        
        # Troviamo tutti gli elementi figli ricorsivamente che potrebbero contenere i testi
        # Cerchiamo tag che iniziano per "music-"
        custom_elements = shoveler.query_selector_all("*")
        tags_found = set()
        for elem in custom_elements:
            tag_name = elem.evaluate("el => el.tagName.toLowerCase()")
            if tag_name.startswith("music-"):
                tags_found.add(tag_name)
        
        print(f"  Tag custom trovati in questo shoveler: {list(tags_found)}")
        
        # Vediamo i primi 3 elementi specifici trovati all'interno dello shoveler per capire le loro proprietà
        for tag in tags_found:
            instances = shoveler.query_selector_all(tag)
            print(f"  -> Istante del tag <{tag}> (mostro le prime 2):")
            for inst in instances[:2]:
                outer_html = inst.evaluate("el => el.outerHTML")
                # Tronchiamo per non appesantire il log
                print(f"     HTML: {outer_html[:400]}...")

    context.close()

if __name__ == "__main__":
    main()

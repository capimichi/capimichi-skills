import os
import sys
import time
from cloakbrowser import launch_persistent_context

def main():
    profile_dir = os.path.join(os.environ.get('XDG_DATA_HOME', os.path.expanduser('~/.local/share')), 'browser-profiles', 'google-search')
    print(f"Avvio del browser con il profilo: {profile_dir}")
    context = launch_persistent_context(profile_dir, headless=False)
    page = context.new_page()
    page.set_viewport_size({"width": 1280, "height": 800})
    
    albums = [
        {"title": "Hanno ucciso l'Uomo Ragno", "year": "1992"},
        {"title": "Nord sud ovest est", "year": "1993"},
        {"title": "La donna il sogno & il grande incubo", "year": "1995"},
        {"title": "La dura legge del gol!", "year": "1997"},
        {"title": "Grazie mille", "year": "1999"},
        {"title": "Uno in più", "year": "2001"}
    ]
    
    results_summary = {}
    
    try:
        # Navighiamo su Google
        print("Navigazione su Google...")
        page.goto("https://www.google.com/?hl=it")
        page.wait_for_timeout(3000)
        
        # Gestiamo l'eventuale banner dei cookie di Google in Italia
        try:
            accept_btn = page.locator("#L2AGLb")
            if accept_btn.count() > 0:
                print("Accetto i cookie di Google...")
                accept_btn.click()
                page.wait_for_timeout(2000)
        except Exception as e:
            print(f"Nessun banner cookie rilevato o errore: {e}")
            
        for album in albums:
            title = album["title"]
            year = album["year"]
            query = f'883 "{title}" {year} torrent 1337x'
            print(f"\nCerco su Google: '{query}'...")
            
            # Troviamo la barra di ricerca (può essere textarea o input con name='q')
            search_box = page.locator("textarea[name='q'], input[name='q']").first
            search_box.focus()
            
            # Puliamo la ricerca precedente se necessario (seleziona tutto + cancella)
            # In alternativa navighiamo direttamente alla URL di ricerca di Google per evitare problemi di pulizia
            google_search_url = f"https://www.google.com/search?q={query.replace(' ', '+')}&hl=it"
            page.goto(google_search_url)
            page.wait_for_timeout(4000)
            
            # Analizziamo i risultati
            # I link dei risultati di ricerca solitamente sono all'interno di tag <a> sotto #search o in elementi con data-hveid o h3
            links = page.locator("a")
            found_1337x = []
            
            count = links.count()
            for i in range(count):
                link = links.nth(i)
                href = link.get_attribute("href") or ""
                text = link.inner_text() or ""
                
                # Cerchiamo se il link contiene "1337x" nel testo o nella URL (href)
                if "1337x" in href.lower() or "1337x" in text.lower():
                    # Evitiamo doppioni nella lista
                    entry = {"text": text.strip().replace("\n", " "), "href": href}
                    if entry not in found_1337x and href.startswith("http"):
                        found_1337x.append(entry)
                        
            results_summary[title] = found_1337x
            print(f"Trovati {len(found_1337x)} risultati per '{title}':")
            for idx, item in enumerate(found_1337x, 1):
                print(f"  {idx}. {item['text']} -> {item['href']}")
                
    except Exception as e:
        print(f"Errore generale: {e}")
        
    print("\n--- RIEPILOGO FINALE ---")
    for title, items in results_summary.items():
        if items:
            print(f"[DISPONIBILE] {title} (Trovati {len(items)} torrent su 1337x)")
        else:
            print(f"[NON TROVATO] {title} su 1337x")
            
    context.close()

if __name__ == "__main__":
    main()

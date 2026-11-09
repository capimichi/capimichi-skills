import os
import sys
from cloakbrowser import launch_persistent_context

def main():
    profile_dir = os.path.join(os.environ.get('XDG_DATA_HOME', os.path.expanduser('~/.local/share')), 'browser-profiles', 'monochrome')
    print(f"Avvio del browser con il profilo: {profile_dir}")
    context = launch_persistent_context(profile_dir, headless=False)
    page = context.new_page()
    page.set_viewport_size({"width": 1280, "height": 800})
    
    print("Navigazione su https://monochrome.tf/...")
    page.goto("https://monochrome.tf/")
    
    # Aspettiamo il caricamento
    page.wait_for_timeout(5000)
    
    query = "Fake News"
    print(f"Inserimento query di ricerca: {query}")
    
    # Proviamo a trovare il selettore dell'input di ricerca.
    # L'utente suggerisce #search-input
    try:
        search_input = page.locator("#search-input")
        search_input.wait_for(state="visible", timeout=10000)
        search_input.fill(query)
        search_input.press("Enter")
    except Exception as e:
        print(f"Errore nella ricerca: {e}")
        # Facciamo uno screenshot o stampiamo il DOM per debug
        page.screenshot(path="search_error.png")
        print("Salvo screenshot in search_error.png")
        
    print("Attesa di 2 secondi...")
    page.wait_for_timeout(2000)
    
    # Clicchiamo sulla tab degli album
    try:
        albums_tab = page.locator('button[data-tab="albums"]').first
        albums_tab.click()
        print("Cliccato sulla tab albums")
    except Exception as e:
        print(f"Errore nel cliccare la tab albums: {e}")
        
    page.wait_for_timeout(2000)
    
    # Leggiamo i risultati degli album e stampiamo l'HTML delle prime due card per inspect
    try:
        cards = page.locator("#search-albums-container .card")
        count = cards.count()
        print(f"Trovati {count} album:")
        for i in range(min(count, 3)):
            card = cards.nth(i)
            print(f"\n--- CARD {i} HTML ---")
            print(card.evaluate("el => el.outerHTML"))
    except Exception as e:
        print(f"Errore nella lettura dei risultati: {e}")
        
    print("Attesa di 5 secondi per osservazione...")
    page.wait_for_timeout(5000)
    context.close()

if __name__ == "__main__":
    main()

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
    page.wait_for_timeout(5000)
    
    query = "Fake News"
    print(f"Inserimento query: {query}")
    
    try:
        search_input = page.locator("#search-input")
        search_input.wait_for(state="visible", timeout=10000)
        search_input.fill(query)
        search_input.press("Enter")
    except Exception as e:
        print(f"Errore ricerca: {e}")
        
    print("Attesa di 2 secondi...")
    page.wait_for_timeout(2000)
    
    try:
        albums_tab = page.locator('button[data-tab="albums"]').first
        albums_tab.click()
        print("Cliccato sulla tab albums")
    except Exception as e:
        print(f"Errore tab: {e}")
        
    page.wait_for_timeout(2000)
    
    # Cerchiamo l'album di "Pinguini Tattici Nucleari"
    target_card = None
    try:
        cards = page.locator("#search-albums-container .card")
        count = cards.count()
        for i in range(count):
            card = cards.nth(i)
            title = card.locator(".card-title").inner_text()
            subtitle = card.locator(".card-subtitle").inner_text()
            print(f"Esamino album: '{title}' - '{subtitle}'")
            if "pinguini" in subtitle.lower() and "fake news" in title.lower():
                target_card = card
                print(f"Trovato target card: {title} - {subtitle}")
                break
    except Exception as e:
        print(f"Errore ricerca target: {e}")
        
    if target_card:
        data_href = target_card.get_attribute("data-href")
        print(f"Clicco sulla card con data-href: {data_href}")
        target_card.click()
        
        print("Attesa di 3 secondi per caricamento album...")
        page.wait_for_timeout(3000)
        
        # Stampiamo l'URL corrente
        print(f"URL corrente: {page.url}")
        
        # Cerchiamo .download-album-btn
        try:
            download_btn = page.locator(".download-album-btn")
            if download_btn.count() > 0:
                print("Trovato .download-album-btn!")
                print(download_btn.evaluate("el => el.outerHTML"))
            else:
                print("Nessun .download-album-btn trovato. Cerco pulsanti di download generici o .download...")
                buttons = page.locator("button, a")
                count = buttons.count()
                for i in range(count):
                    btn = buttons.nth(i)
                    class_name = btn.get_attribute("class") or ""
                    id_name = btn.get_attribute("id") or ""
                    text = btn.inner_text() or ""
                    if "download" in class_name or "download" in id_name or "download" in text.lower() or "scarica" in text.lower():
                        print(f"Trovato possibile pulsante di download: <{btn.evaluate('el => el.tagName')} class='{class_name}' id='{id_name}'>{text}</{btn.evaluate('el => el.tagName')}>")
        except Exception as e:
            print(f"Errore ispezione download button: {e}")
    else:
        print("Album non trovato!")
        
    print("Attesa di 5 secondi prima di chiudere...")
    page.wait_for_timeout(5000)
    context.close()

if __name__ == "__main__":
    main()

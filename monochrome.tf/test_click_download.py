import os
import sys
from cloakbrowser import launch_persistent_context

def main():
    profile_dir = os.path.join(os.environ.get('XDG_DATA_HOME', os.path.expanduser('~/.local/share')), 'browser-profiles', 'monochrome')
    print(f"Avvio del browser con il profilo: {profile_dir}")
    context = launch_persistent_context(profile_dir, headless=False)
    page = context.new_page()
    page.set_viewport_size({"width": 1280, "height": 800})
    
    # Abilitiamo la cattura dei messaggi di console
    page.on("console", lambda msg: print(f"[CONSOLE] {msg.type}: {msg.text}"))
    
    # Listener per download
    downloads = []
    page.on("download", lambda d: downloads.append(d))
    
    print("Navigazione su https://monochrome.tf/album/296803260...")
    page.goto("https://monochrome.tf/album/296803260")
    
    print("Attesa di 5 secondi per il caricamento completo...")
    page.wait_for_timeout(5000)
    
    download_btn = page.locator("#download-album-btn")
    if download_btn.count() > 0:
        print("Pulsante #download-album-btn trovato. Clicco...")
        
        # Facciamo uno screenshot prima del click
        os.makedirs("screenshots", exist_ok=True)
        page.screenshot(path="screenshots/before_click.png")
        
        # Clicchiamo
        download_btn.click()
        
        print("Attesa del download o di messaggi di stato per 30 secondi...")
        # Controlliamo periodicamente lo stato per 30 secondi
        for i in range(30):
            page.wait_for_timeout(1000)
            if downloads:
                print(f"Download rilevato! Nome: {downloads[0].suggested_filename}")
                break
                
        # Facciamo uno screenshot dopo 10 secondi per vedere cosa appare sullo schermo
        page.screenshot(path="screenshots/after_click.png")
        
        if downloads:
            d = downloads[0]
            download_dir = os.path.expanduser('~/Downloads')
            dest = os.path.join(download_dir, d.suggested_filename)
            print(f"Salvataggio in {dest}...")
            d.save_as(dest)
            print("Download salvato con successo!")
        else:
            print("Nessun download avviato in 30 secondi.")
            
            # Vediamo se c'è un modal o popup visibile
            try:
                popups = page.locator(".modal, .popup, .notification, [class*='modal'], [class*='popup']")
                p_count = popups.count()
                if p_count > 0:
                    print(f"Trovati {p_count} elementi popup/notifica:")
                    for j in range(p_count):
                        print(f"Popup {j}: {popups.nth(j).inner_text()}")
            except Exception as e:
                print(f"Errore controllo popup: {e}")
    else:
        print("Pulsante #download-album-btn NON trovato.")
        
    context.close()

if __name__ == "__main__":
    main()

import os
import time
from cloakbrowser import launch_context

def main():
    print("Avvio del browser con un profilo pulito (non persistente)...")
    # launch_context crea un contesto pulito e gestisce i download
    context = launch_context(headless=False)
    page = context.new_page()
    page.set_viewport_size({"width": 1280, "height": 800})
    
    # Raccoglitore per gli eventi di download
    downloads = []
    page.on("download", lambda d: downloads.append(d))
    
    album_url = "https://monochrome.tf/album/296803260"
    print(f"Navigazione su {album_url}...")
    page.goto(album_url)
    
    print("Attesa di 5 secondi...")
    page.wait_for_timeout(5000)
    
    download_btn = page.locator("#download-album-btn")
    if download_btn.count() > 0:
        print("Clicco su #download-album-btn...")
        download_btn.click()
        
        print("Attesa del download per 30 secondi...")
        for i in range(15):
            page.wait_for_timeout(2000)
            if downloads:
                print(f"Download intercettato: {downloads[0].suggested_filename}")
                dest = os.path.expanduser(f"~/Downloads/{downloads[0].suggested_filename}")
                downloads[0].save_as(dest)
                print(f"Salvo in {dest}")
                break
    else:
        print("Pulsante non trovato.")
        
    context.close()

if __name__ == "__main__":
    main()

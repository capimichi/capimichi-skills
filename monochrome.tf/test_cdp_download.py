import os
import sys
import time
from cloakbrowser import launch_persistent_context

def main():
    profile_dir = os.path.join(os.environ.get('XDG_DATA_HOME', os.path.expanduser('~/.local/share')), 'browser-profiles', 'monochrome')
    print(f"Avvio del browser con il profilo: {profile_dir}")
    context = launch_persistent_context(profile_dir, headless=False)
    page = context.new_page()
    page.set_viewport_size({"width": 1280, "height": 800})
    
    # Riconoscimento console
    page.on("console", lambda msg: print(f"[CONSOLE] {msg.type}: {msg.text}"))
    
    # Abilitiamo il download automatico via CDP
    try:
        client = page.context.new_cdp_session(page)
        download_dir = os.path.expanduser('~/Downloads')
        os.makedirs(download_dir, exist_ok=True)
        client.send("Page.setDownloadBehavior", {
            "behavior": "allow",
            "downloadPath": download_dir
        })
        print(f"Configurato CDP Page.setDownloadBehavior con downloadPath: {download_dir}")
    except Exception as e:
        print(f"Errore configurazione CDP: {e}")
    
    # Raccoglitore per gli eventi di download
    downloads = []
    page.on("download", lambda d: downloads.append(d))
    
    album_url = "https://monochrome.tf/album/296803260"
    print(f"Navigazione su {album_url}...")
    page.goto(album_url)
    page.wait_for_timeout(5000)
    
    download_btn = page.locator("#download-album-btn")
    if download_btn.count() > 0:
        print("Clicco su #download-album-btn...")
        download_btn.click()
        
        print("Attesa del download (fino a 60 secondi)...")
        start_time = time.time()
        while time.time() - start_time < 60:
            page.wait_for_timeout(1000)
            if downloads:
                print(f"Download intercettato: {downloads[0].suggested_filename}")
                dest = os.path.join(download_dir, downloads[0].suggested_filename)
                downloads[0].save_as(dest)
                print(f"Salvo in {dest}")
                break
    else:
        print("Pulsante non trovato.")
        
    context.close()

if __name__ == "__main__":
    main()

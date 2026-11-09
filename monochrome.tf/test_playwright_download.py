import os
import sys
from cloakbrowser import launch_persistent_context

def main():
    profile_dir = os.path.join(os.environ.get('XDG_DATA_HOME', os.path.expanduser('~/.local/share')), 'browser-profiles', 'monochrome')
    print(f"Avvio del browser con il profilo: {profile_dir}")
    context = launch_persistent_context(profile_dir, headless=False)
    page = context.new_page()
    page.set_viewport_size({"width": 1280, "height": 800})
    
    album_url = "https://monochrome.tf/album/296803260"
    print(f"Navigazione su {album_url}...")
    page.goto(album_url)
    page.wait_for_timeout(5000)
    
    download_btn = page.locator("#download-album-btn")
    if download_btn.count() > 0:
        print("Clicco su #download-album-btn usando expect_download...")
        try:
            # 1. Configura il gestore del download prima del click (timeout a 2 minuti)
            with page.expect_download(timeout=120000) as download_info:
                # 2. Clicca il pulsante che avvia il download
                download_btn.click()
                
            # 3. Ottieni l'oggetto download
            download = download_info.value
            print(f"Download rilevato! Nome suggerito: {download.suggested_filename}")
            
            # 4. Salva il file
            download_dir = os.path.expanduser('~/Downloads')
            dest_path = os.path.join(download_dir, download.suggested_filename)
            print(f"Salvataggio in corso in: {dest_path}")
            download.save_as(dest_path)
            print("[SUCCESS] Download completato e salvato correttamente!")
        except Exception as e:
            print(f"Errore durante il download: {e}")
    else:
        print("Pulsante non trovato.")
        
    context.close()

if __name__ == "__main__":
    main()

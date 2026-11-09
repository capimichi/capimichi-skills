import os
import sys
import time
import json
from cloakbrowser import launch_persistent_context

def configure_download_prefs(profile_dir):
    pref_path = os.path.join(profile_dir, "Default", "Preferences")
    os.makedirs(os.path.dirname(pref_path), exist_ok=True)
    
    prefs = {}
    if os.path.exists(pref_path):
        try:
            with open(pref_path, "r", encoding="utf-8") as f:
                prefs = json.load(f)
        except Exception as e:
            print(f"Errore caricamento Preferences: {e}")
            
    # Impostiamo le preferenze per disattivare il prompt di salvataggio
    if "download" not in prefs:
        prefs["download"] = {}
        
    prefs["download"]["prompt_for_download"] = False
    prefs["download"]["directory_upgrade"] = True
    prefs["download"]["default_directory"] = os.path.expanduser("~/Downloads")
    
    try:
        with open(pref_path, "w", encoding="utf-8") as f:
            json.dump(prefs, f, indent=4)
        print("Preferenze di download configurate (prompt disattivato).")
    except Exception as e:
        print(f"Errore scrittura Preferences: {e}")

def main():
    profile_dir = os.path.join(os.environ.get('XDG_DATA_HOME', os.path.expanduser('~/.local/share')), 'browser-profiles', 'monochrome')
    
    # Configuriamo le preferenze prima di avviare il browser
    configure_download_prefs(profile_dir)
    
    print(f"Avvio del browser con il profilo: {profile_dir}")
    context = launch_persistent_context(profile_dir, headless=False)
    page = context.new_page()
    page.set_viewport_size({"width": 1280, "height": 800})
    
    # Listener per i messaggi della console
    page.on("console", lambda msg: print(f"[CONSOLE] {msg.type}: {msg.text}"))
    
    # Raccoglitore per gli eventi di download
    downloads = []
    page.on("download", lambda d: downloads.append(d))
    
    album_url = "https://monochrome.tf/album/296803260"
    print(f"Navigazione su {album_url}...")
    page.goto(album_url)
    
    print("Attesa di 5 secondi per il caricamento iniziale...")
    page.wait_for_timeout(5000)
    
    download_btn = page.locator("#download-album-btn")
    if download_btn.count() == 0:
        print("Pulsante #download-album-btn non trovato!")
        context.close()
        return
        
    print("Clicco su #download-album-btn...")
    download_btn.click()
    
    print("Attesa del download (fino a 2 minuti)...")
    start_time = time.time()
    download_completed = False
    
    # Monitoraggio dei messaggi di download nella pagina
    while time.time() - start_time < 120:
        page.wait_for_timeout(1000)
        
        # Se viene catturato il download
        if downloads:
            download = downloads[0]
            print(f"\n[DOWNLOAD INTERCETTATO] Nome suggerito: {download.suggested_filename}")
            
            download_dir = os.path.expanduser('~/Downloads')
            os.makedirs(download_dir, exist_ok=True)
            dest_path = os.path.join(download_dir, download.suggested_filename)
            
            print(f"Salvataggio del file in corso: {dest_path}...")
            download.save_as(dest_path)
            print(f"[SUCCESS] Download completato e salvato con successo!")
            download_completed = True
            break
            
        # Altrimenti, proviamo a stampare il testo del box di download per monitorare il progresso
        try:
            status_elements = page.locator("[class*='download'], [id*='download']").all()
            status_texts = []
            for el in status_elements:
                text = el.inner_text().strip()
                if text and any(k in text.lower() for k in ["starting", "downloading", "progress", "%", "/"]):
                    if len(text) < 200 and text not in status_texts:
                        status_texts.append(text)
            if status_texts:
                print(f"[STATO PAGE]: { ' | '.join(status_texts) }", end="\r")
        except Exception:
            pass
            
    if not download_completed:
        print("\n[ERRORE] Timeout di 2 minuti superato senza che il download venisse avviato.")
        screenshot_path = "screenshots/download_timeout.png"
        os.makedirs("screenshots", exist_ok=True)
        page.screenshot(path=screenshot_path)
        print(f"Screenshot salvato in: {screenshot_path}")
        
    context.close()

if __name__ == "__main__":
    main()

import os
import sys
from cloakbrowser import launch_persistent_context

def main():
    profile_dir = os.path.join(os.environ.get('XDG_DATA_HOME', os.path.expanduser('~/.local/share')), 'browser-profiles', 'monochrome')
    print(f"Avvio del browser con il profilo: {profile_dir}")
    context = launch_persistent_context(profile_dir, headless=False)
    page = context.new_page()
    page.set_viewport_size({"width": 1280, "height": 800})
    
    # Listener per richieste fallite
    page.on("requestfailed", lambda request: print(f"[REQ FAILED] URL: {request.url}, Error: {request.failure if request.failure else 'Unknown'}"))
    
    # Listener per la console
    page.on("console", lambda msg: print(f"[CONSOLE] {msg.type}: {msg.text}"))

    print("Navigazione su https://monochrome.tf/album/296803260...")
    page.goto("https://monochrome.tf/album/296803260")
    page.wait_for_timeout(6000)
    
    download_btn = page.locator("#download-album-btn")
    if download_btn.count() > 0:
        print("Clicco su #download-album-btn...")
        download_btn.click()
        
        # Attendiamo 15 secondi per osservare le richieste di rete
        page.wait_for_timeout(15000)
    else:
        print("Pulsante non trovato.")
        
    context.close()

if __name__ == "__main__":
    main()

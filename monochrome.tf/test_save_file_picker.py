import os
import sys
from cloakbrowser import launch_persistent_context

def main():
    profile_dir = os.path.join(os.environ.get('XDG_DATA_HOME', os.path.expanduser('~/.local/share')), 'browser-profiles', 'monochrome')
    print(f"Avvio del browser con il profilo: {profile_dir}")
    context = launch_persistent_context(profile_dir, headless=False)
    page = context.new_page()
    page.set_viewport_size({"width": 1280, "height": 800})
    
    # Rilevamento console
    page.on("console", lambda msg: print(f"[CONSOLE] {msg.type}: {msg.text}"))
    
    # Iniettiamo uno script per intercettare showSaveFilePicker e stamparlo in console
    page.add_init_script("""
        const originalShowSaveFilePicker = window.showSaveFilePicker;
        window.showSaveFilePicker = async function(options) {
            console.log("=== showSaveFilePicker CHIAMATO! ===", JSON.stringify(options));
            if (originalShowSaveFilePicker) {
                return originalShowSaveFilePicker.apply(this, arguments);
            }
            throw new Error("showSaveFilePicker non supportato originariamente");
        };
        console.log("Script di intercettazione showSaveFilePicker caricato.");
    """)
    
    print("Navigazione su https://monochrome.tf/album/296803260...")
    page.goto("https://monochrome.tf/album/296803260")
    page.wait_for_timeout(5000)
    
    download_btn = page.locator("#download-album-btn")
    if download_btn.count() > 0:
        print("Clicco su #download-album-btn...")
        download_btn.click()
        
        # Attendiamo 15 secondi per vedere se viene loggata la chiamata
        page.wait_for_timeout(15000)
    else:
        print("Pulsante non trovato.")
        
    context.close()

if __name__ == "__main__":
    main()

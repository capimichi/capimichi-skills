import os
import sys
from cloakbrowser import launch_persistent_context

def main():
    if len(sys.argv) < 2:
        print("Uso: python3 downloader.py <URL_DELLA_CANZONE>")
        sys.exit(1)
        
    track_url = sys.argv[1]
    profile_dir = os.path.join(os.environ.get('XDG_DATA_HOME', os.path.expanduser('~/.local/share')), 'browser-profiles', 'lucida')
    
    print(f"Avvio del browser con il profilo: {profile_dir}")
    # Avviamo non-headless per consentire di risolvere eventuali captcha di Cloudflare
    context = launch_persistent_context(profile_dir, headless=False)
    page = context.new_page()
    page.set_viewport_size({"width": 1280, "height": 800})
    
    print("Navigazione su https://lucida.to/...")
    page.goto("https://lucida.to/")
    
    print("Attesa del caricamento dell'interfaccia (superamento protezione Cloudflare)...")
    try:
        # Attendiamo fino a 60 secondi che l'elemento di input diventi visibile
        page.wait_for_selector("#download", timeout=60000)
    except Exception:
        print("Errore: L'interfaccia di Lucida.to non si è caricata. Controlla la finestra del browser.")
        context.close()
        sys.exit(1)
        
    print("Interfaccia pronta! Inserimento dell'URL della canzone...")
    search_input = page.locator("#download")
    search_input.fill(track_url)
    
    # Clicchiamo sul tasto go
    go_button = page.locator("#go")
    go_button.click()
    print("Richiesta inviata. Attesa di 3 secondi per l'avvio dell'elaborazione...")
    page.wait_for_timeout(3000)
    print("Elaborazione in corso (questo potrebbe richiedere un po' di tempo)...")
    
    # Prepariamo i locatori per il controllo dell'esito
    error_locator = page.locator("text=/An error occur/i")
    # Riconosce la classe .download-button o il testo "scarica traccia" (case-insensitive)
    download_locator = page.locator(".download-button").or_(page.locator("text=/scarica traccia/i"))
    
    combined_locator = error_locator.or_(download_locator)
    
    try:
        # Aspettiamo che appaia uno dei due elementi (il caricamento o l'errore)
        # Impostiamo un timeout di 90 secondi per la conversione
        combined_locator.first.wait_for(state="visible", timeout=90000)
    except Exception:
        print("Errore: Timeout durante l'attesa del download o del messaggio di errore.")
        context.close()
        sys.exit(1)
        
    # Controlliamo prima se è apparso l'errore
    if error_locator.is_visible():
        print("[RISULTATO] Non funziona il link: il ripper ha restituito errore per questo URL.")
        context.close()
        sys.exit(1)
        
    # Se invece c'è il tasto download
    if download_locator.first.is_visible():
        print("Brano pronto! Avvio del download...")
        
        # Salviamo nella cartella dei Download dell'utente
        download_dir = os.path.expanduser('~/Downloads')
        os.makedirs(download_dir, exist_ok=True)
        
        try:
            # Registriamo il listener per intercettare l'avvio del download
            downloads = []
            page.on("download", lambda d: downloads.append(d))
            
            # Forziamo il click in JS sul tasto download
            download_locator.first.evaluate("el => el.click()")
            
            # Attendiamo l'esito (errore post-click o avvio effettivo del download)
            error_appeared = False
            for _ in range(45):  # Fino a 45 secondi
                page.wait_for_timeout(1000)
                if error_locator.is_visible():
                    error_appeared = True
                    break
                if downloads:
                    break
            
            if error_appeared:
                screenshot_path = os.path.join(profile_dir, "error_screenshot.png")
                page.screenshot(path=screenshot_path)
                print(f"[RISULTATO] Non funziona il link: errore riscontrato dopo il click su scarica. Screenshot in {screenshot_path}")
                context.close()
                sys.exit(1)
                
            if not downloads:
                screenshot_path = os.path.join(profile_dir, "error_screenshot.png")
                page.screenshot(path=screenshot_path)
                print(f"Errore: Timeout durante l'attesa dell'avvio del download. Screenshot in {screenshot_path}")
                context.close()
                sys.exit(1)
                
            download = downloads[0]
            # Salviamo il file mantenendo il nome suggerito dal portale
            suggested_filename = download.suggested_filename
            dest_path = os.path.join(download_dir, suggested_filename)
            download.save_as(dest_path)
            
            print(f"[SUCCESS] Download completato! File salvato in: {dest_path}")
        except Exception as e:
            print(f"Errore durante il download del file: {e}")
            
    context.close()

if __name__ == "__main__":
    main()

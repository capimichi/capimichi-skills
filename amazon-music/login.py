import os
import sys
from cloakbrowser import launch_persistent_context

def main():
    profile_dir = os.path.join(os.environ.get('XDG_DATA_HOME', os.path.expanduser('~/.local/share')), 'browser-profiles', 'amazon-music')
    print(f"Avvio del browser con il profilo in: {profile_dir}")
    context = launch_persistent_context(profile_dir, headless=False)
    page = context.new_page()
    
    print("Navigazione su https://music.amazon.it/...")
    page.goto("https://music.amazon.it/")
    
    print("\n[ATTENZIONE] Effettua il login nella finestra del browser che si è aperta.")
    print("Una volta effettuato l'accesso con successo, premi INVIO qui per chiudere e salvare la sessione.")
    
    sys.stdin.read(1)  # Aspetta che l'utente invii un carattere/invio
    print("Chiusura del browser e salvataggio della sessione...")
    context.close()

if __name__ == "__main__":
    main()

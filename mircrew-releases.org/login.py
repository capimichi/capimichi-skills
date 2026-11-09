import os
import sys
import getpass
from cloakbrowser import launch_persistent_context

def main():
    profile_dir = os.path.join(os.environ.get('XDG_DATA_HOME', os.path.expanduser('~/.local/share')), 'browser-profiles', 'mircrew')
    username = os.environ.get("MIRCREW_USERNAME") or (sys.argv[1] if len(sys.argv) > 1 else "paolorossi1993")
    password = os.environ.get("MIRCREW_PASSWORD") or (sys.argv[2] if len(sys.argv) > 2 else "Prova.123")
    
    print(f"Avvio del browser Cloak con profilo: {profile_dir}")
    context = launch_persistent_context(profile_dir, headless=False)
    page = context.new_page()
    page.set_viewport_size({"width": 1280, "height": 800})
    
    print("Verifica stato di login...")
    page.goto("https://mircrew-releases.org/", wait_until="domcontentloaded")
    page.wait_for_timeout(2000)
    
    logout_btn = page.locator("a[href*='mode=logout']")
    if logout_btn.count() > 0 and logout_btn.first.is_visible():
        print("✅ Sei già autenticato su Mircrew!")
        context.close()
        return

    print(f"Tentativo di login con utente '{username}'...")
    page.goto("https://mircrew-releases.org/ucp.php?mode=login", wait_until="domcontentloaded")
    page.wait_for_timeout(2000)
    
    # Fill login form
    page.locator("input[name='username']").fill(username)
    page.locator("input[name='password']").fill(password)
    
    # Check autologin / remember me if present
    autologin = page.locator("input[name='autologin']")
    if autologin.count() > 0:
        autologin.check()
        
    viewonline = page.locator("input[name='viewonline']")
    if viewonline.count() > 0:
        viewonline.check()
        
    print("Invio credenziali...")
    page.locator("input[type='submit'][name='login']").click()
    page.wait_for_load_state("networkidle")
    page.wait_for_timeout(3000)
    
    # Check if login succeeded
    logout_btn = page.locator("a[href*='mode=logout']")
    if logout_btn.count() > 0 or "logout" in page.content():
        print("🎉 Login effettuato con successo! Sessione salvata nel profilo.")
    else:
        # Check for errors
        error_box = page.locator(".error, .alert-danger")
        if error_box.count() > 0:
            print(f"❌ Errore login: {error_box.first.inner_text().strip()}")
        else:
            print("⚠️ Stato incerto dopo il login. Controlla il browser.")
            
    context.close()

if __name__ == "__main__":
    main()

import os
import sys
from cloakbrowser import launch_persistent_context

def main():
    profile_dir = os.path.join(os.environ.get('XDG_DATA_HOME', os.path.expanduser('~/.local/share')), 'browser-profiles', 'monochrome')
    print(f"Avvio del browser con il profilo: {profile_dir}")
    context = launch_persistent_context(profile_dir, headless=False)
    page = context.new_page()
    page.set_viewport_size({"width": 1280, "height": 800})
    
    # Dialog listener per gestire window.prompt
    def handle_dialog(dialog):
        print(f"[DIALOG] Tipo: {dialog.type}, Messaggio: {dialog.message}, Valore predefinito: {dialog.default_value}")
        dialog.accept("Fake News Download")
        print("[DIALOG] Accettato con valore 'Fake News Download'")
    page.on("dialog", handle_dialog)

    print("Navigazione su https://monochrome.tf/album/296803260...")
    page.goto("https://monochrome.tf/album/296803260")
    page.wait_for_timeout(5000)
    
    download_btn = page.locator("#download-album-btn")
    if download_btn.count() > 0:
        print("Clicco su #download-album-btn...")
        download_btn.click()
        
        page.wait_for_timeout(3000)
        
        # Facciamo uno screenshot dopo il click
        os.makedirs("screenshots", exist_ok=True)
        page.screenshot(path="screenshots/after_click_inspect.png")
        print("Screenshot salvato in screenshots/after_click_inspect.png")
        
        # Cerchiamo elementi di input visibili o modali
        inputs = page.locator("input:visible")
        i_count = inputs.count()
        print(f"Trovati {i_count} input visibili dopo il click:")
        for idx in range(i_count):
            inp = inputs.nth(idx)
            print(f"  Input {idx}: id='{inp.get_attribute('id')}', class='{inp.get_attribute('class')}', placeholder='{inp.get_attribute('placeholder')}', value='{inp.input_value()}'")
            
        # Vediamo se c'è qualche contenitore modal visibile
        modals = page.locator(".modal:visible, .popup:visible, .dialog:visible, [class*='modal']:visible")
        m_count = modals.count()
        print(f"Trovati {m_count} modal/popup visibili:")
        for idx in range(m_count):
            m = modals.nth(idx)
            print(f"  Modal {idx}: class='{m.get_attribute('class')}', HTML: {m.evaluate('el => el.innerHTML')}")
            
    else:
        print("Pulsante non trovato.")
        
    context.close()

if __name__ == "__main__":
    main()

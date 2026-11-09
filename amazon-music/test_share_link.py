import os
import sys
from cloakbrowser import launch_persistent_context

def test_share_album(album_url):
    profile_dir = os.path.join(os.environ.get('XDG_DATA_HOME', os.path.expanduser('~/.local/share')), 'browser-profiles', 'amazon-music')
    print(f"Caricamento sessione browser da: {profile_dir}")
    
    context = launch_persistent_context(profile_dir, headless=False)
    # Diamo permessi clipboard-read e clipboard-write al contesto del browser
    try:
        context.grant_permissions(["clipboard-read", "clipboard-write"], origin="https://music.amazon.it")
    except Exception as e:
        print(f"Impossibile impostare permessi clipboard: {e}")
        
    page = context.new_page()
    page.set_viewport_size({"width": 1280, "height": 800})
    
    print(f"Navigazione verso: {album_url}...")
    page.goto(album_url)
    page.wait_for_timeout(6000)
    
    print("Cerca il pulsante del menu [name='more'] o #detailHeaderContextButton...")
    
    # 1. Cerca il pulsante context menu in header
    more_btn = page.locator("#detailHeaderContextButton, #detailHeaderButton [name='more'], music-button[icon-name='more']").first
    if more_btn.is_visible():
        print("Trovato pulsante more/context, clicco...")
        more_btn.click()
        page.wait_for_timeout(2000)
    else:
        print("Pulsante more header non trovato direttamente.")
        
    # 2. Cerca l'elemento 'Condividi' tra i music-list-item
    print("Cerca music-list-item 'Condividi'...")
    share_item = page.locator("music-list-item[primary-text*='Condividi'], music-list-item[primary-text*='Share']").first
    if share_item.is_visible():
        print("Trovato elemento Condividi, clicco...")
        share_item.click()
        page.wait_for_timeout(2000)
    else:
        print("Elemento Condividi non visibile direttamente.")
        
    # 3. Cerca il tasto copia link (icon-name='sharelink' o simile)
    print("Cerca tasto copia link [icon-name='sharelink']...")
    copy_btn = page.locator("music-button[icon-name='sharelink'], [icon-name='sharelink'], music-button:has-text('Copia link'), music-button:has-text('Copy link')").first
    if copy_btn.is_visible():
        print("Trovato tasto copia link, clicco...")
        copy_btn.click()
        page.wait_for_timeout(1000)
        
        # Leggiamo il testo dagli appunti usando evaluate JavaScript
        clipboard_text = page.evaluate("navigator.clipboard.readText()")
        print(f"\n🎉 LINK COPIATO NEGLI APPUNTI: {clipboard_text}")
    else:
        print("Tasto copia link non trovato.")
        
    page.wait_for_timeout(3000)
    context.close()

if __name__ == "__main__":
    url = sys.argv[1] if len(sys.argv) > 1 else "https://music.amazon.it/albums/B01F2UC01E"
    test_share_album(url)

import time
from meta.paths import get_cache_dir
from meta.browser import launch_meta_browser

def delete_old_post():
    cache_dir = get_cache_dir()
    context = launch_meta_browser(headless=True)
    page = context.new_page()

    url = 'https://business.facebook.com/latest/posts/published_posts?asset_id=918101574729792'
    print(f"Navigating to {url}...")
    page.goto(url, wait_until='domcontentloaded')
    time.sleep(5)

    ignora = page.get_by_role('button', name='Ignora')
    if ignora.count() > 0:
        try:
            ignora.click()
            time.sleep(1)
        except Exception:
            pass

    # Find checkboxes
    checkboxes = page.locator('input[type="checkbox"]').all()
    print(f'Trovate {len(checkboxes)} checkbox')

    # Row 1 is 16:18, Row 2 is 14:53
    # Checkbox 0 is "Select all", Checkbox 1 is post 1 (16:18), Checkbox 2 is post 2 (14:53)
    # Let's inspect the rows to make sure we select the right one
    rows = page.locator('div[role="row"], tr').all()
    print(f'Trovate {len(rows)} righe')

    # Click checkbox for the 14:53 post
    # Alternatively find the row containing "14:53"
    target_row = page.locator('div[role="row"]:has-text("14:53"), tr:has-text("14:53")')
    if target_row.count() > 0:
        print("Trovata riga con '14:53', clicco la sua checkbox...")
        target_row.locator('input[type="checkbox"]').first.click(force=True)
    elif len(checkboxes) >= 3:
        print("Clicco checkbox[2]...")
        checkboxes[2].click(force=True)
    else:
        print("Errore: impossibile identificare la riga del post vecchio")
        page.screenshot(path=str(cache_dir / "delete_debug.png"))
        context.close()
        return False

    time.sleep(2)
    delete_btn = page.locator('button:has-text("Elimina"), div[role="button"]:has-text("Elimina")').first
    if delete_btn.count() == 0:
        print("Pulsante Elimina non trovato!")
        page.screenshot(path=str(cache_dir / "delete_debug.png"))
        context.close()
        return False

    print("Clicco su 'Elimina'...")
    delete_btn.click()
    time.sleep(2)

    confirm_btn = page.locator('[role="dialog"] [role="button"]:has-text("Sposta nel cestino"), button:has-text("Sposta nel cestino")').first
    if confirm_btn.count() > 0:
        print("Confermo: Clicco 'Sposta nel cestino'...")
        confirm_btn.click()
        time.sleep(5)
        print("Post spostato nel cestino con successo!")
        page.screenshot(path=str(cache_dir / "after_delete_success.png"))
        context.close()
        return True
    else:
        print("Pulsante 'Sposta nel cestino' non trovato!")
        page.screenshot(path=str(cache_dir / "delete_debug.png"))
        context.close()
        return False

if __name__ == "__main__":
    delete_old_post()

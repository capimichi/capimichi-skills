import sys
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from meta.browser import launch_meta_browser

def run():
    context = launch_meta_browser(headless=True)
    page = context.pages[0] if context.pages else context.new_page()

    try:
        # Controlla lista amici di Marcello Ferrari
        print("1. Controllo lista amici: https://www.facebook.com/me/friends")
        page.goto("https://www.facebook.com/me/friends", wait_until="domcontentloaded")
        time.sleep(5)
        page.screenshot(path=str(PROJECT_ROOT / "meta" / "my_friends_list.png"))

        txt = page.locator("body").inner_text()
        print("\n--- TESTO LISTA AMICI ---")
        for line in [l.strip() for l in txt.splitlines() if l.strip()][:40]:
            print(line)

        # Controlla notifiche
        print("\n2. Controllo notifiche: https://www.facebook.com/notifications")
        page.goto("https://www.facebook.com/notifications", wait_until="domcontentloaded")
        time.sleep(5)
        page.screenshot(path=str(PROJECT_ROOT / "meta" / "notifications_list.png"))

        notifs = page.locator("body").inner_text()
        print("\n--- TESTO NOTIFICHE ---")
        for line in [l.strip() for l in notifs.splitlines() if l.strip()][:40]:
            print(line)

    finally:
        context.close()

if __name__ == "__main__":
    run()

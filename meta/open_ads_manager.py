import sys
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from meta.browser import launch_meta_browser

AD_ACCOUNT_ID = "1116925509636183"
URL = f"https://adsmanager.facebook.com/adsmanager/manage/campaigns?act={AD_ACCOUNT_ID}"

def open_ads_manager():
    print("=" * 60)
    print("APERTURA META ADS MANAGER IN MODALITÀ VISIBILE (GUI)")
    print(f"Ad Account ID: {AD_ACCOUNT_ID}")
    print(f"URL: {URL}")
    print("=" * 60)

    context = launch_meta_browser(headless=False)
    page = context.pages[0] if context.pages else context.new_page()
    page.goto(URL)
    print("\nBrowser aperto con successo sulla tua scrivania!")
    print("La finestra rimarrà aperta per permetterti di visualizzare e operare in tempo reale.")

    try:
        while True:
            time.sleep(2)
            if not context.pages or all(p.is_closed() for p in context.pages):
                break
    except KeyboardInterrupt:
        pass
    except Exception as e:
        print(f"Session info: {e}")
    finally:
        try:
            context.close()
        except Exception:
            pass
        print("Finestra del browser chiusa.")

if __name__ == "__main__":
    open_ads_manager()

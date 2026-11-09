import sys
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from meta.browser import launch_meta_browser

AD_ACCOUNT_ID = "1116925509636183"
BILLING_URL = f"https://business.facebook.com/latest/billing_hub/payment_settings/?payment_account_id={AD_ACCOUNT_ID}&asset_id={AD_ACCOUNT_ID}&nav_ref=billing_hub"

def open_billing():
    print(f"Apertura interfaccia pagamenti Meta Ads: {BILLING_URL}")
    context = launch_meta_browser(headless=False)
    page = context.pages[0] if context.pages else context.new_page()
    page.goto(BILLING_URL)
    print("Browser aperto con successo!")
    print("Puoi procedere ad inserire la carta o PayPal nella finestra.")
    print("Il processo rimarrà attivo finché la finestra del browser rimane aperta.")

    try:
        while True:
            time.sleep(2)
            # Verifica se ci sono ancora pagine aperte
            if not context.pages or all(p.is_closed() for p in context.pages):
                break
    except KeyboardInterrupt:
        pass
    except Exception as e:
        print(f"Info sessione: {e}")
    finally:
        try:
            context.close()
        except Exception:
            pass
        print("Sessione browser terminata.")

if __name__ == "__main__":
    open_billing()

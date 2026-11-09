import sys
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from meta.browser import launch_meta_browser

AD_ACCOUNT_ID = "1116925509636183"
CAMPAIGN_ID = "120251426951480676"

def run():
    context = launch_meta_browser(
        headless=True,
        args=["--window-size=2000,1080"],
        viewport={"width": 2000, "height": 1080}
    )
    page = context.pages[0] if context.pages else context.new_page()

    try:
        url = f"https://adsmanager.facebook.com/adsmanager/manage/ads?act={AD_ACCOUNT_ID}&selected_campaign_ids={CAMPAIGN_ID}"
        print(f"Navigo a: {url}")
        page.goto(url, wait_until="domcontentloaded")
        time.sleep(6)

        page.screenshot(path=str(PROJECT_ROOT / "meta" / "current_ads_state.png"))
        print("Screenshot salvato in meta/current_ads_state.png")

        # Esamina righe
        rows = page.locator('div[role="row"]').all()
        print(f"Righe trovate: {len(rows)}")
        for idx, r in enumerate(rows):
            t = r.inner_text().strip().replace('\n', ' | ')
            print(f"Row {idx}: {t[:120]}")

        # Esamina modali / dialoghi
        dialogs = page.locator('div[role="dialog"]').all()
        print(f"Dialoghi trovati: {len(dialogs)}")
        for idx, d in enumerate(dialogs):
            t = d.inner_text().strip().replace('\n', ' | ')
            print(f"Dialog {idx}: {t[:150]}")

    finally:
        context.close()

if __name__ == "__main__":
    run()

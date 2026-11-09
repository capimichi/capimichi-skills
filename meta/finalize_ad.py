import sys
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from meta.paths import get_cache_dir
from meta.browser import launch_meta_browser

AD_ACCOUNT_ID = "1116925509636183"
URL = f"https://adsmanager.facebook.com/adsmanager/manage/campaigns?act={AD_ACCOUNT_ID}"

def finalize_ad():
    cache_dir = get_cache_dir()
    print("=" * 60)
    print("FINALIZZAZIONE INSERZIONE META ADS (LIVE)")
    print("=" * 60)

    context = launch_meta_browser(headless=False)
    page = context.pages[0] if context.pages else context.new_page()

    try:
        print("1. Apertura Ads Manager...")
        page.goto(URL, wait_until="networkidle")
        time.sleep(3)

        # Clicca sulla campagna Rikrestin
        print("2. Apertura campagna Rikrestin...")
        page.locator('text=Rikrestin 2x49 - Test Vendite').first.click()
        time.sleep(2)

        # Seleziona riga adset e apri modifica
        chk = page.locator('input[type="checkbox"]').all()
        if len(chk) >= 2:
            chk[1].click(force=True)
            time.sleep(1)
            mod = page.locator('div[role="button"]:has-text("Modifica"), button:has-text("Modifica")').filter(has_text='Modifica').first
            mod.click()
            time.sleep(3)

        # Clicca Avanti per andare all'Inserzione
        print("3. Navigazione a livello Inserzione...")
        avanti = page.get_by_role('button', name='Avanti')
        if avanti.count() > 0:
            avanti.first.click()
            time.sleep(4)

        page.screenshot(path=str(cache_dir / "live_ad_level.png"))

        # 4. Selezione Pagina Facebook
        print("4. Selezione Pagina Facebook: Naturale e sostenibile...")
        # Cerca combobox per Pagina
        page_combos = page.locator('div:has-text("Pagina Facebook")').locator('div[role="combobox"]').all()
        for cb in page_combos:
            txt = cb.inner_text().strip()
            print("Pagina attuale:", txt)
            if "Naturale e sostenibile" not in txt:
                cb.click()
                time.sleep(1)
                opt = page.locator('text=Naturale e sostenibile').first
                if opt.count() > 0:
                    opt.click()
                    time.sleep(2)
                    print("Selezionata Pagina Naturale e sostenibile!")
                break

        # 5. Selezione "Usa post esistente"
        print("5. Configurazione: Usa post esistente...")
        usa_post = page.locator('div[role="combobox"]:has-text("Crea inserzione"), div:has-text("Crea inserzione")').filter(has=page.locator('[role="combobox"]')).first
        if usa_post.count() > 0:
            usa_post.click()
            time.sleep(1)
            opt_post = page.locator('text=Usa un post esistente, text=Usa post esistente').first
            if opt_post.count() > 0:
                opt_post.click()
                time.sleep(2)
                print("Selezionato 'Usa post esistente'!")

        # 6. Seleziona post
        print("6. Ricerca pulsante 'Seleziona post'...")
        sel_btn = page.locator('button:has-text("Seleziona post"), div[role="button"]:has-text("Seleziona post")').first
        if sel_btn.count() > 0:
            sel_btn.click()
            time.sleep(3)
            # Scegli il post con Rikrestin o delle 16:18
            post_row = page.locator('text=Rikrestin, text=16:18, text=Noti capelli').first
            if post_row.count() > 0:
                post_row.click()
                time.sleep(1)
                page.locator('button:has-text("Continua"), div[role="button"]:has-text("Continua")').first.click()
                time.sleep(3)
                print("Post 16:18 selezionato con successo!")

        print("\nConfigurazione completata! La finestra rimane aperta per la tua revisione finale.")
        while True:
            time.sleep(2)
            if not context.pages or all(p.is_closed() for p in context.pages):
                break

    except KeyboardInterrupt:
        pass
    except Exception as e:
        print(f"Errore / Info: {e}")
    finally:
        try:
            context.close()
        except Exception:
            pass

if __name__ == "__main__":
    finalize_ad()

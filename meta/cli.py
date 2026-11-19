#!/usr/bin/env python3
"""
Meta CLI Entrypoint.
Automazione e navigazione su Facebook, Meta Business Suite e Ads Manager tramite CloakBrowser.
"""

import sys
import time
from pathlib import Path

# Assicura import della repository
current_dir = Path(__file__).resolve().parent
repo_root = current_dir.parent
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))

try:
    import click
except ImportError:
    sys.exit("Errore: modulo 'click' non trovato. Installa le dipendenze richieste eseguendo: pip install click")

AD_ACCOUNT_ID = "1116925509636183"
ASSET_ID = "918101574729792"
BM_HOME_URL = f"https://business.facebook.com/latest/home?asset_id={ASSET_ID}"
ADSMANAGER_URL = f"https://adsmanager.facebook.com/adsmanager/manage/campaigns?act={AD_ACCOUNT_ID}"
BILLING_URL = f"https://business.facebook.com/latest/billing_hub/payment_settings/?payment_account_id={AD_ACCOUNT_ID}&asset_id={AD_ACCOUNT_ID}&nav_ref=billing_hub"


@click.group(help="CLI per l'automazione e gestione di Meta Business Suite e Ads Manager.")
def cli():
    pass


@cli.command(name="login", help="Avvia il browser per effettuare il login interattivo a Meta/Facebook.")
def login_cmd():
    from meta.login import main as run_login
    run_login()


@cli.command(name="status", help="Verifica se la sessione persistente è autenticata su Meta Business Suite.")
@click.option("--visible", is_flag=True, default=False, help="Mostra il browser durante la verifica.")
def status_cmd(visible: bool):
    from meta.browser import launch_meta_browser
    click.echo("Verifica stato di autenticazione su Meta Business Suite...")
    context = launch_meta_browser(headless=not visible)
    try:
        page = context.pages[0] if context.pages else context.new_page()
        page.goto(BM_HOME_URL, wait_until="domcontentloaded", timeout=25000)
        time.sleep(4)
        if "login" not in page.url and ("business.facebook.com" in page.url or "meta" in page.url):
            click.echo("🟢 Sessione attiva e autenticata su Meta Business Suite!")
            click.echo(f"   URL: {page.url}")
        else:
            click.echo("🟡 Sessione non autenticata o richiesta verifica. Esegui 'cli.py login'.")
    finally:
        context.close()


@cli.command(name="billing", help="Ispeziona lo stato contabile o apre la schermata pagamenti per inserimento carta.")
@click.option("--open-ui", is_flag=True, default=False, help="Apre la finestra visibile per inserimento sicuro di carte o PayPal.")
@click.option("--visible", is_flag=True, default=False, help="Mostra il browser durante l'ispezione.")
def billing_cmd(open_ui: bool, visible: bool):
    if open_ui:
        from meta.open_billing import open_billing
        open_billing()
    else:
        from meta.get_account_status import inspect_billing
        inspect_billing(headless=not visible)


@cli.command(name="ads-manager", help="Apre o verifica la schermata di Gestione Inserzioni (Ads Manager).")
@click.option("--open-ui", is_flag=True, default=True, help="Apre la finestra visibile di Ads Manager.")
def ads_manager_cmd(open_ui: bool):
    from meta.browser import launch_meta_browser
    click.echo(f"Apertura Meta Ads Manager (Account #{AD_ACCOUNT_ID})...")
    context = launch_meta_browser(headless=not open_ui)
    page = context.pages[0] if context.pages else context.new_page()
    page.goto(ADSMANAGER_URL)
    click.echo(f"Ads Manager aperto su: {ADSMANAGER_URL}")

    if open_ui:
        click.echo("La finestra rimarrà aperta finché non la chiudi o premi Ctrl+C.")
        try:
            while True:
                time.sleep(2)
                if not context.pages or all(p.is_closed() for p in context.pages):
                    break
        except KeyboardInterrupt:
            pass
        finally:
            try:
                context.close()
            except Exception:
                pass


@cli.command(name="suite", help="Apre Meta Business Suite per la gestione di pagine e risorse.")
@click.option("--open-ui", is_flag=True, default=True, help="Apre la finestra visibile.")
def suite_cmd(open_ui: bool):
    from meta.browser import launch_meta_browser
    click.echo(f"Apertura Meta Business Suite (Asset #{ASSET_ID})...")
    context = launch_meta_browser(headless=not open_ui)
    page = context.pages[0] if context.pages else context.new_page()
    page.goto(BM_HOME_URL)

    if open_ui:
        click.echo("La finestra rimarrà aperta finché non la chiudi o premi Ctrl+C.")
        try:
            while True:
                time.sleep(2)
                if not context.pages or all(p.is_closed() for p in context.pages):
                    break
        except KeyboardInterrupt:
            pass
        finally:
            try:
                context.close()
            except Exception:
                pass


if __name__ == "__main__":
    cli()

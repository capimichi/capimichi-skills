"""
Worldfilia Session & Login Commands.
"""

import time
import click


@click.group(name="session", help="Gestione sessione persistente e login browser Worldfilia.")
def session_group():
    pass


@session_group.command(name="login", help="Avvia il browser per il login (con compilazione automatica credenziali/TOTP se disponibili).")
@click.option("--visible", is_flag=True, default=True, help="Mostra il browser (default: True).")
def login_cmd(visible: bool):
    from worldfilia.login import main as run_login
    # Se visible è False possiamo gestire headless, altrimenti esegue interattivo
    run_login()


@session_group.command(name="status", help="Verifica se la sessione salvata nella directory XDG è autenticata.")
def status_cmd():
    from worldfilia.browser import launch_worldfilia_browser
    click.echo("Verifica sessione Worldfilia...")
    context = launch_worldfilia_browser(headless=True)
    try:
        page = context.new_page()
        page.goto("https://portal.worldfilia.net/publisher", wait_until="domcontentloaded", timeout=20000)
        time.sleep(2)
        if "publisher" in page.url and "login" not in page.url:
            click.echo("🟢 Sessione attiva e autenticata nella dashboard Worldfilia.")
        else:
            click.echo("🟡 Sessione non autenticata o scaduta. Esegui 'cli.py session login'.")
    finally:
        context.close()

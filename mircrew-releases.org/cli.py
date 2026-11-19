#!/usr/bin/env python3
"""
Mircrew Releases CLI Entrypoint.
Automazione e interazione con Mircrew-releases.org: login, ricerca release ed estrazione magnet tramite CloakBrowser.
"""

import sys
from pathlib import Path

# Assicura import del package corrente
current_dir = Path(__file__).resolve().parent
if str(current_dir.parent) not in sys.path:
    sys.path.insert(0, str(current_dir.parent))

try:
    import click
except ImportError:
    sys.exit("Errore: modulo 'click' non trovato. Installa le dipendenze richieste eseguendo: pip install click")


@click.group(help="CLI per la ricerca release ed estrazione magnet da Mircrew-releases.org.")
def cli():
    pass


@cli.command(name="status", help="Verifica se la sessione nel profilo persistente del browser è autenticata.")
@click.option("--headless", is_flag=True, default=False, help="Esegui in modalità headless.")
def status_cmd(headless: bool):
    try:
        from mircrew_releases_org.client import MircrewBrowser
    except ImportError:
        # Fallback direct import se eseguito come cartella con nome hyphenated
        import importlib.util
        client_path = current_dir / "client.py"
        spec = importlib.util.spec_from_file_location("client", str(client_path))
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        MircrewBrowser = mod.MircrewBrowser

    with MircrewBrowser(headless=headless) as browser:
        if browser.is_logged_in():
            click.echo("✅ Sessione attiva e autenticata su Mircrew.")
        else:
            click.echo("❌ Sessione non autenticata o scaduta. Esegui 'cli.py login'.")


@cli.command(name="login", help="Effettua o aggiorna il login salvando la sessione nel profilo persistente.")
@click.option("--username", "-u", default=None, help="Username Mircrew (default: da env MIRCREW_USERNAME o Bitwarden).")
@click.option("--password", "-p", default=None, help="Password Mircrew (default: da env MIRCREW_PASSWORD o Bitwarden).")
@click.option("--headless", is_flag=True, default=False, help="Esegui in modalità headless.")
def login_cmd(username: str, password: str, headless: bool):
    import importlib.util
    client_path = current_dir / "client.py"
    spec = importlib.util.spec_from_file_location("client", str(client_path))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    MircrewBrowser = mod.MircrewBrowser

    with MircrewBrowser(headless=headless) as browser:
        if browser.is_logged_in():
            click.echo("✅ Sei già autenticato su Mircrew!")
            return
        click.echo("Tentativo di autenticazione in corso...")
        try:
            ok = browser.login(username=username, password=password)
            if ok:
                click.echo("🎉 Login effettuato con successo! Sessione salvata nel profilo.")
            else:
                click.echo("❌ Login fallito. Controlla le credenziali o il captcha.")
        except Exception as e:
            click.echo(f"❌ Errore durante il login: {e}")


@cli.command(name="search", help="Cerca film, serie, musica o release sul tracker.")
@click.argument("query")
@click.option("--all-fields", is_flag=True, help="Cerca in tutti i campi (default: solo titolo del topic).")
@click.option("--limit", "-l", type=int, default=15, help="Numero massimo di risultati da mostrare (default: 15).")
@click.option("--magnets", is_flag=True, help="Estrae automaticamente i magnet del primo risultato.")
@click.option("--headless", is_flag=True, default=False, help="Esegui in modalità headless.")
def search_cmd(query: str, all_fields: bool, limit: int, magnets: bool, headless: bool):
    import importlib.util
    client_path = current_dir / "client.py"
    spec = importlib.util.spec_from_file_location("client", str(client_path))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    MircrewBrowser = mod.MircrewBrowser

    click.echo(f"🔎 Ricerca su Mircrew per: '{query}'...")
    with MircrewBrowser(headless=headless) as browser:
        results = browser.search(query, title_only=not all_fields, limit=limit)
        if not results:
            click.echo(f"Nessun risultato trovato per '{query}'.")
            return

        click.echo(f"\n✅ Trovati {len(results)} risultati:")
        click.echo("=" * 80)
        for idx, item in enumerate(results, 1):
            category_tag = f"[{item['forum']}] " if item['forum'] else ""
            click.echo(f"{idx:2d}. {category_tag}{item['title']}")
            click.echo(f"    Topic ID: {item['id']} | URL: {item['url']}")
        click.echo("=" * 80)

        if magnets and results:
            first = results[0]
            click.echo(f"\n🧲 Estrazione magnet per: {first['title']}...")
            details = browser.get_topic_details(first['url'], auto_thank=True)
            if details["magnets"]:
                click.echo(f"Trovati {len(details['magnets'])} magnet:")
                for m in details["magnets"]:
                    click.echo(f"  -> {m}")
            else:
                click.echo("Nessun link magnet trovato nel topic.")


@cli.command(name="magnets", help="Estrae i link magnet da un topic (ID numerico o URL completo).")
@click.argument("topic")
@click.option("--no-thank", is_flag=True, help="Non cliccare automaticamente sul tasto Ringrazia.")
@click.option("--headless", is_flag=True, default=False, help="Esegui in modalità headless.")
def magnets_cmd(topic: str, no_thank: bool, headless: bool):
    import importlib.util
    client_path = current_dir / "client.py"
    spec = importlib.util.spec_from_file_location("client", str(client_path))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    MircrewBrowser = mod.MircrewBrowser

    click.echo(f"🧲 Recupero dettagli per topic: {topic}...")
    with MircrewBrowser(headless=headless) as browser:
        details = browser.get_topic_details(topic, auto_thank=not no_thank)
        click.echo(f"\nTitolo: {details['title']}")
        click.echo(f"URL: {details['url']}")
        click.echo("=" * 80)

        if details["magnets"]:
            click.echo(f"\n✅ Trovati {len(details['magnets'])} link Magnet:")
            for idx, m in enumerate(details["magnets"], 1):
                click.echo(f"[{idx}] {m}")
        else:
            click.echo("\n⚠️ Nessun link Magnet trovato nel post.")

        if details["torrent_links"]:
            click.echo(f"\n📁 Trovati {len(details['torrent_links'])} link Torrent:")
            for idx, t in enumerate(details["torrent_links"], 1):
                click.echo(f"[{idx}] {t}")


if __name__ == "__main__":
    cli()

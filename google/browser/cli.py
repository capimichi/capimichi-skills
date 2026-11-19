#!/usr/bin/env python3
"""
Google & Web Browser CLI Entrypoint.
Automazione e navigazione stealth su Google e siti web tramite CloakBrowser.
"""

import sys
import json
from pathlib import Path

# Assicura import del modulo locale
current_dir = Path(__file__).resolve().parent
if str(current_dir) not in sys.path:
    sys.path.insert(0, str(current_dir))

try:
    import click
except ImportError:
    sys.exit("Errore: modulo 'click' non trovato. Installa le dipendenze richieste eseguendo: pip install click")


@click.group(help="CLI per la navigazione e ricerca web su Google tramite CloakBrowser.")
def cli():
    pass


# ---------------------------------------------------------------------------
# Sottocomando: search
# ---------------------------------------------------------------------------
@cli.command(name="search", help="Esegue una ricerca su Google ed estrae i risultati organici.")
@click.argument("query")
@click.option("--limit", "-l", type=int, default=10, help="Numero massimo di risultati da estrarre (default: 10).")
@click.option("--language", default="it", help="Codice lingua dei risultati (default: 'it').")
@click.option("--country", default="it", help="Codice geografico del paese (default: 'it').")
@click.option("--visible", is_flag=True, default=False, help="Mostra il browser durante la ricerca (non headless).")
@click.option("--json", "as_json", is_flag=True, default=False, help="Restituisce l'output in formato JSON.")
def search_cmd(query: str, limit: int, language: str, country: str, visible: bool, as_json: bool):
    from client import search_google

    results = search_google(
        query=query,
        limit=limit,
        headless=not visible,
        language=language,
        country=country,
    )

    if as_json:
        click.echo(json.dumps(results, indent=2, ensure_ascii=False))
        return

    click.echo("=" * 75)
    click.echo(f"🔎 RISULTATI GOOGLE SEARCH: '{query}' (Trovati: {len(results)})")
    click.echo("=" * 75)

    if not results:
        click.echo("Nessun risultato organico trovato o blocco temporaneo.")
        return

    for idx, item in enumerate(results, 1):
        click.echo(f"\n{idx:2d}. {item['title']}")
        click.echo(f"    🔗 {item['url']}")
        if item["snippet"]:
            click.echo(f"    📝 {item['snippet']}")

    click.echo("\n" + "=" * 75)


# ---------------------------------------------------------------------------
# Sottocomando: open
# ---------------------------------------------------------------------------
@cli.command(name="open", help="Apre un qualsiasi URL web con CloakBrowser stealth.")
@click.argument("url")
@click.option("--visible", is_flag=True, default=False, help="Mostra la finestra del browser.")
@click.option("--interactive", "-i", is_flag=True, default=False, help="Mantiene aperta la finestra per interazione manuale.")
@click.option("--wait", "-w", type=int, default=5, help="Secondi di attesa caricamento (default: 5s).")
@click.option("--screenshot", "-s", default=None, help="Nome file screenshot da salvare in ~/.cache/google-browser/.")
@click.option("--text", "extract_text", is_flag=True, default=False, help="Estrae e stampa il testo della pagina.")
def open_cmd(url: str, visible: bool, interactive: bool, wait: int, screenshot: str, extract_text: bool):
    from client import open_webpage

    # Se l'utente richiede interattività, forziamo visible=True
    is_visible = visible or interactive
    data = open_webpage(
        url=url,
        headless=not is_visible,
        wait_sec=wait,
        screenshot_name=screenshot,
        extract_text=extract_text,
        interactive=interactive,
    )

    click.echo(f"✅ Titolo pagina: {data['title']}")
    click.echo(f"🔗 URL finale:    {data['final_url']}")
    if data["screenshot"]:
        click.echo(f"📸 Screenshot:    {data['screenshot']}")

    if extract_text and data["text"]:
        click.echo("\n--- TESTO ESTRATTO (anteprima) ---")
        click.echo(data["text"][:1500])


# ---------------------------------------------------------------------------
# Sottocomando: inspect
# ---------------------------------------------------------------------------
@cli.command(name="inspect", help="Ispeziona metadati e selettori CSS di una pagina web.")
@click.argument("url")
@click.option("--selector", default=None, help="Selettore CSS da estrarre (es. 'h2', 'article a', '.product-price').")
@click.option("--visible", is_flag=True, default=False, help="Mostra il browser durante l'ispezione.")
@click.option("--json", "as_json", is_flag=True, default=False, help="Restituisce l'output in formato JSON.")
def inspect_cmd(url: str, selector: str, visible: bool, as_json: bool):
    from client import inspect_webpage

    data = inspect_webpage(url=url, selector=selector, headless=not visible)

    if as_json:
        click.echo(json.dumps(data, indent=2, ensure_ascii=False))
        return

    click.echo("=" * 75)
    click.echo(f"🔍 ISPEZIONE PAGINA: {data['title']}")
    click.echo(f"🔗 URL: {data['url']}")
    if data["description"]:
        click.echo(f"📝 Descrizione: {data['description']}")
    click.echo("=" * 75)

    if selector and data.get("elements"):
        click.echo(f"\nElementi trovati per '{selector}' ({len(data['elements'])}):")
        for el in data["elements"]:
            href_part = f" -> {el['href']}" if el.get("href") else ""
            click.echo(f"  [{el['index']}] {el['text']}{href_part}")
    elif data.get("headings"):
        click.echo("\nIntestazioni rilevate:")
        for h in data["headings"]:
            click.echo(f"  • {h}")

    click.echo("=" * 75)


# ---------------------------------------------------------------------------
# Gruppo di comandi: session
# ---------------------------------------------------------------------------
@cli.group(name="session", help="Gestione della sessione persistente e del profilo Google.")
def session_group():
    pass


@session_group.command(name="status", help="Verifica se il profilo locale ha un account Google autenticato.")
@click.option("--visible", is_flag=True, default=False, help="Mostra il browser durante il controllo.")
def session_status(visible: bool):
    from client import check_google_session

    click.echo("Verifica sessione Google in corso...")
    status = check_google_session(headless=not visible)
    if status["is_logged_in"]:
        click.echo(f"🟢 {status['account_info']}")
    else:
        click.echo(f"🟡 {status['account_info']}")
        click.echo("Puoi autenticarti eseguendo: python3 google/browser/cli.py session login")


@session_group.command(name="login", help="Apre una finestra visibile per effettuare il login manuale su Google.")
def session_login():
    from client import open_webpage

    click.echo("Apertura finestra di login su Google Accounts...")
    open_webpage(
        url="https://accounts.google.com/ServiceLogin",
        headless=False,
        interactive=True,
    )
    click.echo("Sessione browser aggiornata e salvata nel profilo XDG.")


if __name__ == "__main__":
    cli()

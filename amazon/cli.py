#!/usr/bin/env python3
"""
Amazon CLI Entrypoint.
Automazione e navigazione su Amazon.it con CloakBrowser: login, stato sessione, ricerca, ispezione prodotti, carrello e ordini.
"""

import sys
import json
from pathlib import Path

# Assicura import dei moduli locali
current_dir = Path(__file__).resolve().parent
if str(current_dir) not in sys.path:
    sys.path.insert(0, str(current_dir))

try:
    import click
except ImportError:
    sys.exit("Errore: modulo 'click' non trovato. Installa le dipendenze richieste eseguendo: pip install click")


@click.group(help="CLI per l'automazione e navigazione su Amazon.it.")
def cli():
    pass


@cli.command(name="login", help="Avvia il browser visibile per effettuare il login manuale su Amazon.it.")
def login_cmd():
    from login import run_manual_login
    run_manual_login()


@cli.command(name="status", help="Verifica se la sessione salvata nella directory XDG è autenticata.")
@click.option("--visible", is_flag=True, default=False, help="Mostra il browser invece di eseguire in headless.")
def status_cmd(visible: bool):
    from browser import launch_amazon_browser, check_amazon_login, accept_cookies_if_present, AMAZON_BASE_URL
    click.echo("Verifica stato di autenticazione...")
    context = launch_amazon_browser(headless=not visible)
    try:
        page = context.new_page()
        page.goto(AMAZON_BASE_URL, wait_until="domcontentloaded", timeout=20000)
        accept_cookies_if_present(page)
        status = check_amazon_login(page)
        if status["is_logged_in"]:
            click.echo(f"🟢 Sessione autenticata: {status['user_greeting']}")
        else:
            click.echo(f"🟡 Non autenticato: {status['user_greeting']}. Esegui 'cli.py login'.")
    finally:
        context.close()


@cli.command(name="search", help="Cerca prodotti su Amazon.it.")
@click.argument("query")
@click.option("--limit", "-l", type=int, default=10, help="Numero massimo di risultati da mostrare (default: 10).")
@click.option(
    "--sort",
    default="relevanceblender",
    type=click.Choice(["relevanceblender", "price-asc-rank", "price-desc-rank", "review-rank"]),
    help="Criterio di ordinamento.",
)
@click.option("--visible", is_flag=True, default=False, help="Mostra il browser durante l'esecuzione.")
@click.option("--json", "as_json", is_flag=True, default=False, help="Output in formato JSON.")
def search_cmd(query: str, limit: int, sort: str, visible: bool, as_json: bool):
    from search import search_amazon
    results = search_amazon(query=query, limit=limit, headless=not visible, sort=sort)

    if as_json:
        click.echo(json.dumps(results, indent=2, ensure_ascii=False))
        return

    click.echo("=" * 75)
    click.echo(f"🔍 RISULTATI RICERCA AMAZON.IT PER: '{query}' (Trovati: {len(results)})")
    click.echo("=" * 75)

    if not results:
        click.echo("Nessun prodotto trovato o pagina protetta da verifica.")
        return

    for idx, item in enumerate(results, start=1):
        prime_badge = " [⚡ Prime]" if item["is_prime"] else ""
        spon_badge = " [Sponsorizzato]" if item["is_sponsored"] else ""
        badge_str = f" [{item['badge']}]" if item["badge"] else ""

        click.echo(f"\n{idx}. {item['title'][:90]}...")
        click.echo(f"   💰 Prezzo: {item['price']}{prime_badge}{badge_str}{spon_badge}")
        click.echo(f"   ⭐ Valutazione: {item['rating']} ({item['reviews_count']} recensioni)")
        click.echo(f"   🆔 ASIN: {item['asin']}")
        if item["url"]:
            click.echo(f"   🔗 Link: {item['url']}")

    click.echo("\n" + "=" * 75)


@cli.command(name="inspect", help="Ispeziona un prodotto per ASIN (10 caratteri) o URL.")
@click.argument("target")
@click.option("--visible", is_flag=True, default=False, help="Mostra il browser durante l'esecuzione.")
@click.option("--json", "as_json", is_flag=True, default=False, help="Output in formato JSON.")
def inspect_cmd(target: str, visible: bool, as_json: bool):
    from inspect_product import inspect_product
    info = inspect_product(target, headless=not visible)

    if as_json:
        click.echo(json.dumps(info, indent=2, ensure_ascii=False))
        return

    click.echo("=" * 75)
    click.echo(f"📦 SCHEDA PRODOTTO: {info['title'] or 'Titolo non rilevato'}")
    click.echo("=" * 75)
    click.echo(f"🆔 ASIN:          {info['asin']}")
    click.echo(f"💰 Prezzo:        {info['price'] or 'N/D'}")
    click.echo(f"📦 Disponibilità: {info['availability'] or 'N/D'}")
    if info["seller"]:
        click.echo(f"🏪 Venditore:     {info['seller']}")
    if info["rating"]:
        click.echo(f"⭐ Valutazione:   {info['rating']} ({info['reviews_count']})")
    click.echo(f"🔗 Link:          {info['url']}")

    if info["bullet_points"]:
        click.echo("\n📝 Caratteristiche principali:")
        for pt in info["bullet_points"][:5]:
            click.echo(f"  • {pt}")
    click.echo("=" * 75)


@cli.command(name="cart", help="Mostra il contenuto e subtotale del carrello Amazon.it.")
@click.option("--visible", is_flag=True, default=False, help="Mostra il browser durante l'esecuzione.")
@click.option("--json", "as_json", is_flag=True, default=False, help="Output in formato JSON.")
def cart_cmd(visible: bool, as_json: bool):
    from cart import get_cart_contents
    data = get_cart_contents(headless=not visible)

    if as_json:
        click.echo(json.dumps(data, indent=2, ensure_ascii=False))
        return

    click.echo("=" * 70)
    click.echo("🛒 CARRELLO AMAZON.IT")
    click.echo("=" * 70)
    status_icon = "🟢 Connesso" if data["logged_in"] else "🟡 Anonimo / Non loggato"
    click.echo(f"Stato sessione:  {status_icon}")
    click.echo(f"Numero articoli: {data['items_count']}")
    click.echo(f"Subtotale:       {data['subtotal']}")
    click.echo("-" * 70)

    if not data["items"]:
        click.echo("Il carrello è vuoto.")
    else:
        for idx, item in enumerate(data["items"], 1):
            click.echo(f"{idx}. {item['title'][:80]}")
            click.echo(f"   💰 Prezzo: {item['price']}  |  🔢 Quantità: {item['quantity']}  |  🆔 ASIN: {item['asin']}")

    click.echo("=" * 70)


@cli.command(name="orders", help="Mostra gli ordini recenti su Amazon.it (richiede sessione autenticata).")
@click.option("--limit", "-l", type=int, default=5, help="Numero di ordini da mostrare (default: 5).")
@click.option("--visible", is_flag=True, default=False, help="Mostra il browser durante l'esecuzione.")
@click.option("--json", "as_json", is_flag=True, default=False, help="Output in formato JSON.")
def orders_cmd(limit: int, visible: bool, as_json: bool):
    from orders import get_amazon_orders
    data = get_amazon_orders(limit=limit, headless=not visible)

    if as_json:
        click.echo(json.dumps(data, indent=2, ensure_ascii=False))
        return

    click.echo("=" * 70)
    click.echo("📦 I MIEI ORDINI AMAZON.IT")
    click.echo("=" * 70)

    if not data["logged_in"]:
        click.echo("❌ Non risulti autenticato!")
        click.echo("Esegui prima il comando per effettuare il login manuale:")
        click.echo("  python3 amazon/cli.py login")
        click.echo("=" * 70)
        return

    click.echo(f"Ordini estratti: {data['orders_count']}")
    click.echo("-" * 70)

    if not data["orders"]:
        click.echo("Nessun ordine trovato nella pagina recente.")
    else:
        for idx, o in enumerate(data["orders"], 1):
            click.echo(f"\n{idx}. Ordine #{o['order_id'] or 'N/D'}")
            click.echo(f"   📅 Data: {o['order_date'] or 'N/D'}  |  💰 Totale: {o['total'] or 'N/D'}")
            if o["recipient"]:
                click.echo(f"   👤 Destinatario: {o['recipient']}")
            if o["items"]:
                click.echo("   Articoli:")
                for item in o["items"]:
                    click.echo(f"     • {item[:80]}")

    click.echo("\n" + "=" * 70)


if __name__ == "__main__":
    cli()

"""
Worldfilia Affiliate Links Commands.
"""

import click


@click.group(name="links", help="Consultazione link affiliato tracciati via API.")
def links_group():
    pass


@links_group.command(name="list", help="Elenca i link affiliato tracciati dell'utente.")
@click.option("--limit", "-l", type=int, default=15, help="Numero di link da mostrare (default: 15).")
def list_links(limit: int):
    from worldfilia.api_client import WorldfiliaAPI
    api = WorldfiliaAPI()

    click.echo("=" * 70)
    click.echo("WORLDFILIA - LINK AFFILIATO UTENTE (OFFICIAL API)")
    click.echo("=" * 70)

    links = api.get_links(take=limit, order_by={"id": "desc"})
    if not links:
        click.echo("Nessun link affiliato trovato.")
        return

    for l in links:
        lid = l.get("id")
        camp = l.get("Campaign") or {}
        landing = l.get("Landing") or {}
        sub1 = l.get("subid1") or ""
        sub2 = l.get("subid2") or ""
        domains = l.get("publisher_domains") or ""

        click.echo(f"🔗 [Link #{lid}] Campagna: {camp.get('name', 'N/D')} (Landing: {landing.get('name', 'N/D')})")
        if sub1 or sub2:
            click.echo(f"   SubID1: '{sub1}' | SubID2: '{sub2}'")
        if domains:
            click.echo(f"   Domini: {domains}")
        click.echo("-" * 70)

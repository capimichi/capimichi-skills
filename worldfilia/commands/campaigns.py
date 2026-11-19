"""
Worldfilia Campaigns Commands.
"""

import click


@click.group(name="campaigns", help="Gestione e consultazione campagne Worldfilia tramite API ufficiale.")
def campaigns_group():
    pass


@campaigns_group.command(name="list", help="Elenca le campagne disponibili con filtri opzionali.")
@click.option("--limit", "-l", type=int, default=15, help="Numero di campagne da mostrare (default: 15).")
@click.option("--search", "-s", type=str, help="Filtra per nome campagna.")
@click.option("--top", is_flag=True, help="Ordina per ranking decrescente.")
def list_campaigns(limit: int, search: str, top: bool):
    from worldfilia.api_client import WorldfiliaAPI
    api = WorldfiliaAPI()

    where = {"name": {"contains": search}} if search else None
    order_by = {"ranking_value": "desc"} if top else {"id": "desc"}

    click.echo("=" * 70)
    click.echo("WORLDFILIA - CAMPAGNE DISPONIBILI (OFFICIAL API)")
    click.echo("=" * 70)
    if search:
        click.echo(f"Filtro ricerca: '{search}'")
    click.echo(f"Ordinamento: {'Ranking decrescente' if top else 'ID decrescente'} | Limite: {limit}")
    click.echo("-" * 70)

    campaigns = api.get_campaigns(take=limit, where=where, order_by=order_by)
    if not campaigns:
        click.echo("Nessuna campagna trovata.")
        return

    for c in campaigns:
        cid = c.get("id")
        name = c.get("name")
        status = c.get("status")
        ranking = c.get("ranking_value", 0.0)
        categories = c.get("categories", "")
        landings = c.get("Landing") or []

        click.echo(f"📦 [#{cid}] {name}")
        click.echo(f"   Stato: {status} | Ranking: {ranking:.2f} | Categorie: {categories} | Landing: {len(landings)}")
        if landings:
            for l in landings[:3]:
                click.echo(f"     - Landing #{l.get('id')}: {l.get('name')} -> {l.get('url')}")

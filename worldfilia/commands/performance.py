"""
Worldfilia Performance & Reporting Commands.
"""

from datetime import date, timedelta
import click


@click.group(name="performance", help="Estrazione report e metriche di conversione via API REST.")
def performance_group():
    pass


@performance_group.command(name="report", help="Mostra metriche di performance aggregate per un periodo.")
@click.option("--today", is_flag=True, help="Mostra le performance di oggi.")
@click.option("--yesterday", is_flag=True, help="Mostra le performance di ieri.")
@click.option("--from-date", type=str, help="Data di inizio (YYYY-MM-DD).")
@click.option("--to-date", type=str, help="Data di fine (YYYY-MM-DD).")
@click.option("--campaign-id", type=int, help="Filtra per ID campagna specifica.")
def report_cmd(today: bool, yesterday: bool, from_date: str, to_date: str, campaign_id: int):
    from worldfilia.api_client import WorldfiliaAPI

    today_str = date.today().isoformat()
    yesterday_str = (date.today() - timedelta(days=1)).isoformat()

    date_from = from_date
    date_to = to_date

    if yesterday:
        date_from = yesterday_str
        date_to = yesterday_str
    elif today or (not date_from and not date_to):
        date_from = today_str
        date_to = today_str

    api = WorldfiliaAPI()

    click.echo("=" * 65)
    click.echo("WORLDFILIA - PERFORMANCE & CONVERSIONI (OFFICIAL REST API)")
    click.echo("=" * 65)
    click.echo(f"Periodo: {date_from} -> {date_to}")
    if campaign_id:
        click.echo(f"Filtro Campagna ID: #{campaign_id}")
    click.echo("-" * 65)

    res = api.get_performance(date_from=date_from, date_to=date_to, campaign_id=campaign_id)

    unique_clicks = res.get("uniqueClicks", 0)
    raw_clicks = res.get("rawClicks", 0)
    sales = res.get("sales", 0)
    leads = res.get("leads", 0)
    approved = res.get("approved", 0)
    rejected = res.get("rejected", 0)
    pending = res.get("pending", 0)
    commissions = res.get("commissions", 0.0)
    epc = res.get("epc", 0.0)
    cr = res.get("cr", 0.0)

    click.echo(f"  • Click Unici:        {unique_clicks} (Totali: {raw_clicks})")
    click.echo(f"  • Conversioni Totali: {sales + leads}")
    click.echo(f"    - Approvate:        {approved}")
    click.echo(f"    - In Attesa:        {pending}")
    click.echo(f"    - Rifiutate:        {rejected}")
    click.echo(f"  • Commissioni:        € {commissions:.2f}")
    click.echo(f"  • Conversion Rate:    {cr:.2f} %")
    click.echo(f"  • EPC:                € {epc:.3f}")
    click.echo("=" * 65)

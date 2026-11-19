#!/usr/bin/env python3
"""
Google Search Console CLI helper with Click.
"""

import datetime
import json
import sys

try:
    import click
except ImportError:
    sys.exit("Errore: modulo 'click' non trovato. Installa le dipendenze richieste eseguendo: pip install click")


def _get_client():
    try:
        import client
        return client
    except ImportError:
        sys.exit(
            "Errore: librerie Google non trovate. Installa le dipendenze richieste eseguendo:\n"
            "pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib"
        )


@click.group(help="CLI per ispezione URL, sitemap e performance su Google Search Console.")
def cli():
    pass


@cli.command("auth", help="Esegue l'autorizzazione OAuth via browser per generare il token.")
def cmd_auth():
    c = _get_client()
    c.get_credentials(force_auth=True)
    click.echo("Authentication successful! Token saved.")


@cli.command("sites", help="Elenca tutte le proprietà verificate in Search Console.")
@click.option("--json", "as_json", is_flag=True, help="Output in formato JSON.")
def cmd_sites(as_json):
    c = _get_client()
    _, webmasters = c.get_services()
    sites = c.list_sites(webmasters)

    if as_json:
        click.echo(json.dumps(sites, indent=2))
        return

    if not sites:
        click.echo("No properties found.")
        return

    click.echo(f"{'SITE URL':<45} | {'PERMISSION LEVEL'}")
    click.echo("-" * 65)
    for s in sites:
        click.echo(f"{s.get('siteUrl'):<45} | {s.get('permissionLevel', 'unknown')}")


@cli.command("inspect", help="Ispeziona un URL specifico (indicizzazione, copertura, canonical).")
@click.argument("url")
@click.option("--site", help="Search Console siteUrl (es. sc-domain:memispaintings.com).")
@click.option("--lang", default="it", help="Codice lingua per i messaggi (default: it).")
@click.option("--json", "as_json", is_flag=True, help="Output in formato JSON.")
def cmd_inspect(url, site, lang, as_json):
    c = _get_client()
    sc_service, webmasters = c.get_services()
    site_url = c.resolve_site_url(webmasters, site_arg=site, target_url=url)

    body = {
        "inspectionUrl": url,
        "siteUrl": site_url,
        "languageCode": lang,
    }

    try:
        res = sc_service.urlInspection().index().inspect(body=body).execute()
    except Exception as err:
        click.echo(f"API Error: {err}", err=True)
        sys.exit(1)

    result = res.get("inspectionResult", {})
    if as_json:
        click.echo(json.dumps(result, indent=2))
        return

    index_status = result.get("indexStatusResult", {})
    verdict = index_status.get("verdict", "UNKNOWN")
    coverage_state = index_status.get("coverageState", "Unknown")
    crawled_as = index_status.get("crawledAs", "Unknown")
    last_crawl = index_status.get("lastCrawlTime", "Never")
    page_fetch = index_status.get("pageFetchState", "Unknown")
    robots_txt = index_status.get("robotsTxtState", "Unknown")
    indexing_state = index_status.get("indexingState", "Unknown")
    user_canonical = index_status.get("userCanonical", "None")
    google_canonical = index_status.get("googleCanonical", "None")

    symbol = "🟢" if verdict == "PASS" else ("🟡" if verdict == "NEUTRAL" else "🔴")

    click.echo("\n" + "=" * 60)
    click.echo(f"Search Console URL Inspection: {url}")
    click.echo(f"Property: {site_url}")
    click.echo("=" * 60)
    click.echo(f"Verdict:           {symbol} {verdict}")
    click.echo(f"Coverage State:    {coverage_state}")
    click.echo(f"Crawled As:        {crawled_as}")
    click.echo(f"Last Crawl Time:   {last_crawl}")
    click.echo(f"Page Fetch State:  {page_fetch}")
    click.echo(f"Robots.txt State:  {robots_txt}")
    click.echo(f"Indexing State:    {indexing_state}")
    click.echo(f"User Canonical:    {user_canonical}")
    click.echo(f"Google Canonical:  {google_canonical}")

    mobile = result.get("mobileUsabilityResult", {})
    if mobile:
        m_verdict = mobile.get("verdict", "N/A")
        click.echo(f"Mobile Usability:  {m_verdict}")
    click.echo("=" * 60 + "\n")


@cli.command("sitemaps", help="Elenca le sitemap inviate e il loro stato.")
@click.option("--site", help="Search Console siteUrl.")
@click.option("--json", "as_json", is_flag=True, help="Output in formato JSON.")
def cmd_sitemaps(site, as_json):
    c = _get_client()
    _, webmasters = c.get_services()
    site_url = c.resolve_site_url(webmasters, site_arg=site)

    try:
        res = webmasters.sitemaps().list(siteUrl=site_url).execute()
    except Exception as err:
        click.echo(f"API Error: {err}", err=True)
        sys.exit(1)

    sitemaps = res.get("sitemap", [])
    if as_json:
        click.echo(json.dumps(sitemaps, indent=2))
        return

    if not sitemaps:
        click.echo(f"No sitemaps found for {site_url}.")
        return

    click.echo(f"\nSitemaps for {site_url}:")
    click.echo(f"{'PATH':<50} | {'LAST SUBMITTED':<20} | {'STATUS'}")
    click.echo("-" * 85)
    for sm in sitemaps:
        path = sm.get("path", "")
        last_sub = sm.get("lastSubmitted", "N/A")[:19]
        status = sm.get("status", "UNKNOWN")
        click.echo(f"{path:<50} | {last_sub:<20} | {status}")


@cli.command("sitemap-submit", help="Invia una sitemap a Search Console.")
@click.argument("feedpath")
@click.option("--site", help="Search Console siteUrl.")
def cmd_sitemap_submit(feedpath, site):
    c = _get_client()
    _, webmasters = c.get_services()
    site_url = c.resolve_site_url(webmasters, site_arg=site, target_url=feedpath)

    try:
        webmasters.sitemaps().submit(siteUrl=site_url, feedpath=feedpath).execute()
        click.echo(f"Successfully submitted sitemap '{feedpath}' to {site_url}!")
    except Exception as err:
        click.echo(f"Error submitting sitemap: {err}", err=True)
        sys.exit(1)


@cli.command("performance", help="Interroga i dati di rendimento della Ricerca Google.")
@click.option("--site", help="Search Console siteUrl.")
@click.option("--days", type=int, default=28, help="Numero di giorni da analizzare (default: 28).")
@click.option("--dimensions", default="query", help="Dimensioni separate da virgola (query, page, country, device).")
@click.option("--page", help="Filtra per specifico URL di pagina.")
@click.option("--limit", type=int, default=25, help="Numero massimo di righe da restituire (default: 25).")
@click.option("--json", "as_json", is_flag=True, help="Output in formato JSON.")
def cmd_performance(site, days, dimensions, page, limit, as_json):
    c = _get_client()
    sc_service, webmasters = c.get_services()
    site_url = c.resolve_site_url(webmasters, site_arg=site, target_url=page)

    end_date = datetime.date.today() - datetime.timedelta(days=2)
    start_date = end_date - datetime.timedelta(days=days)
    dim_list = [d.strip() for d in dimensions.split(",") if d.strip()]

    body = {
        "startDate": start_date.strftime("%Y-%m-%d"),
        "endDate": end_date.strftime("%Y-%m-%d"),
        "dimensions": dim_list,
        "rowLimit": limit,
    }

    if page:
        body["dimensionFilterGroups"] = [{
            "filters": [{
                "dimension": "page",
                "operator": "equals",
                "expression": page
            }]
        }]

    try:
        res = sc_service.searchanalytics().query(siteUrl=site_url, body=body).execute()
    except Exception as err:
        click.echo(f"API Error: {err}", err=True)
        sys.exit(1)

    rows = res.get("rows", [])
    if as_json:
        click.echo(json.dumps(rows, indent=2))
        return

    click.echo(f"\nSearch Performance ({start_date} to {end_date}) for {site_url}:")
    click.echo("=" * 80)
    click.echo(f"{'Keys':<45} | {'Clicks':>6} | {'Impr':>7} | {'CTR':>7} | {'Pos':>5}")
    click.echo("-" * 80)

    for r in rows:
        keys_str = " / ".join(r.get("keys", []))
        if len(keys_str) > 43:
            keys_str = keys_str[:40] + "..."
        clicks = r.get("clicks", 0)
        impressions = r.get("impressions", 0)
        ctr = f"{r.get('ctr', 0) * 100:.1f}%"
        position = f"{r.get('position', 0):.1f}"
        click.echo(f"{keys_str:<45} | {clicks:>6} | {impressions:>7} | {ctr:>7} | {position:>5}")
    click.echo("=" * 80)


if __name__ == "__main__":
    try:
        cli()
    except KeyboardInterrupt:
        sys.exit(130)

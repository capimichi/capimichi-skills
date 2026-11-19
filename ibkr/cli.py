#!/usr/bin/env python3
"""
Interactive Brokers CLI - Gestione e consultazione portafoglio (Sola lettura) con Click.
"""

import json
import sys
from pathlib import Path

try:
    import click
except ImportError:
    sys.exit("Errore: modulo 'click' non trovato. Installa le dipendenze richieste eseguendo: pip install click")

from client import (
    IBKRClient,
    IBKRClientError,
    IBKRAuthRequiredError,
    IBKRConnectionError,
)

try:
    from rich.console import Console
    from rich.table import Table
    console = Console()
    HAS_RICH = True
except ImportError:
    console = None
    HAS_RICH = False


def format_currency(val, currency="EUR"):
    if val is None or val == "":
        return "-"
    try:
        val_f = float(val)
        curr_str = f" {currency}" if currency and str(currency).lower() != "none" else ""
        return f"{val_f:,.2f}{curr_str}"
    except (ValueError, TypeError):
        return str(val)


def _get_client(ctx):
    gateway_url = ctx.obj.get("gateway_url")
    account = ctx.obj.get("account")
    return IBKRClient(base_url=gateway_url, account_id=account)


@click.group(help="CLI di consultazione portafoglio Interactive Brokers (Web API / Sola lettura).")
@click.option("--gateway-url", help="URL base del Gateway CPGW (default: https://localhost:5001).")
@click.option("--account", "-a", help="ID del conto IBKR (default: primo conto o IBKR_ACCOUNT_ID).")
@click.option("--json", "as_json", is_flag=True, help="Output grezzo in formato JSON.")
@click.pass_context
def cli(ctx, gateway_url, account, as_json):
    ctx.ensure_object(dict)
    ctx.obj["gateway_url"] = gateway_url
    ctx.obj["account"] = account
    ctx.obj["json"] = as_json


@cli.command("status", help="Verifica stato Gateway e autenticazione.")
@click.pass_context
def cmd_status(ctx):
    client = _get_client(ctx)
    as_json = ctx.obj["json"]
    try:
        status = client.check_status()
    except IBKRConnectionError as e:
        click.echo(f"❌ {e}", err=True)
        sys.exit(1)

    if as_json:
        click.echo(json.dumps(status, indent=2))
        return

    authenticated = status.get("authenticated", False)
    connected = status.get("connected", False)
    server_name = status.get("serverName", "N/A")
    competing = status.get("competing", False)

    if HAS_RICH:
        table = Table(title="Stato Gateway Interactive Brokers (CPGW)")
        table.add_column("Parametro", style="bold cyan")
        table.add_column("Valore", style="white")

        table.add_row("URL Gateway", client.base_url)
        table.add_row("Connesso a IBKR", "✅ Sì" if connected else "❌ No")
        table.add_row("Autenticato", "✅ Sì" if authenticated else "⚠️ No (Login richiesto)")
        table.add_row("Server", str(server_name))
        table.add_row("Sessione Concorrente", "Sì" if competing else "No")
        console.print(table)
    else:
        click.echo(f"Gateway URL: {client.base_url}")
        click.echo(f"Connesso: {'Sì' if connected else 'No'}")
        click.echo(f"Autenticato: {'Sì' if authenticated else 'No'}")
        click.echo(f"Server: {server_name}")

    if not authenticated:
        click.echo(f"\n👉 Per autenticarti, apri nel browser: {client.base_url}")
        click.echo("   Accedi con username, password e conferma il push 2FA (IB Key).")


@cli.command("accounts", help="Elenco conti IBKR.")
@click.pass_context
def cmd_accounts(ctx):
    client = _get_client(ctx)
    as_json = ctx.obj["json"]
    accounts = client.get_accounts()

    if as_json:
        click.echo(json.dumps(accounts, indent=2))
        return

    if not accounts:
        click.echo("Nessun conto trovato.")
        return

    if HAS_RICH:
        table = Table(title="Conti Interactive Brokers")
        table.add_column("Account ID", style="bold green")
        table.add_column("Tipo", style="white")
        table.add_column("Valuta Base", style="cyan")
        table.add_column("Descrizione / Alias", style="white")

        for acc in accounts:
            table.add_row(
                str(acc.get("id") or acc.get("accountId", "-")),
                str(acc.get("type", "-")),
                str(acc.get("currency", "-")),
                str(acc.get("accountVan") or acc.get("accountTitle", "-")),
            )
        console.print(table)
    else:
        for acc in accounts:
            click.echo(f"- ID: {acc.get('id') or acc.get('accountId')} | Valuta: {acc.get('currency')} | Tipo: {acc.get('type')}")


@cli.command("summary", help="Riepilogo finanziario (NAV, Cash, PnL).")
@click.pass_context
def cmd_summary(ctx):
    client = _get_client(ctx)
    as_json = ctx.obj["json"]
    acc_id = client.resolve_account_id(ctx.obj.get("account"))
    summary = client.get_summary(acc_id)

    if as_json:
        click.echo(json.dumps(summary, indent=2))
        return

    if HAS_RICH:
        table = Table(title=f"Riepilogo Portafoglio Conto [{acc_id}]")
        table.add_column("Metrica", style="bold cyan")
        table.add_column("Valore", style="white")

        keys_map = [
            ("netliquidation", "Net Liquidation Value (NAV)"),
            ("totalcashvalue", "Liquidità Totale (Cash)"),
            ("settledcash", "Liquidità Regolata (Settled Cash)"),
            ("buyingpower", "Potere d'Acquisto (Buying Power)"),
            ("grosspositionvalue", "Valore Lordo Posizioni"),
            ("stockmarketvalue", "Valore Mercato Azioni/ETF"),
            ("unrealizedpnl", "PnL Non Realizzato"),
            ("realizedpnl", "PnL Realizzato"),
            ("cushion", "Margine di Sicurezza (Cushion)"),
        ]

        for key, label in keys_map:
            item = summary.get(key)
            if item and isinstance(item, dict):
                val = item.get("amount") or item.get("value")
                curr = item.get("currency", "")
                table.add_row(label, format_currency(val, curr))
            elif key in summary:
                val = summary[key]
                table.add_row(label, format_currency(val, "") if isinstance(val, (int, float)) else str(val))

        console.print(table)
    else:
        click.echo(f"=== Riepilogo Conto {acc_id} ===")
        for k, v in summary.items():
            if isinstance(v, dict):
                click.echo(f"{k}: {v.get('amount') or v.get('value')} {v.get('currency', '')}")
            else:
                click.echo(f"{k}: {v}")


@cli.command("positions", help="Elenco posizioni aperte in portafoglio.")
@click.pass_context
def cmd_positions(ctx):
    client = _get_client(ctx)
    as_json = ctx.obj["json"]
    acc_id = client.resolve_account_id(ctx.obj.get("account"))
    positions = client.get_positions(acc_id)

    if as_json:
        click.echo(json.dumps(positions, indent=2))
        return

    if not positions:
        click.echo(f"Nessuna posizione aperta sul conto {acc_id}.")
        return

    if HAS_RICH:
        table = Table(title=f"Posizioni Aperte Conto [{acc_id}]")
        table.add_column("Ticker", style="bold green")
        table.add_column("Descrizione", style="white")
        table.add_column("Tipo", style="magenta")
        table.add_column("Q.tà", justify="right", style="cyan")
        table.add_column("Prezzo Medio", justify="right", style="white")
        table.add_column("Prezzo Attuale", justify="right", style="white")
        table.add_column("Valore Mercato", justify="right", style="bold")
        table.add_column("PnL Non Realizzato", justify="right")

        for pos in positions:
            ticker = (
                pos.get("ticker")
                or pos.get("contractDesc")
                or pos.get("description")
                or str(pos.get("conid", "-"))
            )
            desc = pos.get("companyName") or pos.get("description") or pos.get("contractDesc", "-")
            sec_type = pos.get("secType") or pos.get("assetClass", "-")
            qty = pos.get("position", 0)
            avg_cost = pos.get("avgCost") if pos.get("avgCost") is not None else pos.get("avgPrice", 0)
            mkt_price = pos.get("marketPrice") if pos.get("marketPrice") is not None else pos.get("mktPrice", 0)
            mkt_value = pos.get("marketValue") if pos.get("marketValue") is not None else pos.get("mktValue", 0)
            unrealized_pnl = pos.get("unrealizedPnl", 0)
            curr = pos.get("currency", "EUR")

            try:
                pnl_num = float(unrealized_pnl)
                pnl_style = "green" if pnl_num >= 0 else "red"
                pnl_str = f"[{pnl_style}]{format_currency(pnl_num, curr)}[/{pnl_style}]"
            except Exception:
                pnl_str = str(unrealized_pnl)

            try:
                qty_f = float(qty)
                qty_str = f"{qty_f:.4f}".rstrip("0").rstrip(".") if "." in f"{qty_f}" else f"{qty_f:,.0f}"
            except Exception:
                qty_str = str(qty)

            table.add_row(
                ticker,
                desc[:30] + "..." if len(desc) > 30 else desc,
                sec_type,
                qty_str,
                format_currency(avg_cost, curr),
                format_currency(mkt_price, curr),
                format_currency(mkt_value, curr),
                pnl_str,
            )
        console.print(table)
    else:
        for pos in positions:
            ticker = pos.get("ticker") or pos.get("description") or pos.get("conid")
            qty = pos.get("position")
            val = pos.get("marketValue") or pos.get("mktValue")
            pnl = pos.get("unrealizedPnl")
            curr = pos.get("currency", "EUR")
            click.echo(f"- {ticker}: Qty={qty} | Valore={val} {curr} | PnL={pnl} {curr}")


@cli.command("ledger", help="Saldi di cassa per valuta.")
@click.pass_context
def cmd_ledger(ctx):
    client = _get_client(ctx)
    as_json = ctx.obj["json"]
    acc_id = client.resolve_account_id(ctx.obj.get("account"))
    ledger = client.get_ledger(acc_id)

    if as_json:
        click.echo(json.dumps(ledger, indent=2))
        return

    if HAS_RICH:
        table = Table(title=f"Saldi di Cassa (Ledger) Conto [{acc_id}]")
        table.add_column("Valuta", style="bold cyan")
        table.add_column("Cash Saldo", justify="right", style="white")
        table.add_column("Cash Regolato", justify="right", style="white")
        table.add_column("Valore Azioni/Asset", justify="right", style="white")
        table.add_column("Net Liquidation", justify="right", style="bold green")

        for curr, data in ledger.items():
            if isinstance(data, dict):
                cash = format_currency(data.get("cashbalance"), curr)
                settled = format_currency(data.get("settledcash"), curr)
                stocks = format_currency(data.get("stockmarketvalue"), curr)
                net_liq = format_currency(data.get("netliquidationvalue"), curr)
                table.add_row(curr, cash, settled, stocks, net_liq)
        console.print(table)
    else:
        click.echo(json.dumps(ledger, indent=2))


@cli.command("trades", help="Eseguiti e transazioni recenti.")
@click.pass_context
def cmd_trades(ctx):
    client = _get_client(ctx)
    as_json = ctx.obj["json"]
    trades = client.get_trades()

    if as_json:
        click.echo(json.dumps(trades, indent=2))
        return

    if not trades:
        click.echo("Nessun eseguito recente trovato.")
        return

    if HAS_RICH:
        table = Table(title="Ordini Eseguiti Recenti (Trades)")
        table.add_column("ID / Simbolo", style="bold green")
        table.add_column("Operazione", style="magenta")
        table.add_column("Quantità", justify="right", style="white")
        table.add_column("Prezzo", justify="right", style="white")
        table.add_column("Data / Ora", style="cyan")

        for tr in trades:
            sym = tr.get("symbol") or tr.get("conid", "-")
            side = tr.get("side", "-")
            qty = tr.get("size", tr.get("execution_size", "-"))
            price = tr.get("price", "-")
            time_str = tr.get("trade_time_r") or tr.get("trade_time", "-")
            table.add_row(str(sym), str(side), str(qty), str(price), str(time_str))
        console.print(table)
    else:
        for tr in trades:
            click.echo(f"- {tr.get('symbol')} {tr.get('side')} Qty={tr.get('size')} @ {tr.get('price')} ({tr.get('trade_time')})")


@cli.command("tickle", help="Keep-alive ping per mantenere viva la sessione.")
@click.pass_context
def cmd_tickle(ctx):
    client = _get_client(ctx)
    as_json = ctx.obj["json"]
    res = client.tickle()
    if as_json:
        click.echo(json.dumps(res, indent=2))
    else:
        click.echo(f"Ping keep-alive inviato con successo. Dettagli: {res}")


if __name__ == "__main__":
    try:
        cli()
    except (IBKRAuthRequiredError, IBKRConnectionError, IBKRClientError) as e:
        sys.exit(f"❌ {e}")
    except KeyboardInterrupt:
        sys.exit(130)

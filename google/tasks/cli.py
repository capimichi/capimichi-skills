#!/usr/bin/env python3
"""
Google Tasks CLI Helper with Click.
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


@click.group(help="CLI per la gestione delle attività su Google Tasks.")
def cli():
    pass


@cli.command("auth", help="Verifica o esegue l'autenticazione OAuth.")
def cmd_auth():
    c = _get_client()
    c.get_service()
    click.echo("Authentication successful! Token is valid.")


@cli.command("lists", help="Elenca tutte le liste di attività.")
@click.option("--json", "as_json", is_flag=True, help="Output in formato JSON.")
def cmd_lists(as_json):
    c = _get_client()
    service = c.get_service()
    res = service.tasklists().list().execute()
    items = res.get("items", [])
    if as_json:
        click.echo(json.dumps(items, indent=2))
        return

    if not items:
        click.echo("No task lists found.")
        return

    click.echo(f"{'TITLE':<30} {'ID'}")
    click.echo("-" * 75)
    for item in items:
        title = item.get("title", "Untitled")
        click.echo(f"{title:<30} {item['id']}")


@cli.command("add-list", help="Crea una nuova lista di attività.")
@click.argument("title")
@click.option("--json", "as_json", is_flag=True, help="Output in formato JSON.")
def cmd_add_list(title, as_json):
    c = _get_client()
    service = c.get_service()
    res = service.tasklists().insert(body={"title": title}).execute()
    if as_json:
        click.echo(json.dumps(res, indent=2))
    else:
        click.echo(f"Created task list: '{res.get('title')}' (ID: {res.get('id')})")


@cli.command("delete-list", help="Elimina una lista di attività.")
@click.argument("list_id")
def cmd_delete_list(list_id):
    c = _get_client()
    service = c.get_service()
    lid = c.resolve_list_id(service, list_id)
    service.tasklists().delete(tasklist=lid).execute()
    click.echo(f"Deleted task list: {lid}")


@cli.command("list", help="Elenca i task in una lista.")
@click.option("--list", "-l", "list_name", default="@default", help="Titolo o ID della lista (default: @default).")
@click.option("--all", "-a", "show_all", is_flag=True, help="Includi anche i task completati.")
@click.option("--completed", "-c", is_flag=True, help="Mostra SOLO i task completati.")
@click.option("--json", "as_json", is_flag=True, help="Output in formato JSON.")
def cmd_list(list_name, show_all, completed, as_json):
    c = _get_client()
    service = c.get_service()
    list_id = c.resolve_list_id(service, list_name)
    show_completed = show_all or completed
    res = service.tasks().list(
        tasklist=list_id,
        showCompleted=show_completed,
        showHidden=show_completed
    ).execute()
    items = res.get("items", [])

    if not show_all:
        if completed:
            items = [t for t in items if t.get("status") == "completed"]
        else:
            items = [t for t in items if t.get("status") != "completed"]

    if as_json:
        click.echo(json.dumps(items, indent=2))
        return

    if not items:
        click.echo("No tasks found.")
        return

    for t in items:
        status = "[x]" if t.get("status") == "completed" else "[ ]"
        title = t.get("title", "(No title)")
        task_id = t.get("id")
        due = t.get("due")
        due_str = f" [Due: {due[:10]}]" if due else ""
        click.echo(f"{status} {title}{due_str} (ID: {task_id})")
        if t.get("notes"):
            for line in t["notes"].splitlines():
                click.echo(f"      {line}")


@cli.command("add", help="Aggiunge un nuovo task.")
@click.argument("title")
@click.option("--list", "-l", "list_name", default="@default", help="Titolo o ID della lista (default: @default).")
@click.option("--notes", "-n", help="Note o descrizione per il task.")
@click.option("--due", "-d", help="Scadenza (YYYY-MM-DD, 'today', 'tomorrow', '+Nd').")
@click.option("--json", "as_json", is_flag=True, help="Output in formato JSON.")
def cmd_add(title, list_name, notes, due, as_json):
    c = _get_client()
    service = c.get_service()
    list_id = c.resolve_list_id(service, list_name)
    body = {"title": title}
    if notes:
        body["notes"] = notes
    if due:
        body["due"] = c.parse_date(due)

    res = service.tasks().insert(tasklist=list_id, body=body).execute()
    if as_json:
        click.echo(json.dumps(res, indent=2))
    else:
        due_info = f" (due: {due})" if due else ""
        click.echo(f"Task added: '{res.get('title')}'{due_info} [ID: {res.get('id')}]")


@cli.command("done", help="Segna un task come completato.")
@click.argument("task_id")
@click.option("--list", "-l", "list_name", default="@default", help="Titolo o ID della lista (default: @default).")
@click.option("--json", "as_json", is_flag=True, help="Output in formato JSON.")
def cmd_done(task_id, list_name, as_json):
    c = _get_client()
    service = c.get_service()
    list_id = c.resolve_list_id(service, list_name)
    body = {
        "status": "completed",
        "completed": datetime.datetime.now(datetime.timezone.utc).isoformat()
    }
    res = service.tasks().patch(tasklist=list_id, task=task_id, body=body).execute()
    if as_json:
        click.echo(json.dumps(res, indent=2))
    else:
        click.echo(f"Marked as completed: '{res.get('title')}'")


@cli.command("undone", help="Segna un task come da fare (pending).")
@click.argument("task_id")
@click.option("--list", "-l", "list_name", default="@default", help="Titolo o ID della lista (default: @default).")
@click.option("--json", "as_json", is_flag=True, help="Output in formato JSON.")
def cmd_undone(task_id, list_name, as_json):
    c = _get_client()
    service = c.get_service()
    list_id = c.resolve_list_id(service, list_name)
    body = {
        "status": "needsAction",
        "completed": None
    }
    res = service.tasks().patch(tasklist=list_id, task=task_id, body=body).execute()
    if as_json:
        click.echo(json.dumps(res, indent=2))
    else:
        click.echo(f"Marked as pending: '{res.get('title')}'")


@cli.command("delete", help="Elimina un task.")
@click.argument("task_id")
@click.option("--list", "-l", "list_name", default="@default", help="Titolo o ID della lista (default: @default).")
def cmd_delete(task_id, list_name):
    c = _get_client()
    service = c.get_service()
    list_id = c.resolve_list_id(service, list_name)
    service.tasks().delete(tasklist=list_id, task=task_id).execute()
    click.echo(f"Deleted task: {task_id}")


@cli.command("clear", help="Rimuove tutti i task completati da una lista.")
@click.option("--list", "-l", "list_name", default="@default", help="Titolo o ID della lista (default: @default).")
def cmd_clear(list_name):
    c = _get_client()
    service = c.get_service()
    list_id = c.resolve_list_id(service, list_name)
    service.tasks().clear(tasklist=list_id).execute()
    click.echo("Cleared all completed tasks.")


@cli.command("search", help="Cerca task per testo attraverso tutte le liste.")
@click.argument("query")
@click.option("--json", "as_json", is_flag=True, help="Output in formato JSON.")
def cmd_search(query, as_json):
    c = _get_client()
    service = c.get_service()
    q = query.lower()

    tasklists = service.tasklists().list().execute().get("items", [])
    matching_tasks = []

    for tl in tasklists:
        tl_id = tl["id"]
        tl_title = tl.get("title", "Untitled")
        try:
            tasks = service.tasks().list(tasklist=tl_id, showCompleted=True, showHidden=True).execute().get("items", [])
            for t in tasks:
                title = t.get("title", "")
                notes = t.get("notes", "")
                if q in title.lower() or q in notes.lower():
                    matching_tasks.append((tl_title, t))
        except Exception:
            continue

    if as_json:
        click.echo(json.dumps([t for _, t in matching_tasks], indent=2))
        return

    if not matching_tasks:
        click.echo(f"No tasks matching '{query}' found.")
        return

    click.echo(f"Found {len(matching_tasks)} matching task(s):")
    for tl_title, t in matching_tasks:
        status = "[x]" if t.get("status") == "completed" else "[ ]"
        title = t.get("title", "(No title)")
        due = t.get("due")
        due_str = f" [Due: {due[:10]}]" if due else ""
        click.echo(f"{status} [{tl_title}] {title}{due_str} (ID: {t.get('id')})")
        if t.get("notes"):
            for line in t["notes"].splitlines():
                click.echo(f"      {line}")


if __name__ == "__main__":
    try:
        cli()
    except KeyboardInterrupt:
        sys.exit(130)

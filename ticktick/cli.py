#!/usr/bin/env python3
"""
TickTick CLI - Gestione Liste e Attività con Click.
"""

import json
import sys

try:
    import click
except ImportError:
    sys.exit("Errore: modulo 'click' non trovato. Installa le dipendenze richieste eseguendo: pip install click")

from client import (
    get_projects,
    find_project,
    request,
    parse_date
)


@click.group(help="CLI per la gestione di attività e liste su TickTick.")
def cli():
    pass


@cli.command("lists", help="Elenca tutte le liste e i progetti.")
@click.option("--json", "as_json", is_flag=True, help="Output in formato JSON.")
def cmd_lists(as_json):
    projects = get_projects()
    if as_json:
        click.echo(json.dumps(projects, indent=2, ensure_ascii=False))
        return

    if not projects:
        click.echo("Nessuna lista trovata su TickTick.")
        return

    click.echo(f"Trovate {len(projects)} liste/progetti:")
    for p in projects:
        kind = f" [{p.get('kind', 'TASK')}]" if p.get('kind') != 'TASK' else ""
        click.echo(f"  • {p['name']} (ID: {p['id']}){kind}")


@cli.command("tasks", help="Elenca le attività (con filtri per lista e stato).")
@click.option("--list", "-l", "list_name", help="Nome o ID della lista (default: tutte).")
@click.option("--all", "-a", "show_all", is_flag=True, help="Includi sia completate che attive.")
@click.option("--completed", "-c", is_flag=True, help="Mostra solo le completate.")
@click.option("--json", "as_json", is_flag=True, help="Output in formato JSON.")
def cmd_tasks(list_name, show_all, completed, as_json):
    projects = get_projects()
    if list_name:
        selected_project = find_project(list_name, projects)
        if not selected_project:
            click.echo(f"[ERRORE] Lista/progetto '{list_name}' non trovato.", err=True)
            sys.exit(1)
        target_projects = [selected_project]
    else:
        target_projects = projects

    all_tasks = []
    for p in target_projects:
        try:
            p_data = request("GET", f"/project/{p['id']}/data")
            tasks = p_data.get("tasks", [])
            for t in tasks:
                t["_projectName"] = p["name"]
                all_tasks.append(t)
        except Exception as e:
            if list_name:
                click.echo(f"[Warning] Impossibile recuperare task da {p['name']}: {e}", err=True)

    if not show_all:
        if completed:
            all_tasks = [t for t in all_tasks if t.get("status", 0) != 0]
        else:
            all_tasks = [t for t in all_tasks if t.get("status", 0) == 0]

    if as_json:
        click.echo(json.dumps(all_tasks, indent=2, ensure_ascii=False))
        return

    if not all_tasks:
        filter_desc = "completate" if completed else "attive"
        click.echo(f"Nessuna attività ({filter_desc}) trovata.")
        return

    click.echo(f"\nAttività trovate ({len(all_tasks)}):")
    for t in all_tasks:
        status_icon = "✓" if t.get("status", 0) != 0 else "○"
        due = f" [Scadenza: {t['dueDate']}]" if t.get("dueDate") else ""
        priority = f" [Prio: {t['priority']}]" if t.get("priority", 0) > 0 else ""
        proj = f" ({t.get('_projectName')})" if not list_name else ""
        click.echo(f"  {status_icon} {t['title']}{proj}{due}{priority} (ID: {t['id']})")
        if t.get("content"):
            for line in t["content"].strip().split("\n"):
                click.echo(f"      {line}")


@cli.command("add", help="Crea una nuova attività.")
@click.argument("title")
@click.option("--list", "-l", "list_name", help="Nome o ID della lista (default: Inbox).")
@click.option("--due", "-d", help="Scadenza (es. 'today', 'tomorrow 15:30', 'domani 09:00', '2026-11-20 18:00').")
@click.option("--all-day", is_flag=True, help="Imposta l'attività per l'intera giornata.")
@click.option("--notes", "-n", help="Note o descrizione dettagliata.")
@click.option("--priority", "-p", type=click.Choice(["0", "1", "3", "5"]), default="0", help="Priorità: 0 (Nessuna), 1 (Bassa), 3 (Media), 5 (Alta).")
@click.option("--remind", "-r", help="Promemoria (es. '0' all'orario, '15' per 15 min prima, o '0,15').")
@click.option("--json", "as_json", is_flag=True, help="Output in formato JSON.")
def cmd_add(title, list_name, due, all_day, notes, priority, remind, as_json):
    projects = get_projects()
    if list_name:
        p = find_project(list_name, projects)
        if not p:
            click.echo(f"[ERRORE] Lista '{list_name}' non trovata.", err=True)
            sys.exit(1)
        target_project_id = p["id"]
    else:
        target_project_id = "inbox"

    due_formatted, is_all_day = parse_date(due) if due else (None, False)

    payload = {
        "title": title,
        "content": notes or "",
        "priority": int(priority)
    }
    if target_project_id:
        payload["projectId"] = target_project_id
    if due_formatted:
        payload["dueDate"] = due_formatted
        payload["isAllDay"] = is_all_day or all_day

    if remind:
        reminders = []
        for r in remind.split(","):
            r = r.strip()
            if r.startswith("TRIGGER:"):
                reminders.append(r)
            elif r in ("0", "on_time"):
                reminders.append("TRIGGER:PT0S")
            else:
                reminders.append(f"TRIGGER:-PT{r}M")
        payload["reminders"] = reminders

    res = request("POST", "/task", json_data=payload)
    if as_json:
        click.echo(json.dumps(res, indent=2, ensure_ascii=False))
    else:
        click.echo(f"✓ Attività creata con successo! (ID: {res.get('id')})")
        click.echo(f"  Titolo: {res.get('title')}")
        if res.get('dueDate'):
            click.echo(f"  Scadenza: {res.get('dueDate')}")


@cli.command("done", help="Contrassegna un'attività come completata.")
@click.argument("task_id")
@click.option("--project", "-p", "project_id", help="ID del progetto (opzionale, rilevato automaticamente).")
def cmd_done(task_id, project_id):
    if not project_id:
        projects = get_projects()
        for p in projects:
            p_data = request("GET", f"/project/{p['id']}/data")
            for t in p_data.get("tasks", []):
                if t["id"] == task_id:
                    project_id = p["id"]
                    break
            if project_id:
                break

    if not project_id:
        click.echo(f"[ERRORE] Impossibile individuare il progetto per il task {task_id}. Specificalo con --project.", err=True)
        sys.exit(1)

    request("POST", f"/project/{project_id}/task/{task_id}/complete")
    click.echo(f"✓ Attività {task_id} contrassegnata come completata!")


@cli.command("delete", help="Elimina un'attività.")
@click.argument("task_id")
@click.option("--project", "-p", "project_id", help="ID del progetto (opzionale, rilevato automaticamente).")
def cmd_delete(task_id, project_id):
    if not project_id:
        projects = get_projects()
        for p in projects:
            p_data = request("GET", f"/project/{p['id']}/data")
            for t in p_data.get("tasks", []):
                if t["id"] == task_id:
                    project_id = p["id"]
                    break
            if project_id:
                break

    if not project_id:
        click.echo(f"[ERRORE] Impossibile individuare il progetto per il task {task_id}. Specificalo con --project.", err=True)
        sys.exit(1)

    request("DELETE", f"/project/{project_id}/task/{task_id}")
    click.echo(f"✓ Attività {task_id} eliminata con successo!")


@cli.command("add-list", help="Crea una nuova lista/progetto.")
@click.argument("name")
@click.option("--color", help="Colore esadecimale (es. '#F18181').")
@click.option("--view-mode", type=click.Choice(["list", "kanban", "timeline"]), default="list", help="Modalità di visualizzazione.")
@click.option("--json", "as_json", is_flag=True, help="Output in formato JSON.")
def cmd_add_list(name, color, view_mode, as_json):
    payload = {
        "name": name,
        "viewMode": view_mode
    }
    if color:
        payload["color"] = color
    res = request("POST", "/project", json_data=payload)
    if as_json:
        click.echo(json.dumps(res, indent=2, ensure_ascii=False))
    else:
        click.echo(f"✓ Lista/progetto creata con successo! (ID: {res.get('id')}, Nome: {res.get('name')})")


@cli.command("delete-list", help="Elimina una lista/progetto.")
@click.argument("name_or_id")
def cmd_delete_list(name_or_id):
    project = find_project(name_or_id, projects=get_projects(include_inbox=False), exact=True)
    if not project:
        click.echo(f"[ERRORE] Progetto/lista '{name_or_id}' non trovato (serve nome esatto o ID).", err=True)
        sys.exit(1)

    request("DELETE", f"/project/{project['id']}")
    click.echo(f"✓ Lista/progetto '{project['name']}' (ID: {project['id']}) eliminata con successo!")


if __name__ == "__main__":
    try:
        cli()
    except KeyboardInterrupt:
        sys.exit(130)

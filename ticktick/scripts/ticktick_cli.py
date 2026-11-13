#!/usr/bin/env python3
"""
TickTick CLI Helper
Permette di interagire con le Open API di TickTick (https://api.ticktick.com/open/v1).
Utilizza il token salvato nelle variabili d'ambiente (TICKTICK_API_KEY / TICKTICK_TOKEN)
o lo estrae automaticamente da ~/.config/zsh/envs/personal.zsh.
"""

import os
import sys
import json
import re
import argparse
from datetime import datetime, timedelta, timezone
import requests

BASE_URL = "https://api.ticktick.com/open/v1"

def get_api_token():
    # 1. Verifica nelle env correnti
    token = os.environ.get("TICKTICK_API_KEY") or os.environ.get("TICKTICK_TOKEN") or os.environ.get("TICKTICK_API_TOKEN")
    if token:
        return token.strip().strip('"').strip("'")
    
    # 2. Fallback: lettura automatica da ~/.config/zsh/envs/personal.zsh
    env_file = os.path.expanduser("~/.config/zsh/envs/personal.zsh")
    if os.path.exists(env_file):
        try:
            with open(env_file, "r") as f:
                for line in f:
                    m = re.match(r'^\s*export\s+TICKTICK_(?:API_KEY|TOKEN|API_TOKEN)=["\']?([^"\'\s]+)["\']?', line)
                    if m:
                        return m.group(1).strip()
        except Exception:
            pass

    print("[ERRORE] TICKTICK_API_KEY non trovata nelle variabili d'ambiente né in ~/.config/zsh/envs/personal.zsh", file=sys.stderr)
    print("Assicurati di aver impostato l'item in Bitwarden e applicato chezmoi.", file=sys.stderr)
    sys.exit(1)

def request(method, endpoint, params=None, json_data=None):
    token = get_api_token()
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    url = f"{BASE_URL}{endpoint}"
    resp = requests.request(method, url, headers=headers, params=params, json=json_data)
    if resp.status_code == 204:
        return {}
    if resp.status_code >= 400:
        print(f"[ERRORE API {resp.status_code}]: {resp.text}", file=sys.stderr)
        resp.raise_for_status()
    return resp.json() if resp.text else {}

def get_projects():
    return request("GET", "/project")

def find_project(name_or_id, projects=None):
    if not name_or_id:
        return None
    if projects is None:
        projects = get_projects()
    # Match esatto per ID
    for p in projects:
        if p["id"] == name_or_id:
            return p
    # Match case-insensitive per nome (anche parziale o ignorando emoji)
    query = name_or_id.lower().strip()
    for p in projects:
        p_name = p.get("name", "").lower()
        if query == p_name or query in p_name:
            return p
    return None

def parse_date(date_str):
    """
    Interpreta espressioni come:
    - 'today', 'tomorrow', 'oggi', 'domani'
    - 'today 15:30', 'domani 09:00', '18:00'
    - '+2d', '+1d 12:00'
    - 'YYYY-MM-DD' o 'YYYY-MM-DD HH:MM'
    Ritorna: (iso_date_string, is_all_day)
    """
    if not date_str:
        return None, False

    s = date_str.strip().lower()
    now = datetime.now().astimezone()
    target_dt = None
    is_all_day = False

    # Estrazione eventuale orario HH:MM
    time_match = re.search(r'(\d{1,2}):(\d{2})', s)
    hour, minute = (None, None)
    if time_match:
        hour = int(time_match.group(1))
        minute = int(time_match.group(2))
        s = re.sub(r'\s*\d{1,2}:\d{2}\s*', ' ', s).strip()

    if s in ("oggi", "today", ""):
        target_dt = now
    elif s in ("domani", "tomorrow"):
        target_dt = now + timedelta(days=1)
    elif s.startswith("+") and "d" in s:
        days_str = s.replace("+", "").replace("d", "").strip()
        try:
            days = int(days_str)
            target_dt = now + timedelta(days=days)
        except ValueError:
            target_dt = now
    else:
        # Tentativo parsing ISO
        for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d %H:%M"):
            try:
                target_dt = datetime.strptime(s, fmt).astimezone()
                break
            except ValueError:
                pass

    if not target_dt:
        try:
            # Fallback generico
            target_dt = datetime.fromisoformat(date_str).astimezone()
        except Exception:
            print(f"[Warning] Impossibile interpretare la data '{date_str}', ignorata.", file=sys.stderr)
            return None, False

    if hour is not None and minute is not None:
        target_dt = target_dt.replace(hour=hour, minute=minute, second=0, microsecond=0)
        is_all_day = False
    elif "today" in date_str or "oggi" in date_str or "domani" in date_str or "tomorrow" in date_str or re.match(r'^\d{4}-\d{2}-\d{2}$', date_str.strip()):
        is_all_day = True
        target_dt = target_dt.replace(hour=9, minute=0, second=0, microsecond=0)

    # Formato TickTick: yyyy-MM-dd'T'HH:mm:ssZ (es. 2026-11-13T15:30:00+0100)
    formatted = target_dt.strftime("%Y-%m-%dT%H:%M:%S%z")
    return formatted, is_all_day

# --- COMANDI CLI ---

def cmd_lists(args):
    projects = get_projects()
    if args.json:
        print(json.dumps(projects, indent=2, ensure_ascii=False))
        return

    if not projects:
        print("Nessuna lista trovata su TickTick.")
        return

    print(f"Trovate {len(projects)} liste/progetti:")
    for p in projects:
        kind = f" [{p.get('kind', 'TASK')}]" if p.get('kind') != 'TASK' else ""
        print(f"  • {p['name']} (ID: {p['id']}){kind}")

def cmd_tasks(args):
    projects = get_projects()
    selected_project = None
    if args.list:
        selected_project = find_project(args.list, projects)
        if not selected_project:
            print(f"[ERRORE] Lista/progetto '{args.list}' non trovato.", file=sys.stderr)
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
            if args.list:
                print(f"[Warning] Impossibile recuperare task da {p['name']}: {e}", file=sys.stderr)

    # Filtraggio
    if not args.all:
        if args.completed:
            all_tasks = [t for t in all_tasks if t.get("status", 0) != 0]
        else:
            all_tasks = [t for t in all_tasks if t.get("status", 0) == 0]

    if args.json:
        print(json.dumps(all_tasks, indent=2, ensure_ascii=False))
        return

    if not all_tasks:
        filter_desc = "completate" if args.completed else "attive"
        print(f"Nessuna attività ({filter_desc}) trovata.")
        return

    print(f"\nAttività trovate ({len(all_tasks)}):")
    for t in all_tasks:
        status_icon = "✓" if t.get("status", 0) != 0 else "○"
        due = f" [Scadenza: {t['dueDate']}]" if t.get("dueDate") else ""
        priority = f" [Prio: {t['priority']}]" if t.get("priority", 0) > 0 else ""
        proj = f" ({t.get('_projectName')})" if not args.list else ""
        print(f"  {status_icon} {t['title']}{proj}{due}{priority} (ID: {t['id']})")
        if t.get("content"):
            for line in t["content"].strip().split("\n"):
                print(f"      {line}")

def cmd_add(args):
    projects = get_projects()
    target_project_id = None
    if args.list:
        p = find_project(args.list, projects)
        if not p:
            print(f"[ERRORE] Lista '{args.list}' non trovata.", file=sys.stderr)
            sys.exit(1)
        target_project_id = p["id"]
    elif projects:
        # Se non specificato, usa la prima lista o cerca Memo/Inbox
        memo = find_project("Memo", projects) or find_project("Inbox", projects)
        target_project_id = memo["id"] if memo else projects[0]["id"]

    due_formatted, is_all_day = parse_date(args.due) if args.due else (None, False)

    payload = {
        "title": args.title,
        "content": args.notes or "",
        "priority": args.priority
    }
    if target_project_id:
        payload["projectId"] = target_project_id
    if due_formatted:
        payload["dueDate"] = due_formatted
        payload["isAllDay"] = is_all_day or args.all_day

    # Promemoria facoltativi (es. TRIGGER:PT0S = all'orario, TRIGGER:-PT15M = 15m prima)
    if args.remind:
        reminders = []
        for r in args.remind.split(","):
            r = r.strip()
            if r.startswith("TRIGGER:"):
                reminders.append(r)
            elif r == "0" or r == "on_time":
                reminders.append("TRIGGER:PT0S")
            else:
                reminders.append(f"TRIGGER:-PT{r}M")
        payload["reminders"] = reminders

    res = request("POST", "/task", json_data=payload)
    if args.json:
        print(json.dumps(res, indent=2, ensure_ascii=False))
    else:
        print(f"✓ Attività creata con successo! (ID: {res.get('id')})")
        print(f"  Titolo: {res.get('title')}")
        if res.get('dueDate'):
            print(f"  Scadenza: {res.get('dueDate')}")

def cmd_done(args):
    task_id = args.task_id
    project_id = args.project_id

    # Se project_id non fornito, cerca il task tra i progetti
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
        print(f"[ERRORE] Impossibile individuare il progetto per il task {task_id}. Specificalo con --project.", file=sys.stderr)
        sys.exit(1)

    request("POST", f"/project/{project_id}/task/{task_id}/complete")
    print(f"✓ Attività {task_id} contrassegnata come completata!")

def cmd_delete(args):
    task_id = args.task_id
    project_id = args.project_id

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
        print(f"[ERRORE] Impossibile individuare il progetto per il task {task_id}. Specificalo con --project.", file=sys.stderr)
        sys.exit(1)

    request("DELETE", f"/project/{project_id}/task/{task_id}")
    print(f"✓ Attività {task_id} eliminata con successo!")

def cmd_add_list(args):
    payload = {
        "name": args.name,
        "viewMode": args.view_mode
    }
    if args.color:
        payload["color"] = args.color
    res = request("POST", "/project", json_data=payload)
    if args.json:
        print(json.dumps(res, indent=2, ensure_ascii=False))
    else:
        print(f"✓ Lista/progetto creata con successo! (ID: {res.get('id')}, Nome: {res.get('name')})")

def cmd_delete_list(args):
    project = find_project(args.name_or_id)
    if not project:
        print(f"[ERRORE] Progetto/lista '{args.name_or_id}' non trovato.", file=sys.stderr)
        sys.exit(1)

    request("DELETE", f"/project/{project['id']}")
    print(f"✓ Lista/progetto '{project['name']}' (ID: {project['id']}) eliminata con successo!")

def main():
    parser = argparse.ArgumentParser(description="TickTick Open API CLI Client")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # lists
    p_lists = subparsers.add_parser("lists", aliases=["projects"], help="Elenca tutte le liste/progetti")
    p_lists.add_argument("--json", action="store_true", help="Output in formato JSON")
    p_lists.set_defaults(func=cmd_lists)

    # tasks
    p_tasks = subparsers.add_parser("tasks", aliases=["list"], help="Elenca le attività")
    p_tasks.add_argument("--list", "-l", help="Nome o ID della lista")
    p_tasks.add_argument("--all", "-a", action="store_true", help="Includi sia completate che attive")
    p_tasks.add_argument("--completed", "-c", action="store_true", help="Mostra solo le completate")
    p_tasks.add_argument("--json", action="store_true", help="Output in formato JSON")
    p_tasks.set_defaults(func=cmd_tasks)

    # add
    p_add = subparsers.add_parser("add", help="Crea una nuova attività")
    p_add.add_argument("title", help="Titolo dell'attività")
    p_add.add_argument("--list", "-l", help="Nome o ID della lista (default: prima lista o Memo)")
    p_add.add_argument("--due", "-d", help="Scadenza (es. 'today', 'tomorrow 15:30', 'domani 09:00', '2026-11-20 18:00')")
    p_add.add_argument("--all-day", action="store_true", help="Imposta l'attività per l'intera giornata")
    p_add.add_argument("--notes", "-n", help="Note o descrizione dettagliata")
    p_add.add_argument("--priority", "-p", type=int, choices=[0, 1, 3, 5], default=0, help="Priorità: 0 (Nessuna), 1 (Bassa), 3 (Media), 5 (Alta)")
    p_add.add_argument("--remind", "-r", help="Promemoria (es. '0' per all'orario, '15' per 15 min prima, o '0,15')")
    p_add.add_argument("--json", action="store_true", help="Output in formato JSON")
    p_add.set_defaults(func=cmd_add)

    # done
    p_done = subparsers.add_parser("done", aliases=["complete"], help="Contrassegna un'attività come completata")
    p_done.add_argument("task_id", help="ID dell'attività")
    p_done.add_argument("--project", "-p", dest="project_id", help="ID del progetto (opzionale)")
    p_done.set_defaults(func=cmd_done)

    # delete
    p_del = subparsers.add_parser("delete", help="Elimina un'attività")
    p_del.add_argument("task_id", help="ID dell'attività")
    p_del.add_argument("--project", "-p", dest="project_id", help="ID del progetto (opzionale)")
    p_del.set_defaults(func=cmd_delete)

    # add-list
    p_addl = subparsers.add_parser("add-list", help="Crea una nuova lista/progetto")
    p_addl.add_argument("name", help="Nome della lista")
    p_addl.add_argument("--color", help="Colore esadecimale (es. '#F18181')")
    p_addl.add_argument("--view-mode", choices=["list", "kanban", "timeline"], default="list")
    p_addl.add_argument("--json", action="store_true", help="Output JSON")
    p_addl.set_defaults(func=cmd_add_list)

    # delete-list
    p_dell = subparsers.add_parser("delete-list", help="Elimina una lista/progetto")
    p_dell.add_argument("name_or_id", help="Nome o ID della lista da eliminare")
    p_dell.set_defaults(func=cmd_delete_list)

    args = parser.parse_args()
    args.func(args)

if __name__ == "__main__":
    main()

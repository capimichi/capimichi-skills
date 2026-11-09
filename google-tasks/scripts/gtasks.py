#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "google-api-python-client>=2.100.0",
#     "google-auth-httplib2>=0.2.0",
#     "google-auth-oauthlib>=1.2.0",
# ]
# ///

import argparse
import datetime
import json
import os
import sys
from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

SCOPES = ["https://www.googleapis.com/auth/tasks"]

CONFIG_DIR = Path(os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config")) / "google-tasks"
STATE_DIR = Path(os.environ.get("XDG_STATE_HOME", Path.home() / ".local" / "state")) / "google-tasks"
CREDENTIALS_FILE = Path(os.environ.get("GOOGLE_TASKS_CREDENTIALS", CONFIG_DIR / "credentials.json"))
TOKEN_FILE = Path(os.environ.get("GOOGLE_TASKS_TOKEN", STATE_DIR / "token.json"))

# Fallback: check legacy config dir if token not in state dir
if not TOKEN_FILE.exists() and (CONFIG_DIR / "token.json").exists():
    TOKEN_FILE = CONFIG_DIR / "token.json"


def get_credentials():
    creds = None
    if TOKEN_FILE.exists():
        try:
            creds = Credentials.from_authorized_user_file(str(TOKEN_FILE), SCOPES)
        except Exception as e:
            sys.stderr.write(f"Warning: could not read token file: {e}\n")

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
            except Exception as e:
                sys.stderr.write(f"Token refresh failed: {e}. Re-authenticating...\n")
                creds = None

        if not creds:
            if not CREDENTIALS_FILE.exists():
                sys.stderr.write(
                    f"Error: Credentials file not found at {CREDENTIALS_FILE}.\n"
                    "Please download your OAuth client credentials JSON from Google Cloud Console.\n"
                )
                sys.exit(1)

            flow = InstalledAppFlow.from_client_secrets_file(str(CREDENTIALS_FILE), SCOPES)
            creds = flow.run_local_server(port=0)

        TOKEN_FILE.parent.mkdir(parents=True, exist_ok=True)
        TOKEN_FILE.write_text(creds.to_json())
        TOKEN_FILE.chmod(0o600)

    return creds


def get_service():
    creds = get_credentials()
    return build("tasks", "v1", credentials=creds)


def resolve_list_id(service, list_arg):
    if not list_arg or list_arg in ("@default", "default"):
        return "@default"
    
    # Check if list_arg is already a valid list ID
    try:
        tasklists = service.tasklists().list().execute().get("items", [])
    except HttpError as e:
        sys.stderr.write(f"API Error fetching lists: {e}\n")
        sys.exit(1)

    for tl in tasklists:
        if tl["id"] == list_arg:
            return tl["id"]

    # Try matching by title (case-insensitive)
    matches = [tl for tl in tasklists if tl.get("title", "").lower() == list_arg.lower()]
    if matches:
        return matches[0]["id"]

    # Substring match
    matches = [tl for tl in tasklists if list_arg.lower() in tl.get("title", "").lower()]
    if len(matches) == 1:
        return matches[0]["id"]
    elif len(matches) > 1:
        sys.stderr.write(f"Ambiguous list name '{list_arg}'. Matches: {', '.join(m['title'] for m in matches)}\n")
        sys.exit(1)

    sys.stderr.write(f"List '{list_arg}' not found. Use 'lists' command to see available lists.\n")
    sys.exit(1)


def parse_date(date_str):
    if not date_str:
        return None
    date_str = date_str.strip().lower()
    today = datetime.date.today()
    if date_str == "today" or date_str == "oggi":
        d = today
    elif date_str == "tomorrow" or date_str == "domani":
        d = today + datetime.timedelta(days=1)
    elif date_str.startswith("+") and date_str.endswith("d"):
        try:
            days = int(date_str[1:-1])
            d = today + datetime.timedelta(days=days)
        except ValueError:
            d = None
    else:
        try:
            d = datetime.date.fromisoformat(date_str)
        except ValueError:
            sys.stderr.write(f"Invalid date format '{date_str}'. Use YYYY-MM-DD, 'today', 'tomorrow', or '+Nd'.\n")
            sys.exit(1)

    return datetime.datetime(d.year, d.month, d.day, 0, 0, 0, tzinfo=datetime.timezone.utc).isoformat()


def cmd_auth(args):
    get_service()
    print("Authentication successful! Token is valid.")


def cmd_lists(args):
    service = get_service()
    res = service.tasklists().list().execute()
    items = res.get("items", [])
    if args.json:
        print(json.dumps(items, indent=2))
        return

    if not items:
        print("No task lists found.")
        return

    print(f"{'TITLE':<30} {'ID'}")
    print("-" * 75)
    for item in items:
        title = item.get("title", "Untitled")
        print(f"{title:<30} {item['id']}")


def cmd_add_list(args):
    service = get_service()
    res = service.tasklists().insert(body={"title": args.title}).execute()
    if args.json:
        print(json.dumps(res, indent=2))
    else:
        print(f"Created task list: '{res.get('title')}' (ID: {res.get('id')})")


def cmd_delete_list(args):
    service = get_service()
    list_id = resolve_list_id(service, args.list_id)
    service.tasklists().delete(tasklist=list_id).execute()
    print(f"Deleted task list: {list_id}")


def cmd_list_tasks(args):
    service = get_service()
    list_id = resolve_list_id(service, args.list)
    show_completed = args.all or args.completed
    res = service.tasks().list(
        tasklist=list_id,
        showCompleted=show_completed,
        showHidden=show_completed
    ).execute()
    items = res.get("items", [])

    if not args.all:
        if args.completed:
            items = [t for t in items if t.get("status") == "completed"]
        else:
            items = [t for t in items if t.get("status") != "completed"]

    if args.json:
        print(json.dumps(items, indent=2))
        return

    if not items:
        print("No tasks found.")
        return

    for t in items:
        status = "[x]" if t.get("status") == "completed" else "[ ]"
        title = t.get("title", "(No title)")
        task_id = t.get("id")
        due = t.get("due")
        due_str = f" [Due: {due[:10]}]" if due else ""
        print(f"{status} {title}{due_str} (ID: {task_id})")
        if t.get("notes"):
            for line in t["notes"].splitlines():
                print(f"      {line}")


def cmd_add_task(args):
    service = get_service()
    list_id = resolve_list_id(service, args.list)
    body = {"title": args.title}
    if args.notes:
        body["notes"] = args.notes
    if args.due:
        body["due"] = parse_date(args.due)

    res = service.tasks().insert(tasklist=list_id, body=body).execute()
    if args.json:
        print(json.dumps(res, indent=2))
    else:
        due_info = f" (due: {args.due})" if args.due else ""
        print(f"Task added: '{res.get('title')}'{due_info} [ID: {res.get('id')}]")


def cmd_done_task(args):
    service = get_service()
    list_id = resolve_list_id(service, args.list)
    body = {
        "status": "completed",
        "completed": datetime.datetime.now(datetime.timezone.utc).isoformat()
    }
    res = service.tasks().patch(tasklist=list_id, task=args.task_id, body=body).execute()
    if args.json:
        print(json.dumps(res, indent=2))
    else:
        print(f"Marked as completed: '{res.get('title')}'")


def cmd_undone_task(args):
    service = get_service()
    list_id = resolve_list_id(service, args.list)
    body = {
        "status": "needsAction",
        "completed": None
    }
    res = service.tasks().patch(tasklist=list_id, task=args.task_id, body=body).execute()
    if args.json:
        print(json.dumps(res, indent=2))
    else:
        print(f"Marked as pending: '{res.get('title')}'")


def cmd_delete_task(args):
    service = get_service()
    list_id = resolve_list_id(service, args.list)
    service.tasks().delete(tasklist=list_id, task=args.task_id).execute()
    print(f"Deleted task: {args.task_id}")


def cmd_clear_tasks(args):
    service = get_service()
    list_id = resolve_list_id(service, args.list)
    service.tasks().clear(tasklist=list_id).execute()
    print("Cleared all completed tasks.")


def cmd_search_tasks(args):
    service = get_service()
    query = args.query.lower()
    
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
                if query in title.lower() or query in notes.lower():
                    matching_tasks.append((tl_title, t))
        except Exception:
            continue

    if args.json:
        print(json.dumps([t for _, t in matching_tasks], indent=2))
        return

    if not matching_tasks:
        print(f"No tasks matching '{args.query}' found.")
        return

    print(f"Found {len(matching_tasks)} matching task(s):")
    for tl_title, t in matching_tasks:
        status = "[x]" if t.get("status") == "completed" else "[ ]"
        title = t.get("title", "(No title)")
        due = t.get("due")
        due_str = f" [Due: {due[:10]}]" if due else ""
        print(f"{status} [{tl_title}] {title}{due_str} (ID: {t.get('id')})")
        if t.get("notes"):
            for line in t["notes"].splitlines():
                print(f"      {line}")


def main():
    parser = argparse.ArgumentParser(description="Google Tasks CLI Helper")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # auth
    p_auth = subparsers.add_parser("auth", help="Verify or execute OAuth authentication")

    # lists
    p_lists = subparsers.add_parser("lists", help="List all task lists")
    p_lists.add_argument("--json", action="store_true", help="Output raw JSON")

    # add-list
    p_add_list = subparsers.add_parser("add-list", help="Create a new task list")
    p_add_list.add_argument("title", help="Title of the new task list")
    p_add_list.add_argument("--json", action="store_true", help="Output raw JSON")

    # delete-list
    p_del_list = subparsers.add_parser("delete-list", help="Delete a task list")
    p_del_list.add_argument("list_id", help="ID or title of the list to delete")

    # list tasks
    p_list = subparsers.add_parser("list", help="List tasks in a list")
    p_list.add_argument("--list", "-l", default="@default", help="List title or ID (default: @default)")
    p_list.add_argument("--all", "-a", action="store_true", help="Include completed tasks")
    p_list.add_argument("--completed", "-c", action="store_true", help="Show ONLY completed tasks")
    p_list.add_argument("--json", action="store_true", help="Output raw JSON")

    # add task
    p_add = subparsers.add_parser("add", help="Add a new task")
    p_add.add_argument("title", help="Title of the task")
    p_add.add_argument("--list", "-l", default="@default", help="List title or ID (default: @default)")
    p_add.add_argument("--notes", "-n", help="Notes / description for the task")
    p_add.add_argument("--due", "-d", help="Due date (YYYY-MM-DD, 'today', 'tomorrow', '+Nd')")
    p_add.add_argument("--json", action="store_true", help="Output raw JSON")

    # done task
    p_done = subparsers.add_parser("done", help="Mark a task as completed")
    p_done.add_argument("task_id", help="Task ID to mark done")
    p_done.add_argument("--list", "-l", default="@default", help="List title or ID (default: @default)")
    p_done.add_argument("--json", action="store_true", help="Output raw JSON")

    # undone task
    p_undone = subparsers.add_parser("undone", help="Mark a task as pending")
    p_undone.add_argument("task_id", help="Task ID to mark pending")
    p_undone.add_argument("--list", "-l", default="@default", help="List title or ID (default: @default)")
    p_undone.add_argument("--json", action="store_true", help="Output raw JSON")

    # delete task
    p_del = subparsers.add_parser("delete", help="Delete a task")
    p_del.add_argument("task_id", help="Task ID to delete")
    p_del.add_argument("--list", "-l", default="@default", help="List title or ID (default: @default)")

    # clear completed
    p_clear = subparsers.add_parser("clear", help="Clear all completed tasks from a list")
    p_clear.add_argument("--list", "-l", default="@default", help="List title or ID (default: @default)")

    # search
    p_search = subparsers.add_parser("search", help="Search tasks across lists")
    p_search.add_argument("query", help="Text search query")
    p_search.add_argument("--json", action="store_true", help="Output raw JSON")

    args = parser.parse_args()

    command_map = {
        "auth": cmd_auth,
        "lists": cmd_lists,
        "add-list": cmd_add_list,
        "delete-list": cmd_delete_list,
        "list": cmd_list_tasks,
        "add": cmd_add_task,
        "done": cmd_done_task,
        "undone": cmd_undone_task,
        "delete": cmd_delete_task,
        "clear": cmd_clear_tasks,
        "search": cmd_search_tasks,
    }

    try:
        command_map[args.command](args)
    except HttpError as e:
        sys.stderr.write(f"Google API Error: {e}\n")
        sys.exit(1)
    except KeyboardInterrupt:
        sys.exit(130)


if __name__ == "__main__":
    main()

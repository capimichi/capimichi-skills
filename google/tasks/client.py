#!/usr/bin/env python3
"""
Google Tasks API Client helper.
"""

import datetime
import os
import sys
from pathlib import Path

try:
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from googleapiclient.discovery import build
    from googleapiclient.errors import HttpError
except ImportError:
    sys.exit(
        "Errore: librerie Google non trovate. Installa le dipendenze richieste eseguendo:\n"
        "pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib click"
    )

SCOPES = ["https://www.googleapis.com/auth/tasks"]

HOME = Path(os.environ.get("HOME", Path.home()))
CONFIG_DIR = Path(os.environ.get("XDG_CONFIG_HOME", HOME / ".config")) / "google-tasks"
STATE_DIR = Path(os.environ.get("XDG_STATE_HOME", HOME / ".local" / "state")) / "google-tasks"
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

    try:
        tasklists = service.tasklists().list().execute().get("items", [])
    except HttpError as e:
        sys.stderr.write(f"API Error fetching lists: {e}\n")
        sys.exit(1)

    for tl in tasklists:
        if tl["id"] == list_arg:
            return tl["id"]

    matches = [tl for tl in tasklists if tl.get("title", "").lower() == list_arg.lower()]
    if matches:
        return matches[0]["id"]

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
    if date_str in ("today", "oggi"):
        d = today
    elif date_str in ("tomorrow", "domani"):
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

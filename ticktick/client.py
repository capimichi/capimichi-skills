#!/usr/bin/env python3
"""
TickTick Open API Client Helper.
"""

import os
import sys
import re
from datetime import datetime, timedelta

try:
    import requests
except ImportError:
    sys.exit("Errore: modulo 'requests' non trovato. Installa le dipendenze richieste eseguendo: pip install requests")

BASE_URL = "https://api.ticktick.com/open/v1"
INBOX = {"id": "inbox", "name": "Inbox", "kind": "TASK"}


def get_api_token():
    token = os.environ.get("TICKTICK_APIKEY", "").strip()
    if not token:
        # Fallback di compatibilità
        token = os.environ.get("TICKTICK_API_KEY", "").strip()
    if token:
        return token

    sys.exit("Errore: Variabile d'ambiente TICKTICK_APIKEY non impostata nell'ambiente.")


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
        sys.stderr.write(f"[ERRORE API {resp.status_code}]: {resp.text}\n")
        resp.raise_for_status()
    return resp.json() if resp.text else {}


def get_projects(include_inbox=True):
    projects = request("GET", "/project")
    if include_inbox:
        return [INBOX] + projects
    return projects


def find_project(name_or_id, projects=None, exact=False):
    if not name_or_id:
        return None
    if projects is None:
        projects = get_projects()

    # 1. Match esatto per ID
    for p in projects:
        if p["id"] == name_or_id:
            return p

    # 2. Match esatto case-insensitive per nome
    query = name_or_id.lower().strip()
    for p in projects:
        if p.get("name", "").lower().strip() == query:
            return p

    if exact:
        return None

    # 3. Match parziale
    partial = [p for p in projects if query in p.get("name", "").lower()]
    if len(partial) == 1:
        return partial[0]
    elif len(partial) > 1:
        names = ", ".join(f"{p['name']} ({p['id']})" for p in partial)
        sys.stderr.write(f"[ERRORE] '{name_or_id}' è ambiguo: {names}\n")
        sys.exit(1)

    return None


def parse_date(date_str):
    """
    Interpreta espressioni temporali e ritorna: (iso_date_string, is_all_day).
    """
    if not date_str:
        return None, False

    s = date_str.strip().lower()
    now = datetime.now().astimezone()
    target_dt = None
    is_all_day = False

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
        for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d %H:%M"):
            try:
                target_dt = datetime.strptime(s, fmt).astimezone()
                break
            except ValueError:
                pass

    if not target_dt:
        try:
            target_dt = datetime.fromisoformat(date_str).astimezone()
        except Exception:
            sys.stderr.write(f"[Warning] Impossibile interpretare la data '{date_str}', ignorata.\n")
            return None, False

    if hour is not None and minute is not None:
        target_dt = target_dt.replace(hour=hour, minute=minute, second=0, microsecond=0)
        is_all_day = False
    elif "today" in date_str or "oggi" in date_str or "domani" in date_str or "tomorrow" in date_str or re.match(r'^\d{4}-\d{2}-\d{2}$', date_str.strip()):
        is_all_day = True
        target_dt = target_dt.replace(hour=9, minute=0, second=0, microsecond=0)

    formatted = target_dt.strftime("%Y-%m-%dT%H:%M:%S%z")
    return formatted, is_all_day

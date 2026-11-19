#!/usr/bin/env python3
"""
ISS San Marino - Prescription Automation CLI
Allows automated filling and submission of prescription renewal requests to the ISS online portal:
https://servizionline.iss.sm/#new-1

Safe by default: requests will run in dry-run mode unless --submit is explicitly provided.
Follows ADD_SKILL_RULES.md: strictly consumes system environment variables only.
"""

import json
import os
import re
import sys
from typing import Dict, List, Optional, Tuple

import click
import requests

BASE_URL = "https://servizionline.iss.sm"
FORM_ACTION_URL = f"{BASE_URL}/iss.asp"
SEARCH_ACTION_URL = f"{BASE_URL}/iss.asp?action=search"

REQUEST_TYPES: Dict[str, str] = {
    "ordinary": "23",  # Rinnovo ricetta ordinaria
    "repetitive": "24",  # Rinnovo ricetta ripetitiva
}

REQUEST_TYPE_LABELS: Dict[str, str] = {
    "23": "Rinnovo ricetta ordinaria",
    "24": "Rinnovo ricetta ripetitiva",
}

# Fallback doctors list if portal is temporarily unreachable
FALLBACK_DOCTORS: List[Dict[str, str]] = [
    # CS Borgo Maggiore
    {"id": "97", "name": "Matteo Villa", "label": "Matteo Villa - Borgo 1", "code": "Borgo 1", "center": "CS Borgo Maggiore"},
    {"id": "85", "name": "Giulia Tolomelli", "label": "Giulia Tolomelli - Borgo 2", "code": "Borgo 2", "center": "CS Borgo Maggiore"},
    {"id": "75", "name": "Elizaveta Hadji", "label": "Elizaveta Hadji - Borgo 3", "code": "Borgo 3", "center": "CS Borgo Maggiore"},
    {"id": "92", "name": "Michael Pulazza", "label": "Michael Pulazza - Borgo 4", "code": "Borgo 4", "center": "CS Borgo Maggiore"},
    {"id": "68", "name": "Denise Barretto Mori", "label": "Denise Barretto Mori - Borgo 5", "code": "Borgo 5", "center": "CS Borgo Maggiore"},
    {"id": "9", "name": "Patrizia Tamagnini", "label": "Patrizia Tamagnini - Borgo 6", "code": "Borgo 6", "center": "CS Borgo Maggiore"},
    # CS Murata
    {"id": "94", "name": "Milena Cannuccia", "label": "Milena Cannuccia - Murata 1", "code": "Murata 1", "center": "CS Murata"},
    {"id": "98", "name": "Sandro Stacchini", "label": "Sandro Stacchini - Murata 2", "code": "Murata 2", "center": "CS Murata"},
    {"id": "83", "name": "Maria Vittoria Casali", "label": "Maria Vittoria Casali - Murata 3", "code": "Murata 3", "center": "CS Murata"},
    {"id": "13", "name": "Silvia Genghini", "label": "Silvia Genghini - Murata 4", "code": "Murata 4", "center": "CS Murata"},
    {"id": "65", "name": "Cristina Cristiano", "label": "Cristina Cristiano - Murata 5", "code": "Murata 5", "center": "CS Murata"},
    {"id": "90", "name": "Martina Guerra", "label": "Martina Guerra - Murata 6", "code": "Murata 6", "center": "CS Murata"},
    # CS Serravalle
    {"id": "81", "name": "Emanuele Dominique Cappella", "label": "Emanuele Dominique Cappella - Serravalle 1", "code": "Serravalle 1", "center": "CS Serravalle"},
    {"id": "17", "name": "Alessandra Zannoni", "label": "Alessandra Zannoni - Serravalle 2", "code": "Serravalle 2", "center": "CS Serravalle"},
    {"id": "18", "name": "Maria Anna Aalders", "label": "Maria Anna Aalders - Serravalle 3", "code": "Serravalle 3", "center": "CS Serravalle"},
    {"id": "19", "name": "Deborah Beccari", "label": "Deborah Beccari - Serravalle 4", "code": "Serravalle 4", "center": "CS Serravalle"},
    {"id": "20", "name": "Barbara Cosimetti", "label": "Barbara Cosimetti - Serravalle 5", "code": "Serravalle 5", "center": "CS Serravalle"},
    {"id": "77", "name": "Federico Gorrieri", "label": "Federico Gorrieri - Serravalle 6", "code": "Serravalle 6", "center": "CS Serravalle"},
    {"id": "22", "name": "Massimo Vignali", "label": "Massimo Vignali - Serravalle 7", "code": "Serravalle 7", "center": "CS Serravalle"},
]


def fetch_live_doctors() -> List[Dict[str, str]]:
    """Dynamically fetches current doctors and IDs from the live ISS portal."""
    try:
        resp = requests.get(f"{BASE_URL}/", timeout=4)
        if resp.status_code == 200:
            text = resp.content.decode("latin-1", errors="ignore")
            m = re.search(r'\"listacondotta\":\{.*?\"1\":\"(<select.*?</select>)\"', text)
            if m:
                clean = m.group(1).encode("utf-8").decode("unicode_escape")
                groups = re.split(r'<optgroup label=\"([^\"]+)\">', clean)
                doctors: List[Dict[str, str]] = []
                for i in range(1, len(groups), 2):
                    center = groups[i]
                    content = groups[i + 1]
                    for opt in re.finditer(r'<option value=\"(\d+)\">([^<]+)</option>', content):
                        doc_id = opt.group(1)
                        label = opt.group(2)
                        name = label.split(" - ")[0].strip() if " - " in label else label.strip()
                        code = label.split(" - ")[1].strip() if " - " in label else ""
                        doctors.append({
                            "id": doc_id,
                            "name": name,
                            "label": label,
                            "code": code,
                            "center": center,
                        })
                if doctors:
                    return doctors
    except Exception:
        pass
    return FALLBACK_DOCTORS


def resolve_doctor(query: str, doctors: List[Dict[str, str]]) -> Tuple[Optional[Dict[str, str]], List[Dict[str, str]]]:
    """
    Resolves doctor by numeric ID or by name (case-insensitive substring match).
    Returns (matched_doctor_dict or None, list_of_ambiguous_candidates).
    """
    q = query.strip()
    if not q:
        return None, []

    # 1. Exact ID match
    if q.isdigit():
        for d in doctors:
            if d["id"] == q:
                return d, []

    q_lower = q.lower()

    # 2. Exact name match
    exact_matches = [d for d in doctors if d["name"].lower() == q_lower or d["label"].lower() == q_lower]
    if len(exact_matches) == 1:
        return exact_matches[0], []

    # 3. Substring match (in name or label)
    matches = [d for d in doctors if q_lower in d["name"].lower() or q_lower in d["label"].lower()]
    if len(matches) == 1:
        return matches[0], []
    if len(matches) > 1:
        return None, matches

    return None, []


def resolve_config(param_val: Optional[str], env_vars: List[str]) -> Optional[str]:
    """Resolves config strictly from CLI parameter or System Environment Variables."""
    if param_val is not None and param_val != "":
        return param_val
    for ev in env_vars:
        val = os.environ.get(ev)
        if val is not None and val.strip() != "":
            return val.strip()
    return None


def format_birth_date(date_str: str) -> str:
    """Normalizes birth date string into D/M/YYYY or DD/MM/YYYY."""
    date_str = date_str.strip()
    if re.match(r"^\d{1,2}[./-]\d{1,2}[./-]\d{4}$", date_str):
        parts = re.split(r"[./-]", date_str)
        return f"{int(parts[0])}/{int(parts[1])}/{parts[2]}"
    if re.match(r"^\d{4}-\d{1,2}-\d{1,2}$", date_str):
        parts = date_str.split("-")
        return f"{int(parts[2])}/{int(parts[1])}/{parts[0]}"
    return date_str


def validate_iss_code(code: str) -> bool:
    return bool(re.match(r"^[1-9][0-9]{0,6}$", code))


def validate_birth_date(date_str: str) -> bool:
    return bool(re.match(r"^\d{1,2}([./-])\d{1,2}\1\d{4}$", date_str))


def validate_email(email_str: str) -> bool:
    return bool(re.match(r"^([a-zA-Z0-9_\-\.]+)@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.)|(([a-zA-Z0-9\-]+\.)+))([a-zA-Z]{2,}|[0-9]{1,3})(\]?)$", email_str))


@click.group()
def cli():
    """ISS San Marino - Prescription Renewal Assistant."""
    pass


@cli.command("doctors")
@click.option("--search", "-s", default="", help="Filter by doctor name or health center.")
@click.option("--json-output", is_flag=True, help="Print output in JSON format.")
def list_doctors(search: str, json_output: bool):
    """List all available primary care doctors and their IDs from the ISS portal."""
    doctors = fetch_live_doctors()
    filtered = doctors
    if search:
        s = search.lower()
        filtered = [d for d in doctors if s in d["name"].lower() or s in d["center"].lower() or s in d["code"].lower()]

    if json_output:
        click.echo(json.dumps(filtered, indent=2, ensure_ascii=False))
        return

    click.echo("\nAvailable Primary Care Doctors (Cure Primarie - Live):")
    click.echo("=" * 65)
    current_center = ""
    for d in filtered:
        if d["center"] != current_center:
            current_center = d["center"]
            click.echo(f"\n[{current_center}]")
        click.echo(f"  ID: {d['id']:>2} | {d['name']:<28} ({d['code']})")
    click.echo("=" * 65 + "\n")


@cli.command("status")
@click.option("--code", "-c", help="Patient ISS code (env: ISS_CODE).")
@click.option("--request-id", "-r", required=True, help="Request ID returned during prescription submission.")
@click.option("--json-output", is_flag=True, help="Print raw JSON response from server.")
def check_status(code: Optional[str], request_id: str, json_output: bool):
    """Check the status of a previously submitted prescription request."""
    iss_code = resolve_config(code, ["ISS_CODE"])

    if not iss_code:
        click.echo("Error: Missing ISS Code. Set ISS_CODE environment variable or pass --code.", err=True)
        sys.exit(1)

    payload = {
        "set": "1",
        "iss": iss_code,
        "codice": request_id.strip(),
    }

    try:
        session = requests.Session()
        session.headers.update({
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)",
            "Referer": f"{BASE_URL}/",
        })
        resp = session.post(SEARCH_ACTION_URL, data=payload, timeout=15)
        resp.raise_for_status()

        try:
            data = resp.json()
        except ValueError:
            click.echo(f"Error parsing response: {resp.text}", err=True)
            sys.exit(1)

        if json_output:
            click.echo(json.dumps(data, indent=2, ensure_ascii=False))
            return

        click.echo("\n--- ISS Request Status ---")
        if data.get("id"):
            status_code = data.get("status")
            status_labels = {
                "25": "IN PROGRESS / NON ELABORATA (In lavorazione)",
                "26": "COMPLETED / ELABORATA (Pronta)",
                "27": "CANCELLED / ANNULLATA",
                "28": "CANCELLED BY USER / ANNULLATA DA TE",
            }
            status_desc = status_labels.get(status_code, f"Status code: {status_code}")
            click.echo(f"Request ID:   {data.get('id')}")
            click.echo(f"Request Type: {data.get('typedesc', 'N/A')}")
            click.echo(f"Status:       {status_desc}")
            if data.get("statusdesc"):
                click.echo(f"Portal State: {data.get('statusdesc')}")
            if data.get("message"):
                click.echo(f"Message:      {data.get('message')}")
        else:
            click.echo("No matching request found or invalid ISS Code / Request ID.")
        click.echo("--------------------------\n")

    except requests.RequestException as e:
        click.echo(f"Network error communicating with ISS portal: {e}", err=True)
        sys.exit(1)


@cli.command("request")
@click.option("--medications", "-m", required=True, help="Medication names and daily dosages (required).")
@click.option("--type", "-t", "req_type", type=click.Choice(["ordinary", "repetitive"], case_sensitive=False), default="ordinary", show_default=True, help="Prescription type.")
@click.option("--code", "-c", help="Patient ISS code (env: ISS_CODE).")
@click.option("--first-name", "-f", help="Patient first name (env: ISS_FIRST_NAME).")
@click.option("--last-name", "-l", help="Patient last name (env: ISS_LAST_NAME).")
@click.option("--birth-date", "-b", help="Patient birth date in D/M/YYYY or YYYY-MM-DD (env: ISS_BIRTH_DATE).")
@click.option("--phone", "-p", help="Patient phone number (env: ISS_PHONE).")
@click.option("--email", "-e", help="Patient email address for notifications (env: ISS_EMAIL).")
@click.option("--doctor", "-d", help="Assigned doctor name (e.g. 'Milena Cannuccia') or numeric ID (env: ISS_DOCTOR).")
@click.option("--submit", is_flag=True, default=False, help="Perform actual live submission. Defaults to dry-run mode.")
def submit_request(
    medications: str,
    req_type: str,
    code: Optional[str],
    first_name: Optional[str],
    last_name: Optional[str],
    birth_date: Optional[str],
    phone: Optional[str],
    email: Optional[str],
    doctor: Optional[str],
    submit: bool,
):
    """
    Submit a prescription renewal request to the ISS portal.
    By default runs in DRY-RUN mode to prevent accidental submissions.
    """
    iss_code = resolve_config(code, ["ISS_CODE"])
    fname = resolve_config(first_name, ["ISS_FIRST_NAME"])
    lname = resolve_config(last_name, ["ISS_LAST_NAME"])
    bdate_raw = resolve_config(birth_date, ["ISS_BIRTH_DATE"])
    tel = resolve_config(phone, ["ISS_PHONE"])
    mail = resolve_config(email, ["ISS_EMAIL"]) or ""
    doc_query = resolve_config(doctor, ["ISS_DOCTOR", "ISS_DOCTOR_ID"])

    # Validate missing fields
    missing: List[str] = []
    if not iss_code:
        missing.append("ISS Code (--code or env ISS_CODE)")
    if not fname:
        missing.append("First Name (--first-name or env ISS_FIRST_NAME)")
    if not lname:
        missing.append("Last Name (--last-name or env ISS_LAST_NAME)")
    if not bdate_raw:
        missing.append("Birth Date (--birth-date or env ISS_BIRTH_DATE)")
    if not tel:
        missing.append("Phone (--phone or env ISS_PHONE)")
    if not doc_query:
        missing.append("Doctor Name/ID (--doctor or env ISS_DOCTOR)")

    if missing:
        click.echo("Error: Missing required configuration. Please set the following environment variables or CLI options:", err=True)
        for m in missing:
            click.echo(f"  - {m}", err=True)
        sys.exit(1)

    # Resolve doctor dynamically from live portal
    live_doctors = fetch_live_doctors()
    matched_doc, ambig = resolve_doctor(doc_query, live_doctors)

    if ambig:
        click.echo(f"Error: Doctor query '{doc_query}' is ambiguous. Matching doctors:", err=True)
        for a in ambig:
            click.echo(f"  - ID {a['id']}: {a['label']} ({a['center']})", err=True)
        click.echo("Please provide a more specific doctor name or ID.", err=True)
        sys.exit(1)

    if not matched_doc:
        click.echo(f"Error: Doctor '{doc_query}' not found in ISS system.", err=True)
        click.echo("Run 'cli.py doctors' to view available doctors.", err=True)
        sys.exit(1)

    doc_id = matched_doc["id"]
    doctor_info = f"{matched_doc['name']} ({matched_doc['code']} - {matched_doc['center']})"

    # Format and validate birth date
    bdate = format_birth_date(bdate_raw)
    if not validate_birth_date(bdate):
        click.echo(f"Error: Invalid birth date format '{bdate_raw}'. Expected D/M/YYYY or DD/MM/YYYY.", err=True)
        sys.exit(1)

    if not validate_iss_code(iss_code):
        click.echo(f"Error: Invalid ISS code '{iss_code}'. Must be numeric, 1-7 digits.", err=True)
        sys.exit(1)

    if mail and not validate_email(mail):
        click.echo(f"Error: Invalid email format '{mail}'.", err=True)
        sys.exit(1)

    type_code = REQUEST_TYPES.get(req_type.lower(), "23")
    type_label = REQUEST_TYPE_LABELS.get(type_code, "Rinnovo ricetta")

    # Prepare exact form payload
    payload = {
        "set": "1",
        "gruppo": "1",
        "iss": iss_code,
        "nome": fname,
        "cognome": lname,
        "datanascita": bdate,
        "telefono": tel,
        "email": mail,
        "richiesta": type_code,
        "condotta": doc_id,
        "domanda": medications.strip(),
    }

    # Summary table
    click.echo("\n=======================================================")
    click.echo("        ISS SAN MARINO - PRESCRIPTION REQUEST          ")
    click.echo("=======================================================")
    click.echo(f" Patient:      {fname} {lname}")
    click.echo(f" ISS Code:     {iss_code}")
    click.echo(f" Birth Date:   {bdate}")
    click.echo(f" Phone:        {tel}")
    click.echo(f" Email:        {mail if mail else '(None)'}")
    click.echo(f" Doctor:       {doctor_info} [Portal ID: {doc_id}]")
    click.echo(f" Type:         {type_label} (code: {type_code})")
    click.echo(f" Medications:  {medications.strip()}")
    click.echo("=======================================================")

    if not submit:
        click.echo("\n[DRY RUN MODE] - No request was sent to the ISS server.")
        click.echo("To perform the actual live submission, re-run with --submit.\n")
        click.echo("Payload preview:")
        click.echo(json.dumps(payload, indent=2, ensure_ascii=False))
        return

    # Real submission
    click.echo("\nSubmitting prescription request to ISS portal...")
    try:
        session = requests.Session()
        session.headers.update({
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
            "Referer": f"{BASE_URL}/",
            "Origin": BASE_URL,
        })
        resp = session.post(FORM_ACTION_URL, data=payload, timeout=20)
        resp.raise_for_status()

        try:
            data = resp.json()
        except ValueError:
            click.echo(f"Unexpected non-JSON response from server: {resp.text}", err=True)
            sys.exit(1)

        if data.get("id"):
            req_id = data.get("id")
            warning = data.get("warning", "")
            click.echo("\n SUCCESS! Prescription request registered successfully.")
            click.echo(f" Request Tracking Code (ID): {req_id}")
            if warning:
                click.echo(f" Notice: {warning}")
            click.echo(f"\nYou can track status anytime with:")
            click.echo(f"  cli.py status --request-id {req_id}\n")
        elif data.get("error"):
            click.echo(f"\n Submission rejected by server: {data.get('error')}", err=True)
            sys.exit(1)
        else:
            click.echo(f"\n Unknown server response: {data}", err=True)
            sys.exit(1)

    except requests.RequestException as e:
        click.echo(f"\n Network error communicating with ISS portal: {e}", err=True)
        sys.exit(1)


if __name__ == "__main__":
    cli()

#!/usr/bin/env python3
"""
Google Search Console API Client helper.
"""

import datetime
import os
import sys
from pathlib import Path
from urllib.parse import urlparse

try:
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from google.oauth2 import service_account
    from google_auth_oauthlib.flow import InstalledAppFlow
    from googleapiclient.discovery import build
    from googleapiclient.errors import HttpError
except ImportError:
    sys.exit(
        "Errore: librerie Google non trovate. Installa le dipendenze richieste eseguendo:\n"
        "pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib click"
    )

SCOPES = ["https://www.googleapis.com/auth/webmasters"]

HOME = Path(os.environ.get("HOME", Path.home()))
CONFIG_DIR = Path(os.environ.get("XDG_CONFIG_HOME", HOME / ".config")) / "google-search-console"
STATE_DIR = Path(os.environ.get("XDG_STATE_HOME", HOME / ".local" / "state")) / "google-search-console"
CREDENTIALS_FILE = Path(os.environ.get("SEARCH_CONSOLE_CREDENTIALS", CONFIG_DIR / "credentials.json"))
SERVICE_ACCOUNT_FILE = Path(os.environ.get("SEARCH_CONSOLE_SERVICE_ACCOUNT", CONFIG_DIR / "service_account.json"))
TOKEN_FILE = Path(os.environ.get("SEARCH_CONSOLE_TOKEN", STATE_DIR / "token.json"))

# Dynamic fallbacks
if not TOKEN_FILE.exists():
    if (CONFIG_DIR / "token.json").exists():
        TOKEN_FILE = CONFIG_DIR / "token.json"
    elif (HOME / ".local" / "state" / "google-search-console" / "token.json").exists():
        TOKEN_FILE = HOME / ".local" / "state" / "google-search-console" / "token.json"

if not CREDENTIALS_FILE.exists() and (HOME / ".config" / "google-search-console" / "credentials.json").exists():
    CREDENTIALS_FILE = HOME / ".config" / "google-search-console" / "credentials.json"


def get_credentials(force_auth=False):
    # 1. Check if Service Account JSON key is available
    if not force_auth and SERVICE_ACCOUNT_FILE.exists():
        try:
            return service_account.Credentials.from_service_account_file(
                str(SERVICE_ACCOUNT_FILE), scopes=SCOPES
            )
        except Exception as e:
            sys.stderr.write(f"Warning: could not load service account credentials: {e}\n")

    # 2. Check OAuth Token
    creds = None
    if not force_auth and TOKEN_FILE.exists():
        try:
            creds = Credentials.from_authorized_user_file(str(TOKEN_FILE), SCOPES)
        except Exception as e:
            sys.stderr.write(f"Warning: could not read token file: {e}\n")

    if not creds or not creds.valid or force_auth:
        if creds and creds.expired and creds.refresh_token and not force_auth:
            try:
                creds.refresh(Request())
            except Exception as e:
                sys.stderr.write(f"Token refresh failed: {e}. Re-authenticating...\n")
                creds = None

        if not creds or force_auth:
            if not CREDENTIALS_FILE.exists():
                sys.stderr.write(
                    f"Error: Credentials file not found at {CREDENTIALS_FILE}.\n"
                    "Ensure credentials.json is present in ~/.config/google-search-console/\n"
                    "or pass SEARCH_CONSOLE_CREDENTIALS.\n"
                )
                sys.exit(1)

            flow = InstalledAppFlow.from_client_secrets_file(str(CREDENTIALS_FILE), SCOPES)
            creds = flow.run_local_server(port=0)

        TOKEN_FILE.parent.mkdir(parents=True, exist_ok=True)
        TOKEN_FILE.write_text(creds.to_json())
        TOKEN_FILE.chmod(0o600)

    return creds


def get_services(creds=None):
    if not creds:
        creds = get_credentials()
    searchconsole = build("searchconsole", "v1", credentials=creds)
    webmasters = build("webmasters", "v3", credentials=creds)
    return searchconsole, webmasters


def list_sites(webmasters_service):
    res = webmasters_service.sites().list().execute()
    return res.get("siteEntry", [])


def resolve_site_url(webmasters_service, site_arg=None, target_url=None):
    if site_arg:
        return site_arg

    env_site = os.environ.get("GSC_SITE_URL") or os.environ.get("SEARCH_CONSOLE_SITE_URL")
    if env_site:
        return env_site

    sites = list_sites(webmasters_service)
    if not sites:
        sys.stderr.write("Error: No verified properties found in Google Search Console.\n")
        sys.exit(1)

    site_urls = [s["siteUrl"] for s in sites]

    if target_url:
        parsed = urlparse(target_url)
        host = parsed.netloc.lower()
        if host.startswith("www."):
            host_no_www = host[4:]
        else:
            host_no_www = host

        for s in site_urls:
            if s == f"sc-domain:{host}" or s == f"sc-domain:{host_no_www}":
                return s

        for s in site_urls:
            if s.startswith("http") and host_no_www in s:
                return s

    if len(site_urls) == 1:
        return site_urls[0]

    for s in site_urls:
        if "memispaintings" in s:
            return s

    return site_urls[0]

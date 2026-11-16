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
from urllib.parse import urlparse

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google.oauth2 import service_account
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

SCOPES = ["https://www.googleapis.com/auth/webmasters"]

HOME = Path(os.environ.get("HOME", Path.home()))
CONFIG_DIR = Path(os.environ.get("XDG_CONFIG_HOME", HOME / ".config")) / "google-search-console"
STATE_DIR = Path(os.environ.get("XDG_STATE_HOME", HOME / ".local" / "state")) / "google-search-console"
CREDENTIALS_FILE = Path(os.environ.get("SEARCH_CONSOLE_CREDENTIALS", CONFIG_DIR / "credentials.json"))
SERVICE_ACCOUNT_FILE = Path(os.environ.get("SEARCH_CONSOLE_SERVICE_ACCOUNT", CONFIG_DIR / "service_account.json"))
TOKEN_FILE = Path(os.environ.get("SEARCH_CONSOLE_TOKEN", STATE_DIR / "token.json"))

# Fallback check in config dir if token not in state dir
if not TOKEN_FILE.exists() and (CONFIG_DIR / "token.json").exists():
    TOKEN_FILE = CONFIG_DIR / "token.json"


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

    # If target_url is provided, attempt to match siteUrl
    if target_url:
        parsed = urlparse(target_url)
        host = parsed.netloc.lower()
        if host.startswith("www."):
            host_no_www = host[4:]
        else:
            host_no_www = host

        # 1. Match domain property: sc-domain:host or sc-domain:host_no_www
        for s in site_urls:
            if s == f"sc-domain:{host}" or s == f"sc-domain:{host_no_www}":
                return s

        # 2. Match URL prefix property
        for s in site_urls:
            if s.startswith("http") and host_no_www in s:
                return s

    # Fallback to single site if only one exists
    if len(site_urls) == 1:
        return site_urls[0]

    # Fallback default: memispaintings.com if present
    for s in site_urls:
        if "memispaintings" in s:
            return s

    return site_urls[0]


# --- Commands ---

def cmd_auth(args):
    print("Initiating Google Search Console OAuth authorization...")
    creds = get_credentials(force_auth=True)
    if creds and creds.valid:
        print(f"✅ Authorization successful! Token saved to: {TOKEN_FILE}")
    else:
        print("❌ Authorization failed.")
        sys.exit(1)


def cmd_sites(args):
    _, webmasters = get_services()
    sites = list_sites(webmasters)
    if args.json:
        print(json.dumps(sites, indent=2))
        return

    if not sites:
        print("No verified properties found in Google Search Console.")
        return

    print("\nVerified Search Console Properties:")
    print("-" * 60)
    for s in sites:
        perm = s.get("permissionLevel", "unknown")
        url = s.get("siteUrl", "")
        print(f"• {url:<40} (Permission: {perm})")
    print("-" * 60)


def cmd_inspect(args):
    sc_service, webmasters = get_services()
    site_url = resolve_site_url(webmasters, args.site, args.url)
    
    body = {
        "inspectionUrl": args.url,
        "siteUrl": site_url,
    }
    if args.lang:
        body["languageCode"] = args.lang

    try:
        res = sc_service.urlInspection().index().inspect(body=body).execute()
    except HttpError as err:
        sys.stderr.write(f"API Error ({err.status_code}): {err.error_details}\n")
        sys.exit(1)

    result = res.get("inspectionResult", {})
    if args.json:
        print(json.dumps(result, indent=2))
        return

    idx_res = result.get("indexStatusResult", {})
    verdict = idx_res.get("verdict", "UNKNOWN")
    coverage = idx_res.get("coverageState", "Unknown")
    crawled_as = idx_res.get("crawledAs", "Unknown")
    robots_state = idx_res.get("robotsTxtState", "Unknown")
    indexing_state = idx_res.get("indexingState", "Unknown")
    last_crawl = idx_res.get("lastCrawlTime", "Never")
    user_canonical = idx_res.get("userCanonical", "None declared")
    google_canonical = idx_res.get("googleCanonical", "None selected")
    referring_urls = idx_res.get("referringUrls", [])

    status_icon = "✅" if verdict == "PASS" else ("⚠️" if verdict == "NEUTRAL" else "❌")

    print(f"\n{status_icon} URL Inspection Report: {args.url}")
    print("=" * 70)
    print(f"• Property (Site URL):      {site_url}")
    print(f"• Overall Verdict:          {verdict}")
    print(f"• Coverage State:           {coverage}")
    print(f"• Indexing State:           {indexing_state}")
    print(f"• Robots.txt:               {robots_state}")
    print(f"• Crawled As:               {crawled_as}")
    print(f"• Last Crawl Time:          {last_crawl}")
    print(f"• User Canonical:           {user_canonical}")
    print(f"• Google Canonical:         {google_canonical}")

    if referring_urls:
        print(f"• Discovered via ({len(referring_urls)} sources):")
        for ref in referring_urls[:5]:
            print(f"    - {ref}")

    # Mobile usability
    mobile = result.get("mobileUsabilityResult", {})
    if mobile:
        m_verdict = mobile.get("verdict", "UNKNOWN")
        print(f"• Mobile Usability:         {m_verdict}")
        for issue in mobile.get("issues", []):
            print(f"    ⚠️ {issue.get('issueType')}")

    # Rich results
    rich = result.get("richResultsResult", {})
    if rich:
        r_verdict = rich.get("verdict", "UNKNOWN")
        print(f"• Rich Results:             {r_verdict}")
        for item in rich.get("detectedItems", []):
            for item_type in item.get("items", []):
                print(f"    ✨ {item_type.get('name')}")
    print("=" * 70)


def cmd_sitemaps(args):
    _, webmasters = get_services()
    site_url = resolve_site_url(webmasters, args.site)

    try:
        res = webmasters.sitemaps().list(siteUrl=site_url).execute()
    except HttpError as err:
        sys.stderr.write(f"API Error ({err.status_code}): {err.error_details}\n")
        sys.exit(1)

    sitemaps = res.get("sitemap", [])
    if args.json:
        print(json.dumps(sitemaps, indent=2))
        return

    print(f"\nSitemaps for property: {site_url}")
    print("=" * 75)
    if not sitemaps:
        print("No sitemaps submitted yet.")
        return

    for sm in sitemaps:
        path = sm.get("path", "")
        last_downloaded = sm.get("lastDownloaded", "Never")
        last_submitted = sm.get("lastSubmitted", "")
        has_errors = sm.get("errors", "0")
        has_warnings = sm.get("warnings", "0")
        is_pending = sm.get("isPending", False)

        contents = sm.get("contents", [])
        total_submitted = sum(int(c.get("submitted", 0)) for c in contents)
        total_indexed = sum(int(c.get("indexed", 0)) for c in contents)

        status_str = "PENDING" if is_pending else ("ERRORS" if int(has_errors) > 0 else "SUCCESS")
        icon = "⏳" if is_pending else ("❌" if int(has_errors) > 0 else "✅")

        print(f"{icon} Path: {path}")
        print(f"   Status: {status_str} | Last Downloaded: {last_downloaded} | Submitted: {last_submitted}")
        print(f"   Errors: {has_errors} | Warnings: {has_warnings}")
        if total_submitted > 0 or total_indexed > 0:
            print(f"   URLs Submitted: {total_submitted} | URLs Indexed: {total_indexed}")
        print("-" * 75)


def cmd_sitemap_submit(args):
    _, webmasters = get_services()
    site_url = resolve_site_url(webmasters, args.site, args.feedpath)

    try:
        webmasters.sitemaps().submit(siteUrl=site_url, feedpath=args.feedpath).execute()
        print(f"✅ Sitemap successfully submitted to {site_url}: {args.feedpath}")
    except HttpError as err:
        sys.stderr.write(f"API Error ({err.status_code}): {err.error_details}\n")
        sys.exit(1)


def cmd_performance(args):
    sc_service, webmasters = get_services()
    site_url = resolve_site_url(webmasters, args.site)

    end_date = datetime.date.today() - datetime.timedelta(days=2) # GSC data typically has ~2 days latency
    start_date = end_date - datetime.timedelta(days=args.days)

    dimensions = [d.strip() for d in args.dimensions.split(",") if d.strip()]

    body = {
        "startDate": start_date.strftime("%Y-%m-%d"),
        "endDate": end_date.strftime("%Y-%m-%d"),
        "dimensions": dimensions,
        "rowLimit": args.limit,
    }

    if args.page:
        body["dimensionFilterGroups"] = [{
            "filters": [{
                "dimension": "page",
                "operator": "equals",
                "expression": args.page
            }]
        }]

    try:
        res = sc_service.searchanalytics().query(siteUrl=site_url, body=body).execute()
    except HttpError as err:
        sys.stderr.write(f"API Error ({err.status_code}): {err.error_details}\n")
        sys.exit(1)

    rows = res.get("rows", [])
    if args.json:
        print(json.dumps(rows, indent=2))
        return

    print(f"\nSearch Performance ({start_date} to {end_date}) for {site_url}:")
    print("=" * 80)
    print(f"{'Keys':<45} | {'Clicks':>6} | {'Impr':>7} | {'CTR':>7} | {'Pos':>5}")
    print("-" * 80)

    for r in rows:
        keys_str = " / ".join(r.get("keys", []))
        if len(keys_str) > 43:
            keys_str = keys_str[:40] + "..."
        clicks = r.get("clicks", 0)
        impressions = r.get("impressions", 0)
        ctr = f"{r.get('ctr', 0) * 100:.1f}%"
        position = f"{r.get('position', 0):.1f}"
        print(f"{keys_str:<45} | {clicks:>6} | {impressions:>7} | {ctr:>7} | {position:>5}")
    print("=" * 80)


def main():
    parser = argparse.ArgumentParser(
        description="Google Search Console CLI helper for index inspection, sitemaps, and search analytics."
    )
    subparsers = parser.add_subparsers(dest="subcommand", required=True)

    # auth
    subparsers.add_parser("auth", help="Authorize with Google via OAuth consent flow")

    # sites
    p_sites = subparsers.add_parser("sites", help="List verified Search Console properties")
    p_sites.add_argument("--json", action="store_true", help="Output raw JSON")
    p_sites.set_defaults(func=cmd_sites)

    # inspect
    p_inspect = subparsers.add_parser("inspect", help="Inspect an individual URL (Index Status, Coverage, Canonicals)")
    p_inspect.add_argument("url", help="Exact URL to inspect (e.g. https://memispaintings.com/gallery/)")
    p_inspect.add_argument("--site", help="Search Console siteUrl (e.g. sc-domain:memispaintings.com)")
    p_inspect.add_argument("--lang", default="it", help="Language code for coverage messages (default: it)")
    p_inspect.add_argument("--json", action="store_true", help="Output raw JSON")
    p_inspect.set_defaults(func=cmd_inspect)

    # sitemaps
    p_sitemaps = subparsers.add_parser("sitemaps", help="List submitted sitemaps and status")
    p_sitemaps.add_argument("--site", help="Search Console siteUrl")
    p_sitemaps.add_argument("--json", action="store_true", help="Output raw JSON")
    p_sitemaps.set_defaults(func=cmd_sitemaps)

    # sitemap-submit
    p_submit = subparsers.add_parser("sitemap-submit", help="Submit a sitemap to Search Console")
    p_submit.add_argument("feedpath", help="Full URL of sitemap (e.g. https://memispaintings.com/sitemap.xml)")
    p_submit.add_argument("--site", help="Search Console siteUrl")
    p_submit.set_defaults(func=cmd_sitemap_submit)

    # performance
    p_perf = subparsers.add_parser("performance", help="Query search analytics performance")
    p_perf.add_argument("--site", help="Search Console siteUrl")
    p_perf.add_argument("--days", type=int, default=28, help="Number of days to analyze (default: 28)")
    p_perf.add_argument("--dimensions", default="query", help="Comma-separated dimensions (query,page,country,device)")
    p_perf.add_argument("--page", help="Filter by specific page URL")
    p_perf.add_argument("--limit", type=int, default=25, help="Max rows to return (default: 25)")
    p_perf.add_argument("--json", action="store_true", help="Output raw JSON")
    p_perf.set_defaults(func=cmd_performance)

    args = parser.parse_args()
    if args.subcommand == "auth":
        cmd_auth(args)
    elif hasattr(args, "func"):
        args.func(args)


if __name__ == "__main__":
    main()

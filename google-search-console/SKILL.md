---
name: google-search-console
description: Inspect URL indexing status, coverage issues, canonical discrepancies, sitemaps, and search analytics performance in Google Search Console. Use whenever the user asks about Google Search Console, URL inspection, indexing errors, sitemaps, or organic search traffic.
---

# Google Search Console Skill

This skill allows the agent to interact with **Google Search Console** via the official API using an authenticated CLI helper.

It supports inspecting URL indexing status, analyzing coverage errors (e.g. duplicate pages, canonical mismatches, crawl errors), checking submitted sitemaps, submitting new sitemaps, and querying search performance (clicks, impressions, CTR, average position).

---

## Requirements & Credentials

The CLI helper supports both **OAuth 2.0 Desktop Client** and **Google Cloud Service Account**:

| Item | Location / Variable | Description |
| :--- | :--- | :--- |
| **OAuth Credentials** | `~/.config/google-search-console/credentials.json` | OAuth 2.0 Desktop Client JSON (override: `SEARCH_CONSOLE_CREDENTIALS`) |
| **OAuth Token** | `~/.local/state/google-search-console/token.json` | Generated OAuth session token (override: `SEARCH_CONSOLE_TOKEN`) |
| **Service Account (Alt)** | `~/.config/google-search-console/service_account.json` | Service Account JSON key (override: `SEARCH_CONSOLE_SERVICE_ACCOUNT`) |
| **Default Property** | `GSC_SITE_URL` | Optional default Search Console site URL (e.g. `sc-domain:memispaintings.com`) |

---

## Initial Authentication (OAuth 2.0)

If using OAuth and `~/.local/state/google-search-console/token.json` does not exist or has expired, run:

```bash
uv run $USER_SKILLS_DIR/google-search-console/scripts/search_console.py auth
```

This launches a local web server and opens the Google OAuth consent flow in the browser. Once authorized, the token is saved locally to `~/.local/state/google-search-console/token.json`.

---

## Command Reference

Execute all commands using `uv run`:

```bash
uv run $USER_SKILLS_DIR/google-search-console/scripts/search_console.py <subcommand> [options]
```

### 1. List Verified Properties
Lists all verified sites/properties in the Search Console account:

```bash
uv run $USER_SKILLS_DIR/google-search-console/scripts/search_console.py sites
```
Options:
- `--json`: Output raw JSON list.

---

### 2. Inspect an Individual URL (URL Inspection API)
Inspects the live index status, coverage state, crawling details, and canonical declarations for any URL:

```bash
uv run $USER_SKILLS_DIR/google-search-console/scripts/search_console.py inspect "https://memispaintings.com/gallery/"
```

Inspect with explicit site property:
```bash
uv run $USER_SKILLS_DIR/google-search-console/scripts/search_console.py inspect "https://memispaintings.com/gallery/" --site "sc-domain:memispaintings.com"
```

Output raw JSON:
```bash
uv run $USER_SKILLS_DIR/google-search-console/scripts/search_console.py inspect "https://memispaintings.com/gallery/" --json
```

**Key Information Returned**:
- **Verdict**: `PASS`, `NEUTRAL`, `FAIL`.
- **Coverage State**: e.g., *Submitted and indexed*, *Crawled - currently not indexed*, *Duplicate without user-selected canonical*, *Discovered - currently not indexed*.
- **User Canonical**: Canonical URL declared in HTML by the site.
- **Google Canonical**: Canonical URL chosen by Googlebot.
- **Robots.txt State**: `ALLOWED` or `DISALLOWED`.
- **Last Crawl Time** & **Crawled As** (`MOBILE` or `DESKTOP`).
- **Mobile Usability** & **Rich Results** detection.

---

### 3. View Sitemaps Status
Lists submitted sitemaps for a property, including status, last download date, error/warning count, and submitted vs indexed URL counts:

```bash
uv run $USER_SKILLS_DIR/google-search-console/scripts/search_console.py sitemaps
```

Specific property:
```bash
uv run $USER_SKILLS_DIR/google-search-console/scripts/search_console.py sitemaps --site "sc-domain:memispaintings.com"
```

---

### 4. Submit / Re-submit a Sitemap
Submits or asks Google to re-crawl a sitemap URL:

```bash
uv run $USER_SKILLS_DIR/google-search-console/scripts/search_console.py sitemap-submit "https://memispaintings.com/sitemap.xml"
```

---

### 5. Search Analytics & Performance
Queries search performance data (clicks, impressions, CTR, position) over a specified time window:

```bash
# Top queries over the last 28 days
uv run $USER_SKILLS_DIR/google-search-console/scripts/search_console.py performance --days 28

# Top pages
uv run $USER_SKILLS_DIR/google-search-console/scripts/search_console.py performance --dimensions page --limit 20

# Performance for a specific page URL
uv run $USER_SKILLS_DIR/google-search-console/scripts/search_console.py performance --page "https://memispaintings.com/gallery/" --dimensions query
```

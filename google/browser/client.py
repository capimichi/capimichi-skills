#!/usr/bin/env python3
"""
Google & Web Automation Client with CloakBrowser.
Fornisce funzionalità di ricerca Google strutturata, apertura pagine con stealth anti-bot e ispezione DOM.
"""

import os
import sys
import time
import urllib.parse
from typing import Any, Dict, List, Optional
from pathlib import Path

# Assicura import dei moduli locali
current_dir = Path(__file__).resolve().parent
if str(current_dir) not in sys.path:
    sys.path.insert(0, str(current_dir))

from browser import (
    accept_google_cookies,
    get_cache_dir,
    get_profile_dir,
    launch_browser,
)


def search_google(
    query: str,
    limit: int = 10,
    headless: bool = True,
    language: str = "it",
    country: str = "it",
) -> List[Dict[str, Any]]:
    """
    Esegue una ricerca su Google ed estrae i risultati organici (titolo, URL, snippet).
    """
    encoded_query = urllib.parse.quote_plus(query)
    search_url = f"https://www.google.com/search?q={encoded_query}&hl={language}&gl={country}"

    context = launch_browser(headless=headless)
    page = context.new_page()
    results: List[Dict[str, Any]] = []

    try:
        page.goto(search_url, wait_until="domcontentloaded", timeout=25000)
        page.wait_for_timeout(1000)

        # Gestione del cookie consent banner se presente
        accept_google_cookies(page)
        page.wait_for_timeout(1000)

        # Estrazione diretta ed efficiente dei risultati tramite i link contenenti h3
        links = page.locator("a:has(h3)").all()

        for a in links:
            if len(results) >= limit:
                break

            try:
                h3 = a.locator("h3").first
                if h3.count() == 0:
                    continue
                title = h3.inner_text().strip()
                if not title:
                    continue

                # Estrazione URL pulito: preferisce il tag <cite>, altrimenti l'href
                raw_href = a.get_attribute("href") or ""
                cite_el = a.locator("cite").first
                if cite_el.count() > 0:
                    clean_url = cite_el.inner_text().strip()
                    if not clean_url.startswith("http://") and not clean_url.startswith("https://"):
                        clean_url = f"https://{clean_url}"
                elif raw_href.startswith("http://") or raw_href.startswith("https://"):
                    clean_url = raw_href
                else:
                    clean_url = f"https://www.google.com{raw_href}" if raw_href.startswith("/") else raw_href

                # Evita query interne di Google
                if "google.com/search" in clean_url or "maps.google." in clean_url:
                    continue

                if any(r["url"] == clean_url for r in results):
                    continue

                # Snippet descrittivo dall'elemento contenitore
                snippet = ""
                parent = a.locator('xpath=ancestor::div[contains(@class, "MjjYud") or contains(@class, "g") or contains(@class, "tF2Cpc")]').first
                if parent.count() > 0:
                    snip_el = parent.locator("div.VwiC3b, div.yXK7lf, div[data-sncf]").first
                    if snip_el.count() > 0:
                        snippet = snip_el.inner_text().strip().replace("\n", " ")

                results.append({
                    "title": title,
                    "url": clean_url,
                    "snippet": snippet,
                })
            except Exception:
                continue

    finally:
        context.close()

    return results


def open_webpage(
    url: str,
    headless: bool = False,
    wait_sec: int = 5,
    screenshot_name: Optional[str] = None,
    extract_text: bool = False,
    interactive: bool = False,
) -> Dict[str, Any]:
    """
    Apre un qualsiasi URL web con CloakBrowser sfruttando la sessione persistente e protezioni anti-bot.
    """
    if not url.startswith("http://") and not url.startswith("https://"):
        url = f"https://{url}"

    context = launch_browser(headless=headless)
    page = context.new_page()
    cache_dir = get_cache_dir()

    data: Dict[str, Any] = {
        "url": url,
        "final_url": "",
        "title": "",
        "screenshot": None,
        "text": None,
    }

    try:
        print(f"Navigazione stealth verso: {url}...")
        page.goto(url, wait_until="domcontentloaded", timeout=45000)

        # Se siamo su Google, prova ad accettare i cookie
        if "google." in page.url:
            accept_google_cookies(page)

        if wait_sec > 0:
            page.wait_for_timeout(wait_sec * 1000)

        data["final_url"] = page.url
        data["title"] = page.title()

        if screenshot_name:
            if not screenshot_name.endswith(".png"):
                screenshot_name = f"{screenshot_name}.png"
            dest_path = cache_dir / screenshot_name
            page.screenshot(path=str(dest_path), full_page=False)
            data["screenshot"] = str(dest_path)
            print(f"Screenshot salvato in: {dest_path}")

        if extract_text:
            body_text = page.inner_text("body")
            # Pulizia linee vuote
            cleaned_lines = [l.strip() for l in body_text.splitlines() if l.strip()]
            data["text"] = "\n".join(cleaned_lines[:200])  # Prime 200 righe

        if interactive:
            print("\n" + "=" * 70)
            print("👉 BROWSER INTERATTIVO APERTO")
            print("Puoi interagire con la pagina. Il processo rimarrà attivo finché")
            print("non chiudi la finestra del browser o premi [INVIO] nella console.")
            print("=" * 70 + "\n")
            try:
                while True:
                    time.sleep(1.5)
                    if not context.pages or all(p.is_closed() for p in context.pages):
                        break
            except (KeyboardInterrupt, EOFError):
                pass
    finally:
        try:
            context.close()
        except Exception:
            pass

    return data


def inspect_webpage(
    url: str,
    selector: Optional[str] = None,
    headless: bool = True,
) -> Dict[str, Any]:
    """
    Estrae metadati, titolo e contenuti specifici da una pagina web tramite selettore CSS.
    """
    if not url.startswith("http://") and not url.startswith("https://"):
        url = f"https://{url}"

    context = launch_browser(headless=headless)
    page = context.new_page()
    result: Dict[str, Any] = {
        "url": url,
        "title": "",
        "description": "",
        "elements": [],
    }

    try:
        page.goto(url, wait_until="domcontentloaded", timeout=30000)
        page.wait_for_timeout(2000)

        if "google." in page.url:
            accept_google_cookies(page)

        result["title"] = page.title()

        # Meta description
        meta_desc = page.locator("meta[name='description'], meta[property='og:description']").first
        if meta_desc.count() > 0:
            result["description"] = meta_desc.get_attribute("content") or ""

        # Selettore specifico o intestazioni
        if selector:
            matches = page.locator(selector).all()
            for idx, el in enumerate(matches[:50], 1):
                try:
                    txt = el.inner_text().strip()
                    href = el.get_attribute("href") or ""
                    item = {"index": idx, "text": txt}
                    if href:
                        item["href"] = href
                    result["elements"].append(item)
                except Exception:
                    continue
        else:
            headings = []
            for h in page.locator("h1, h2, h3").all()[:15]:
                txt = h.inner_text().strip()
                if txt and txt not in headings:
                    headings.append(txt)
            result["headings"] = headings
    finally:
        context.close()

    return result


def check_google_session(headless: bool = True) -> Dict[str, Any]:
    """
    Verifica se il profilo browser corrente ha una sessione Google autenticata.
    """
    context = launch_browser(headless=headless)
    page = context.new_page()
    status = {
        "is_logged_in": False,
        "account_info": "Nessun account Google connesso (navigazione anonima)",
        "url": "",
    }

    try:
        page.goto("https://myaccount.google.com/", wait_until="domcontentloaded", timeout=25000)
        page.wait_for_timeout(2000)
        accept_google_cookies(page)

        status["url"] = page.url
        if "accounts.google.com/ServiceLogin" not in page.url and "myaccount.google.com" in page.url:
            status["is_logged_in"] = True
            title = page.title()
            status["account_info"] = f"Account autenticato ({title})"
    finally:
        context.close()

    return status

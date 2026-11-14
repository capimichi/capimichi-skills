#!/usr/bin/env python3
"""
Ricerca di prodotti su Amazon.it tramite browser virtuale.
Utilizza la sessione salvata nella directory XDG.
Supporta output formattato per terminale e JSON.
"""

import argparse
import json
import re
import sys
import urllib.parse
from pathlib import Path
from typing import Any, Dict, List

CURRENT_DIR = Path(__file__).resolve().parent
if str(CURRENT_DIR) not in sys.path:
    sys.path.insert(0, str(CURRENT_DIR))

from browser import (
    AMAZON_BASE_URL,
    accept_cookies_if_present,
    launch_amazon_browser,
    take_screenshot,
)


def search_amazon(
    query: str,
    limit: int = 10,
    headless: bool = True,
    sort: str = "relevanceblender",
) -> List[Dict[str, Any]]:
    """
    Esegue una ricerca su Amazon.it e restituisce i dettagli strutturati dei prodotti.

    Args:
        query: Parola chiave di ricerca (es. 'mouse wireless').
        limit: Numero massimo di risultati da estrarre.
        headless: Esegui senza interfaccia grafica (True) o visibile (False).
        sort: Ordinamento Amazon (relevanceblender, price-asc-rank, price-desc-rank, review-rank).
    """
    encoded_query = urllib.parse.quote_plus(query)
    search_url = f"{AMAZON_BASE_URL}/s?k={encoded_query}&s={sort}"

    context = launch_amazon_browser(headless=headless)
    page = context.new_page()
    results = []

    try:
        page.goto(search_url, wait_until="domcontentloaded", timeout=30000)
        page.wait_for_timeout(1500)
        accept_cookies_if_present(page)

        # Attesa della griglia risultati
        try:
            page.wait_for_selector(
                "div[data-component-type='s-search-result'], div[data-asin]",
                timeout=8000,
            )
        except Exception:
            take_screenshot(page, "search_no_results.png")
            return []

        cards = page.locator("div[data-component-type='s-search-result']").all()

        for card in cards:
            if len(results) >= limit:
                break

            asin = card.get_attribute("data-asin") or ""
            if not asin or asin.strip() == "":
                continue

            # Titolo e link
            title = ""
            url = ""
            try:
                title_elem = card.locator("h2 a").first
                if title_elem.count() > 0:
                    title = title_elem.inner_text().strip()
                    href = title_elem.get_attribute("href") or ""
                    if href.startswith("/"):
                        url = f"{AMAZON_BASE_URL}{href}"
                    else:
                        url = href
            except Exception:
                pass

            if not title:
                # Prova fallback su qualsiasi h2
                try:
                    title = card.locator("h2").first.inner_text().strip()
                except Exception:
                    continue

            # Prezzo
            price_str = ""
            try:
                price_elem = card.locator("span.a-price span.a-offscreen").first
                if price_elem.count() > 0:
                    price_str = price_elem.inner_text().strip()
                else:
                    whole = card.locator(".a-price-whole").first.inner_text().strip()
                    fraction = card.locator(".a-price-fraction").first.inner_text().strip()
                    price_str = f"{whole},{fraction} €"
            except Exception:
                pass

            # Valutazione (stelle)
            rating = ""
            try:
                rating_elem = card.locator("i.a-icon-star-small span.a-icon-alt, span[aria-label*='su 5 stelle']").first
                if rating_elem.count() > 0:
                    rating = rating_elem.inner_text().strip()
            except Exception:
                pass

            # Numero recensioni
            reviews_count = ""
            try:
                rev_elem = card.locator("span.a-size-base.s-underline-text, a[href*='#customerReviews'] span").first
                if rev_elem.count() > 0:
                    reviews_count = rev_elem.inner_text().strip()
            except Exception:
                pass

            # Prime & Sponsorizzato
            is_prime = card.locator("i.a-icon-prime, span[aria-label*='Prime']").count() > 0
            is_sponsored = (
                card.locator("span.puis-sponsored-label-text").count() > 0
                or "sponsorizzato" in card.inner_text().lower()[:100]
            )

            # Badge / Scelta Amazon
            badge = ""
            try:
                badge_elem = card.locator("span.a-badge-text").first
                if badge_elem.count() > 0:
                    badge = badge_elem.inner_text().strip()
            except Exception:
                pass

            results.append({
                "asin": asin,
                "title": title,
                "price": price_str or "N/D",
                "rating": rating or "N/D",
                "reviews_count": reviews_count or "0",
                "is_prime": is_prime,
                "is_sponsored": is_sponsored,
                "badge": badge,
                "url": url,
            })

    finally:
        try:
            context.close()
        except Exception:
            pass

    return results


def main():
    parser = argparse.ArgumentParser(description="Ricerca prodotti su Amazon.it")
    parser.add_argument("query", help="Termine di ricerca (es. 'caricatore usb c')")
    parser.add_argument("--limit", "-l", type=int, default=10, help="Numero massimo di prodotti (default: 10)")
    parser.add_argument("--visible", action="store_true", help="Mostra il browser invece di girare in headless")
    parser.add_argument("--json", action="store_true", help="Output in formato JSON")
    parser.add_argument(
        "--sort",
        default="relevanceblender",
        choices=["relevanceblender", "price-asc-rank", "price-desc-rank", "review-rank"],
        help="Criterio di ordinamento",
    )

    args = parser.parse_args()

    results = search_amazon(
        query=args.query,
        limit=args.limit,
        headless=not args.visible,
        sort=args.sort,
    )

    if args.json:
        print(json.dumps(results, indent=2, ensure_ascii=False))
        return

    print("=" * 75)
    print(f"🔍 RISULTATI RICERCA AMAZON.IT PER: '{args.query}' (Trovati: {len(results)})")
    print("=" * 75)

    if not results:
        print("Nessun prodotto trovato o pagina protetta da verifica.")
        return

    for idx, item in enumerate(results, start=1):
        prime_badge = " [⚡ Prime]" if item["is_prime"] else ""
        spon_badge = " [Sponsorizzato]" if item["is_sponsored"] else ""
        badge_str = f" [{item['badge']}]" if item["badge"] else ""

        print(f"\n{idx}. {item['title'][:90]}...")
        print(f"   💰 Prezzo: {item['price']}{prime_badge}{badge_str}{spon_badge}")
        print(f"   ⭐ Valutazione: {item['rating']} ({item['reviews_count']} recensioni)")
        print(f"   🆔 ASIN: {item['asin']}")
        if item["url"]:
            print(f"   🔗 Link: {item['url']}")

    print("\n" + "=" * 75)


if __name__ == "__main__":
    main()

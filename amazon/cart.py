#!/usr/bin/env python3
"""
Visualizzazione e ispezione rapida del carrello Amazon.it.
Utilizza la sessione salvata nella directory XDG.
"""

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any, Dict, List

CURRENT_DIR = Path(__file__).resolve().parent
if str(CURRENT_DIR) not in sys.path:
    sys.path.insert(0, str(CURRENT_DIR))

from browser import (
    AMAZON_BASE_URL,
    accept_cookies_if_present,
    check_amazon_login,
    launch_amazon_browser,
)


def get_cart_contents(headless: bool = True) -> Dict[str, Any]:
    cart_url = f"{AMAZON_BASE_URL}/gp/cart/view.html"
    context = launch_amazon_browser(headless=headless)
    page = context.pages[0] if context.pages else context.new_page()

    result: Dict[str, Any] = {
        "logged_in": False,
        "subtotal": "0,00 €",
        "items_count": 0,
        "items": [],
    }

    try:
        page.goto(cart_url, wait_until="domcontentloaded", timeout=20000)
        page.wait_for_timeout(1000)
        accept_cookies_if_present(page, timeout_ms=1000)

        login_status = check_amazon_login(page)
        result["logged_in"] = login_status["is_logged_in"]

        # Subtotale
        try:
            subtotal_elem = page.locator(
                "#sc-subtotal-amount-activecart .sc-price, #sc-subtotal-amount-buybox .sc-price, #sc-subtotal-amount-activecart"
            ).first
            if subtotal_elem.count() > 0:
                result["subtotal"] = subtotal_elem.inner_text(timeout=1000).strip().replace("\xa0", " ")
        except Exception:
            pass

        # Articoli attivi nel carrello (utilizziamo il form del carrello attivo per evitare elementi salvati per dopo o sponsorizzati)
        items = page.locator("#activeCartViewForm [data-asin]").all()
        for it in items:
            try:
                asin = it.get_attribute("data-asin") or ""
                if not asin or len(asin) != 10:
                    continue

                # Titolo
                title = ""
                title_elem = it.locator(".a-truncate-cut, .sc-product-title, a[href*='/dp/']").first
                if title_elem.count() > 0:
                    title = title_elem.inner_text(timeout=1000).strip()
                if not title:
                    continue

                # Prezzo
                price = "N/D"
                price_elem = it.locator(".sc-price, .sc-product-price, .a-price .a-offscreen").first
                if price_elem.count() > 0:
                    price = price_elem.inner_text(timeout=1000).strip().replace("\xa0", " ")

                # Quantità
                qty = "1"
                try:
                    qty_elem = it.locator(".sc-action-quantity legend, .sc-action-quantity, span.a-dropdown-prompt").first
                    if qty_elem.count() > 0:
                        txt = qty_elem.inner_text(timeout=800)
                        m = re.search(r"(\d+)", txt)
                        if m:
                            qty = m.group(1)
                except Exception:
                    pass

                result["items"].append({
                    "asin": asin,
                    "title": title,
                    "price": price,
                    "quantity": qty,
                })
            except Exception:
                continue

        result["items_count"] = len(result["items"])

        if not headless:
            print("[INFO] Finestra visibile: chiusura automatica tra 3 secondi...")
            page.wait_for_timeout(3000)

    finally:
        try:
            context.close()
        except Exception:
            pass

    return result


def main():
    parser = argparse.ArgumentParser(description="Ispeziona il carrello di Amazon.it")
    parser.add_argument("--visible", action="store_true", help="Mostra il browser")
    parser.add_argument("--json", action="store_true", help="Output JSON")
    args = parser.parse_args()

    data = get_cart_contents(headless=not args.visible)

    if args.json:
        print(json.dumps(data, indent=2, ensure_ascii=False))
        return

    print("=" * 70)
    print("🛒 CARRELLO AMAZON.IT")
    print("=" * 70)
    status_icon = "🟢 Connesso" if data["logged_in"] else "🟡 Anonimo / Non loggato"
    print(f"Stato sessione:  {status_icon}")
    print(f"Numero articoli: {data['items_count']}")
    print(f"Subtotale:       {data['subtotal']}")
    print("-" * 70)

    if not data["items"]:
        print("Il carrello è vuoto.")
    else:
        for idx, item in enumerate(data["items"], 1):
            print(f"{idx}. {item['title'][:80]}")
            print(f"   💰 Prezzo: {item['price']}  |  🔢 Quantità: {item['quantity']}  |  🆔 ASIN: {item['asin']}")

    print("=" * 70)


if __name__ == "__main__":
    main()

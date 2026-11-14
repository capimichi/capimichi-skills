#!/usr/bin/env python3
"""
Consultazione degli ordini recenti su Amazon.it.
Richiede una sessione autenticata salvata tramite 'login.py'.
"""

import argparse
import json
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
    take_screenshot,
)


def get_amazon_orders(limit: int = 5, headless: bool = True) -> Dict[str, Any]:
    orders_url = f"{AMAZON_BASE_URL}/your-orders/orders"
    context = launch_amazon_browser(headless=headless)
    page = context.pages[0] if context.pages else context.new_page()

    result: Dict[str, Any] = {
        "logged_in": False,
        "orders_count": 0,
        "orders": [],
    }

    try:
        page.goto(orders_url, wait_until="domcontentloaded", timeout=20000)
        page.wait_for_timeout(1000)
        accept_cookies_if_present(page, timeout_ms=1000)

        login_status = check_amazon_login(page)
        result["logged_in"] = login_status["is_logged_in"]

        if not login_status["is_logged_in"]:
            take_screenshot(page, "orders_login_required.png")
            return result

        order_cards = page.locator(".order-card, .order, div[data-component-type='order']").all()
        for card in order_cards:
            if len(result["orders"]) >= limit:
                break

            order_data: Dict[str, Any] = {
                "order_id": "",
                "order_date": "",
                "total": "",
                "recipient": "",
                "items": [],
            }

            try:
                # Numero ordine
                oid_elem = card.locator("bdi[dir='ltr'], .yohtmlc-order-id span, span:has-text('Ordine n.') + span").first
                if oid_elem.count() > 0:
                    order_data["order_id"] = oid_elem.inner_text(timeout=800).strip()

                # Data ordine
                date_elem = card.locator(".order-header span.value, .a-column:has-text('Ordine effettuato') span.value").first
                if date_elem.count() > 0:
                    order_data["order_date"] = date_elem.inner_text(timeout=800).strip()

                # Totale
                tot_elem = card.locator(".order-header span:has-text('Totale') + span, .yohtmlc-order-total span.value").first
                if tot_elem.count() > 0:
                    order_data["total"] = tot_elem.inner_text(timeout=800).strip()

                # Destinatario
                recip_elem = card.locator(".yohtmlc-recipient span.trigger-text").first
                if recip_elem.count() > 0:
                    order_data["recipient"] = recip_elem.inner_text(timeout=800).strip()

                # Articoli nell'ordine
                titles = card.locator(".yohtmlc-item a:not([class*='action']), .a-fixed-left-grid-col.a-col-right a[href*='/gp/product/'], .a-fixed-left-grid-col.a-col-right a[href*='/dp/']").all()
                for t in titles:
                    txt = t.inner_text(timeout=800).strip()
                    if txt and txt not in order_data["items"] and len(txt) > 3:
                        order_data["items"].append(txt)

                result["orders"].append(order_data)
            except Exception:
                continue

        result["orders_count"] = len(result["orders"])

        if not headless:
            page.wait_for_timeout(3000)

    finally:
        try:
            context.close()
        except Exception:
            pass

    return result


def main():
    parser = argparse.ArgumentParser(description="Mostra gli ordini recenti su Amazon.it")
    parser.add_argument("--limit", "-l", type=int, default=5, help="Numero di ordini da mostrare")
    parser.add_argument("--visible", action="store_true", help="Mostra il browser")
    parser.add_argument("--json", action="store_true", help="Output JSON")
    args = parser.parse_args()

    data = get_amazon_orders(limit=args.limit, headless=not args.visible)

    if args.json:
        print(json.dumps(data, indent=2, ensure_ascii=False))
        return

    print("=" * 70)
    print("📦 I MIEI ORDINI AMAZON.IT")
    print("=" * 70)

    if not data["logged_in"]:
        print("❌ Non risulti autenticato!")
        print("Esegui prima lo script per effettuare il login manuale:")
        print("  python3 login.py")
        print("=" * 70)
        return

    print(f"Ordini estratti: {data['orders_count']}")
    print("-" * 70)

    if not data["orders"]:
        print("Nessun ordine trovato nella pagina recente.")
    else:
        for idx, o in enumerate(data["orders"], 1):
            print(f"\n{idx}. Ordine #{o['order_id'] or 'N/D'}")
            print(f"   📅 Data: {o['order_date'] or 'N/D'}  |  💰 Totale: {o['total'] or 'N/D'}")
            if o["recipient"]:
                print(f"   👤 Destinatario: {o['recipient']}")
            if o["items"]:
                print("   Articoli:")
                for item in o["items"]:
                    print(f"     • {item[:80]}")

    print("\n" + "=" * 70)


if __name__ == "__main__":
    main()

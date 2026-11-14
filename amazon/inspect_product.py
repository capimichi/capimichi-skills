#!/usr/bin/env python3
"""
Ispezione dettagliata di una scheda prodotto Amazon.it tramite ASIN o URL completo.
Estrae titolo, prezzo, disponibilità, venditore/spedizione, recensioni e punti chiave.
"""

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any, Dict

CURRENT_DIR = Path(__file__).resolve().parent
if str(CURRENT_DIR) not in sys.path:
    sys.path.insert(0, str(CURRENT_DIR))

from browser import (
    AMAZON_BASE_URL,
    accept_cookies_if_present,
    launch_amazon_browser,
    take_screenshot,
)


def extract_asin(query: str) -> str:
    """Estrae l'ASIN da un URL o restituisce la stringa se è già un ASIN valido."""
    match = re.search(r"(?:/dp/|/gp/product/|/d/)([A-Z0-9]{10})", query)
    if match:
        return match.group(1)
    cleaned = query.strip()
    if len(cleaned) == 10 and cleaned.isalnum():
        return cleaned.upper()
    return cleaned


def inspect_product(asin_or_url: str, headless: bool = True) -> Dict[str, Any]:
    asin = extract_asin(asin_or_url)
    if asin_or_url.startswith("http"):
        target_url = asin_or_url
    else:
        target_url = f"{AMAZON_BASE_URL}/dp/{asin}"

    context = launch_amazon_browser(headless=headless)
    page = context.new_page()
    data: Dict[str, Any] = {
        "asin": asin,
        "url": target_url,
        "title": "",
        "price": "",
        "availability": "",
        "seller": "",
        "shipper": "",
        "rating": "",
        "reviews_count": "",
        "bullet_points": [],
    }

    try:
        page.goto(target_url, wait_until="domcontentloaded", timeout=30000)
        page.wait_for_timeout(1500)
        accept_cookies_if_present(page)

        # Titolo
        try:
            title_elem = page.locator("#productTitle").first
            if title_elem.count() > 0:
                data["title"] = title_elem.inner_text().strip()
        except Exception:
            pass

        # Prezzo
        price_selectors = [
            "#corePrice_feature_div .a-price .a-offscreen",
            "#corePriceDisplay_desktop_feature_div .a-price .a-offscreen",
            "#apex_desktop .a-price .a-offscreen",
            ".priceToPay .a-price .a-offscreen",
            "span.a-price span.a-offscreen",
        ]
        for sel in price_selectors:
            try:
                p_elem = page.locator(sel).first
                if p_elem.count() > 0:
                    val = p_elem.text_content().strip()
                    if val and "€" in val:
                        data["price"] = val.replace("\xa0", " ")
                        break
            except Exception:
                continue

        # Fallback parsing da whole + fraction
        if not data["price"]:
            try:
                price_js = page.evaluate('''() => {
                    const whole = document.querySelector(".priceToPay .a-price-whole, #corePriceDisplay_desktop_feature_div .a-price-whole, .a-price-whole");
                    const frac = document.querySelector(".priceToPay .a-price-fraction, #corePriceDisplay_desktop_feature_div .a-price-fraction, .a-price-fraction");
                    if (whole) {
                        const w = whole.innerText.replace(/[^0-9]/g, "");
                        const f = frac ? frac.innerText.replace(/[^0-9]/g, "") : "00";
                        return w ? `${w},${f} €` : "";
                    }
                    return "";
                }''')
                if price_js:
                    data["price"] = price_js
            except Exception:
                pass

        # Disponibilità
        try:
            avail_elem = page.locator("#availability span").first
            if avail_elem.count() > 0:
                data["availability"] = avail_elem.inner_text().strip()
        except Exception:
            pass

        # Spedito da / Venduto da
        try:
            merchant_elem = page.locator("#merchant-info").first
            if merchant_elem.count() > 0:
                text = merchant_elem.inner_text().strip()
                data["seller"] = text
            else:
                shipper = page.locator("#tabular-buybox .tabular-buybox-text:has-text('Amazon')").first
                if shipper.count() > 0:
                    data["shipper"] = "Amazon"
        except Exception:
            pass

        # Valutazione e numero recensioni
        try:
            rating_elem = page.locator("#acrPopover span.a-icon-alt, #averageCustomerReviews .a-icon-alt").first
            if rating_elem.count() > 0:
                data["rating"] = rating_elem.inner_text().strip()
        except Exception:
            pass

        try:
            rev_elem = page.locator("#acrCustomerReviewText").first
            if rev_elem.count() > 0:
                data["reviews_count"] = rev_elem.inner_text().strip()
        except Exception:
            pass

        # Punti elenco / Caratteristiche salienti
        try:
            bullets = page.locator("#feature-bullets ul li span.a-list-item").all()
            for b in bullets:
                txt = b.inner_text().strip()
                if txt and not txt.startswith("›"):
                    data["bullet_points"].append(txt)
        except Exception:
            pass

    finally:
        try:
            context.close()
        except Exception:
            pass

    return data


def main():
    parser = argparse.ArgumentParser(description="Ispeziona un prodotto su Amazon.it")
    parser.add_argument("target", help="ASIN (10 caratteri) o URL del prodotto")
    parser.add_argument("--visible", action="store_true", help="Mostra il browser")
    parser.add_argument("--json", action="store_true", help="Output JSON")
    args = parser.parse_args()

    info = inspect_product(args.target, headless=not args.visible)

    if args.json:
        print(json.dumps(info, indent=2, ensure_ascii=False))
        return

    print("=" * 75)
    print(f"📦 SCHEDA PRODOTTO: {info['title'] or 'Titolo non rilevato'}")
    print("=" * 75)
    print(f"🆔 ASIN:          {info['asin']}")
    print(f"💰 Prezzo:        {info['price'] or 'N/D'}")
    print(f"📦 Disponibilità: {info['availability'] or 'N/D'}")
    if info["seller"]:
        print(f"🏪 Venditore:     {info['seller']}")
    if info["rating"]:
        print(f"⭐ Valutazione:   {info['rating']} ({info['reviews_count']})")
    print(f"🔗 Link:          {info['url']}")

    if info["bullet_points"]:
        print("\n📝 Caratteristiche principali:")
        for idx, pt in enumerate(info["bullet_points"][:5], 1):
            print(f"  • {pt}")
    print("=" * 75)


if __name__ == "__main__":
    main()

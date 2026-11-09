#!/usr/bin/env python3
import sys
import argparse
from client import MircrewBrowser


def main():
    parser = argparse.ArgumentParser(description="Cerca release su Mircrew-releases.org con CloakBrowser")
    parser.add_argument("query", help="Termine di ricerca (es. 'Matrix', 'Inception', 'Dune')")
    parser.add_argument("--all-fields", action="store_true", help="Cerca in tutti i campi (default: solo titolo)")
    parser.add_argument("--limit", type=int, default=15, help="Numero massimo di risultati da mostrare (default: 15)")
    parser.add_argument("--magnets", action="store_true", help="Estrae automaticamente i magnet del primo risultato")
    parser.add_argument("--headless", action="store_true", help="Avvia in modalità headless")

    args = parser.parse_args()

    print(f"🔎 Ricerca su Mircrew per: '{args.query}'...")
    with MircrewBrowser(headless=args.headless) as browser:
        results = browser.search(args.query, title_only=not args.all_fields, limit=args.limit)

        if not results:
            print(f"Nessun risultato trovato per '{args.query}'.")
            return

        print(f"\n✅ Trovati {len(results)} risultati:")
        print("=" * 80)
        for idx, item in enumerate(results, 1):
            category_tag = f"[{item['forum']}] " if item['forum'] else ""
            print(f"{idx:2d}. {category_tag}{item['title']}")
            print(f"    Topic ID: {item['id']} | URL: {item['url']}")
        print("=" * 80)

        if args.magnets and results:
            first = results[0]
            print(f"\n🧲 Estrazione magnet per: {first['title']}...")
            details = browser.get_topic_details(first['url'], auto_thank=True)
            if details["magnets"]:
                print(f"Trovati {len(details['magnets'])} magnet:")
                for m in details["magnets"]:
                    print(f"  -> {m}")
            else:
                print("Nessun link magnet trovato nel topic.")


if __name__ == "__main__":
    main()

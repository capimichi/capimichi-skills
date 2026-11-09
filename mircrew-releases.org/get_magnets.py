#!/usr/bin/env python3
import sys
import argparse
from client import MircrewBrowser


def main():
    parser = argparse.ArgumentParser(description="Estrae i link magnet da un topic di Mircrew-releases.org")
    parser.add_argument("topic", help="URL del topic o ID numerico (es. 40075 o 'https://mircrew-releases.org/viewtopic.php?t=40075')")
    parser.add_argument("--no-thank", action="store_true", help="Non cliccare automaticamente sul tasto Ringrazia")
    parser.add_argument("--headless", action="store_true", help="Avvia in modalità headless")

    args = parser.parse_args()

    print(f"🧲 Recupero dettagli per topic: {args.topic}...")
    with MircrewBrowser(headless=args.headless) as browser:
        details = browser.get_topic_details(args.topic, auto_thank=not args.no_thank)

        print(f"\nTitolo: {details['title']}")
        print(f"URL: {details['url']}")
        print("=" * 80)

        if details["magnets"]:
            print(f"\n✅ Trovati {len(details['magnets'])} link Magnet:")
            for idx, m in enumerate(details["magnets"], 1):
                print(f"[{idx}] {m}")
        else:
            print("\n⚠️ Nessun link Magnet trovato nel post.")

        if details["torrent_links"]:
            print(f"\n📁 Trovati {len(details['torrent_links'])} link Torrent:")
            for idx, t in enumerate(details["torrent_links"], 1):
                print(f"[{idx}] {t}")


if __name__ == "__main__":
    main()

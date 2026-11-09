#!/usr/bin/env python3
"""
Elenca o cerca corrispondenti, tag e tipi di documento su Paperless-ngx.
"""

import sys
import json
import argparse
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from paperless.client import PaperlessClient


def main():
    parser = argparse.ArgumentParser(description="Gestione e consultazione metadati Paperless-ngx")
    parser.add_argument("entity", choices=["correspondents", "tags", "types", "all"], default="all", nargs="?",
                        help="Entità da mostrare: correspondents, tags, types, o all (default: all)")
    parser.add_argument("-s", "--search", help="Filtra per nome (ricerca parziale)")
    parser.add_argument("--json", action="store_true", help="Output in formato JSON")

    args = parser.parse_args()

    try:
        client = PaperlessClient()
    except Exception as e:
        print(e, file=sys.stderr)
        sys.exit(1)

    entities = {}
    if args.entity in ("correspondents", "all"):
        entities["Corrispondenti (Mittenti)"] = client.list_correspondents(search=args.search)
    if args.entity in ("tags", "all"):
        entities["Tag"] = client.list_tags(search=args.search)
    if args.entity in ("types", "all"):
        entities["Tipi Documento"] = client.list_document_types(search=args.search)

    if args.json:
        print(json.dumps(entities, indent=2, ensure_ascii=False))
        return

    for title, items in entities.items():
        print(f"\n📁 {title} ({len(items)} trovati):")
        print("-" * 60)
        if not items:
            print("  Nessun elemento.")
            continue
        for item in sorted(items, key=lambda x: x["name"].lower()):
            doc_count = item.get("document_count", "-")
            count_str = f" ({doc_count} doc)" if doc_count != "-" else ""
            print(f"  [{item['id']:3d}] {item['name']}{count_str}")


if __name__ == "__main__":
    main()

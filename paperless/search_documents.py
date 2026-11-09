#!/usr/bin/env python3
"""
Cerca documenti su Paperless-ngx per testo, corrispondente, tag, tipo documento o anno.
"""

import sys
import json
import argparse
from pathlib import Path

# Permette import sia relativo che assoluto
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from paperless.client import PaperlessClient


def main():
    parser = argparse.ArgumentParser(description="Ricerca documenti su Paperless-ngx")
    parser.add_argument("query", nargs="?", default=None, help="Query full-text di ricerca (testo o titolo)")
    parser.add_argument("-q", "--text", dest="query_flag", help="Testo di ricerca alternativo")
    parser.add_argument("-c", "--correspondent", help="Nome o ID del mittente/corrispondente (es. AASS)")
    parser.add_argument("-t", "--tag", action="append", help="Nome o ID del tag (ripetibile: -t bolletta -t luce)")
    parser.add_argument("--type", help="Tipo di documento (es. Fattura, Ricevuta, Avviso)")
    parser.add_argument("-y", "--year", help="Anno di creazione (es. 2026)")
    parser.add_argument("-n", "--limit", type=int, default=15, help="Numero massimo di risultati da mostrare (default: 15)")
    parser.add_argument("--page", type=int, default=1, help="Numero pagina (default: 1)")
    parser.add_argument("--sort", default="-created", help="Ordinamento (default: -created)")
    parser.add_argument("--content", action="store_true", help="Mostra uno snippet del contenuto OCR estratto")
    parser.add_argument("--json", action="store_true", help="Stampa l'output grezzo in formato JSON")

    args = parser.parse_args()
    search_query = args.query or args.query_flag

    try:
        client = PaperlessClient()
    except Exception as e:
        print(e, file=sys.stderr)
        sys.exit(1)

    try:
        res = client.search_documents(
            query=search_query,
            correspondent=args.correspondent,
            tag=args.tag,
            document_type=args.type,
            year=args.year,
            page=args.page,
            page_size=args.limit,
            ordering=args.sort,
        )
    except Exception as e:
        print(f"❌ Errore durante la ricerca: {e}", file=sys.stderr)
        sys.exit(1)

    if args.json:
        print(json.dumps(res, indent=2, ensure_ascii=False))
        return

    count = res.get("count", 0)
    results = res.get("results", [])

    print(f"\n📄 Totale documenti trovati: {count} (mostrati {len(results)} su pagina {args.page})\n" + "=" * 80)
    if not results:
        print("Nessun documento corrispondente ai filtri specificati.")
        return

    # Cache metadati per visualizzare i nomi al posto dei soli ID
    corrs = {c["id"]: c["name"] for c in client.list_correspondents()}
    tags_map = {t["id"]: t["name"] for t in client.list_tags()}
    types_map = {dt["id"]: dt["name"] for dt in client.list_document_types()}

    for doc in results:
        doc_id = doc["id"]
        title = doc.get("title", "Senza titolo")
        created = doc.get("created", doc.get("created_date", "Data sconosciuta"))
        c_name = corrs.get(doc.get("correspondent"), "-")
        dt_name = types_map.get(doc.get("document_type"), "-")
        doc_tags = [tags_map.get(tid, str(tid)) for tid in doc.get("tags", [])]
        tags_str = ", ".join(doc_tags) if doc_tags else "-"

        print(f"🔹 [{doc_id}] {title}")
        print(f"   📅 Data: {created} | 🏢 Mittente: {c_name} | 📑 Tipo: {dt_name}")
        print(f"   🏷️  Tag: {tags_str}")
        print(f"   🔗 File originale: {doc.get('original_file_name', '-')}")

        if args.content and doc.get("content"):
            snippet = doc["content"][:300].strip().replace("\n", " ")
            print(f"   📝 OCR Preview: \"{snippet}...\"")
        print("-" * 80)


if __name__ == "__main__":
    main()

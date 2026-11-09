#!/usr/bin/env python3
"""
Recupera i dettagli completi e il testo OCR di un singolo documento Paperless-ngx per ID.
"""

import sys
import json
import argparse
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from paperless.client import PaperlessClient


def main():
    parser = argparse.ArgumentParser(description="Dettagli e OCR di un documento Paperless")
    parser.add_argument("doc_id", type=int, help="ID numerico del documento")
    parser.add_argument("--content", action="store_true", help="Stampa l'intero contenuto OCR estratto")
    parser.add_argument("--json", action="store_true", help="Stampa l'intero JSON restituito dall'API")

    args = parser.parse_args()

    try:
        client = PaperlessClient()
        doc = client.get_document(args.doc_id)
    except Exception as e:
        print(f"❌ Errore recupero documento #{args.doc_id}: {e}", file=sys.stderr)
        sys.exit(1)

    if args.json:
        print(json.dumps(doc, indent=2, ensure_ascii=False))
        return

    # Info di base
    corrs = {c["id"]: c["name"] for c in client.list_correspondents()}
    tags_map = {t["id"]: t["name"] for t in client.list_tags()}
    types_map = {dt["id"]: dt["name"] for dt in client.list_document_types()}

    c_name = corrs.get(doc.get("correspondent"), "-")
    dt_name = types_map.get(doc.get("document_type"), "-")
    doc_tags = [tags_map.get(tid, str(tid)) for tid in doc.get("tags", [])]

    print("\n" + "=" * 80)
    print(f"📄 DOCUMENTO #{doc['id']}: {doc.get('title')}")
    print("=" * 80)
    print(f"🏢 Mittente / Corrispondente: {c_name} (ID: {doc.get('correspondent')})")
    print(f"📑 Tipologia documento:      {dt_name} (ID: {doc.get('document_type')})")
    print(f"📅 Data creazione documento: {doc.get('created')}")
    print(f"🕒 Data aggiunta a Paperless: {doc.get('added')}")
    print(f"🏷️  Tag:                     {', '.join(doc_tags) if doc_tags else 'Nessuno'}")
    print(f"📁 Nome file originale:     {doc.get('original_file_name')}")
    print(f"📦 Nome file archiviato:    {doc.get('archived_file_name')}")
    print(f"📄 Conteggio pagine:         {doc.get('page_count', 'N/D')}")
    print(f"🌐 Mime Type:                {doc.get('mime_type', 'N/D')}")

    notes = doc.get("notes", [])
    if notes:
        print("\n📌 NOTE:")
        for n in notes:
            print(f" - [{n.get('created')}] {n.get('note')}")

    custom_fields = doc.get("custom_fields", [])
    if custom_fields:
        cf_defs = {cf["id"]: cf["name"] for cf in client.request("api/custom_fields/").get("results", [])}
        print("\n🧩 CAMPI PERSONALIZZATI:")
        for cf in custom_fields:
            name = cf_defs.get(cf.get("field"), f"Campo #{cf.get('field')}")
            print(f" - {name}: {cf.get('value')}")

    if args.content:
        print("\n" + "=" * 80)
        print("📝 TESTO COMPLETO OCR:")
        print("=" * 80)
        print(doc.get("content") or "(Nessun testo estratto)")
    else:
        print("\n💡 Suggerimento: usa --content per visualizzare l'intero testo OCR del documento.")


if __name__ == "__main__":
    main()

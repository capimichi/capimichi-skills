#!/usr/bin/env python3
"""
Scarica il file (PDF originale o archiviato) di un documento da Paperless-ngx.
"""

import sys
import argparse
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from paperless.client import PaperlessClient


def main():
    parser = argparse.ArgumentParser(description="Download documento da Paperless-ngx")
    parser.add_argument("doc_id", type=int, help="ID numerico del documento")
    parser.add_argument("-o", "--output", help="Percorso file o cartella di destinazione (default: cartella corrente)")
    parser.add_argument("--original", action="store_true", help="Scarica il file originale invece della versione archiviata/processata")

    args = parser.parse_args()

    try:
        client = PaperlessClient()
        saved_path = client.download_document(
            doc_id=args.doc_id,
            original=args.original,
            output_path=args.output,
        )
        print(f"✅ Documento #{args.doc_id} scaricato con successo in:\n   {saved_path}")
    except Exception as e:
        print(f"❌ Errore download documento #{args.doc_id}: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()

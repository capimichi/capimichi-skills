#!/usr/bin/env python3
"""
Carica un documento (PDF o immagine) su Paperless-ngx.
Include controllo e auto-riparazione preventiva con qpdf per evitare errori di elaborazione.
"""

import sys
import argparse
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from paperless.client import PaperlessClient


def main():
    parser = argparse.ArgumentParser(description="Upload di un documento su Paperless-ngx")
    parser.add_argument("file", help="Percorso del file da caricare (es. fattura.pdf)")
    parser.add_argument("-t", "--title", help="Titolo del documento su Paperless")
    parser.add_argument("-c", "--correspondent", help="Nome o ID del mittente/corrispondente")
    parser.add_argument("--tags", help="Tag separati da virgola (es. 'fattura,luce,casa')")
    parser.add_argument("--type", help="Tipologia di documento (es. 'Fattura')")
    parser.add_argument("--created", help="Data creazione documento nel formato YYYY-MM-DD")
    parser.add_argument("--no-repair", action="store_true", help="Disabilita il controllo/riparazione preventiva qpdf")

    args = parser.parse_args()

    tags_list = [t.strip() for t in args.tags.split(",") if t.strip()] if args.tags else None

    try:
        client = PaperlessClient()
        task_id = client.upload_document(
            file_path=args.file,
            title=args.title,
            correspondent=args.correspondent,
            tags=tags_list,
            document_type=args.type,
            created=args.created,
            auto_repair=not args.no_repair,
        )
        print(f"🚀 Documento inviato con successo a Paperless-ngx!")
        if isinstance(task_id, str):
            print(f"   Task ID ingestione: {task_id}")
        elif isinstance(task_id, dict):
            print(f"   Risposta: {task_id}")
    except Exception as e:
        print(f"❌ Errore durante l'upload del file: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()

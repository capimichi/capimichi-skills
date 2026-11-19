#!/usr/bin/env python3
"""
Paperless-ngx CLI Helper with Click.
"""

import json
import sys
from pathlib import Path

try:
    import click
except ImportError:
    sys.exit("Errore: modulo 'click' non trovato. Installa le dipendenze richieste eseguendo: pip install click")

from client import PaperlessClient


def _get_client():
    try:
        return PaperlessClient()
    except Exception as e:
        sys.exit(f"❌ {e}")


@click.group(help="CLI per la gestione e ricerca documenti su Paperless-ngx.")
def cli():
    pass


@cli.command("search", help="Cerca documenti per testo, mittente, tag, tipo o anno.")
@click.argument("query", required=False, default=None)
@click.option("-c", "--correspondent", help="Nome o ID del mittente/corrispondente (es. AASS).")
@click.option("-t", "--tag", multiple=True, help="Nome o ID del tag (ripetibile: -t bolletta -t luce).")
@click.option("--type", "doc_type", help="Tipo di documento (es. Fattura, Ricevuta, Avviso).")
@click.option("-y", "--year", help="Anno di creazione (es. 2026).")
@click.option("-n", "--limit", type=int, default=15, help="Numero massimo di risultati (default: 15).")
@click.option("--page", type=int, default=1, help="Numero pagina (default: 1).")
@click.option("--sort", default="-created", help="Ordinamento (default: -created).")
@click.option("--content", is_flag=True, help="Mostra uno snippet del contenuto OCR estratto.")
@click.option("--json", "as_json", is_flag=True, help="Output in formato JSON.")
def cmd_search(query, correspondent, tag, doc_type, year, limit, page, sort, content, as_json):
    client = _get_client()
    tags_list = list(tag) if tag else None

    try:
        res = client.search_documents(
            query=query,
            correspondent=correspondent,
            tag=tags_list,
            document_type=doc_type,
            year=year,
            page=page,
            page_size=limit,
            ordering=sort,
        )
    except Exception as e:
        click.echo(f"❌ Errore durante la ricerca: {e}", err=True)
        sys.exit(1)

    if as_json:
        click.echo(json.dumps(res, indent=2, ensure_ascii=False))
        return

    count = res.get("count", 0)
    results = res.get("results", [])

    click.echo(f"\n📄 Totale documenti trovati: {count} (mostrati {len(results)} su pagina {page})\n" + "=" * 80)
    if not results:
        click.echo("Nessun documento corrispondente ai filtri specificati.")
        return

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

        click.echo(f"🔹 [{doc_id}] {title}")
        click.echo(f"   📅 Data: {created} | 🏢 Mittente: {c_name} | 📑 Tipo: {dt_name}")
        click.echo(f"   🏷️  Tag: {tags_str}")
        click.echo(f"   🔗 File originale: {doc.get('original_file_name', '-')}")

        if content and doc.get("content"):
            snippet = doc["content"][:300].strip().replace("\n", " ")
            click.echo(f"   📝 OCR Preview: \"{snippet}...\"")
        click.echo("-" * 80)


@cli.command("get", help="Mostra i dettagli completi e il testo OCR di un documento per ID.")
@click.argument("doc_id", type=int)
@click.option("--no-content", is_flag=True, help="Non mostrare il testo completo OCR.")
@click.option("--json", "as_json", is_flag=True, help="Output in formato JSON.")
def cmd_get(doc_id, no_content, as_json):
    client = _get_client()
    try:
        doc = client.get_document(doc_id, include_content=not no_content)
    except Exception as e:
        click.echo(f"❌ Errore durante il recupero del documento: {e}", err=True)
        sys.exit(1)

    if as_json:
        click.echo(json.dumps(doc, indent=2, ensure_ascii=False))
        return

    corrs = {c["id"]: c["name"] for c in client.list_correspondents()}
    tags_map = {t["id"]: t["name"] for t in client.list_tags()}
    types_map = {dt["id"]: dt["name"] for dt in client.list_document_types()}

    title = doc.get("title", "Senza titolo")
    created = doc.get("created", doc.get("created_date", "-"))
    c_name = corrs.get(doc.get("correspondent"), "-")
    dt_name = types_map.get(doc.get("document_type"), "-")
    doc_tags = [tags_map.get(tid, str(tid)) for tid in doc.get("tags", [])]
    tags_str = ", ".join(doc_tags) if doc_tags else "-"

    click.echo("\n" + "=" * 80)
    click.echo(f"📄 Documento #{doc_id}: {title}")
    click.echo("=" * 80)
    click.echo(f"📅 Data Creazione:   {created}")
    click.echo(f"🏢 Mittente:         {c_name}")
    click.echo(f"📑 Tipo Documento:   {dt_name}")
    click.echo(f"🏷️  Tag:              {tags_str}")
    click.echo(f"🔗 File Originale:   {doc.get('original_file_name', '-')}")
    click.echo(f"📥 Archiviato:       {doc.get('archive_filename', '-')}")

    if not no_content and doc.get("content"):
        click.echo("\n📝 Testo OCR Estratto:")
        click.echo("-" * 80)
        click.echo(doc["content"].strip())
        click.echo("-" * 80)


@cli.command("download", help="Scarica il file PDF di un documento.")
@click.argument("doc_id", type=int)
@click.option("-o", "--output", help="Percorso o nome file locale di destinazione.")
@click.option("--original", is_flag=True, help="Scarica il file grezzo originale anziché la versione PDF archiviata.")
def cmd_download(doc_id, output, original):
    client = _get_client()
    try:
        saved_path = client.download_document(doc_id, output_path=output, original=original)
        click.echo(f"✅ Documento #{doc_id} scaricato con successo in:\n   {saved_path}")
    except Exception as e:
        click.echo(f"❌ Errore durante il download: {e}", err=True)
        sys.exit(1)


@cli.command("upload", help="Carica un nuovo documento su Paperless.")
@click.argument("file_path", type=click.Path(exists=True))
@click.option("-t", "--title", help="Titolo personalizzato (default: nome del file).")
@click.option("-c", "--correspondent", help="Nome o ID del mittente/corrispondente.")
@click.option("--type", "doc_type", help="Tipo di documento (es. Fattura, Ricevuta).")
@click.option("--tag", multiple=True, help="Tag da assegnare (ripetibile: --tag bolletta --tag casa).")
@click.option("--created", help="Data di creazione nel formato YYYY-MM-DD.")
def cmd_upload(file_path, title, correspondent, doc_type, tag, created):
    client = _get_client()
    tags_list = list(tag) if tag else None
    click.echo(f"📤 Caricamento in corso: {file_path}...")
    try:
        task_id = client.upload_document(
            file_path=file_path,
            title=title,
            correspondent=correspondent,
            document_type=doc_type,
            tags=tags_list,
            created=created,
        )
        click.echo(f"✅ Documento inviato a Paperless con successo! (Task ID: {task_id})")
    except Exception as e:
        click.echo(f"❌ Errore durante il caricamento: {e}", err=True)
        sys.exit(1)


@cli.command("metadata", help="Elenca metadati (corrispondenti, tag, tipi documento).")
@click.option("--type", "meta_type", type=click.Choice(["all", "correspondents", "tags", "types"]), default="all", help="Tipo di metadati da visualizzare.")
@click.option("--json", "as_json", is_flag=True, help="Output in formato JSON.")
def cmd_metadata(meta_type, as_json):
    client = _get_client()
    data = {}
    if meta_type in ("all", "correspondents"):
        data["correspondents"] = client.list_correspondents()
    if meta_type in ("all", "tags"):
        data["tags"] = client.list_tags()
    if meta_type in ("all", "types"):
        data["document_types"] = client.list_document_types()

    if as_json:
        click.echo(json.dumps(data, indent=2, ensure_ascii=False))
        return

    if "correspondents" in data:
        click.echo(f"\n🏢 Mittenti / Corrispondenti ({len(data['correspondents'])}):")
        for c in data["correspondents"]:
            click.echo(f"  • [{c['id']}] {c['name']}")

    if "tags" in data:
        click.echo(f"\n🏷️  Tag ({len(data['tags'])}):")
        for t in data["tags"]:
            click.echo(f"  • [{t['id']}] {t['name']}")

    if "document_types" in data:
        click.echo(f"\n📑 Tipi Documento ({len(data['document_types'])}):")
        for dt in data["document_types"]:
            click.echo(f"  • [{dt['id']}] {dt['name']}")


if __name__ == "__main__":
    try:
        cli()
    except KeyboardInterrupt:
        sys.exit(130)

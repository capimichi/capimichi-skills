#!/usr/bin/env python3
"""
WhatsApp Backup & Archival Utility for rclone / Cloud Storage.

Processes WhatsApp chat exports (.zip or directory from iOS AirDrop),
categorizes contents into:
  - Chat/
      ├── Archives/               # Raw exported txt files (e.g. chat_2026-10-22.txt)
      └── chat.txt                # Unified, deduplicated, chronologically ordered chat
  - Media/
      ├── Foto/                   # Images and stickers (.jpg, .png, .webp, etc.)
      ├── Video/                  # Videos and GIFs (.mp4, .mov, etc.)
      └── Audio/                  # Voice notes and audio (.opus, .m4a, .mp3, etc.)
  - Docs/                         # Documents (PDF, Word, Excel, VCF, etc.)
and uploads incrementally to cloud storage (default: onedrive-michele:Backup/WhatsApp/<ChatName>).
"""

import os
import sys
import re
import shutil
import zipfile
import argparse
import subprocess
import tempfile
import unicodedata
from datetime import datetime
from pathlib import Path

DEFAULT_REMOTE_BASE = "onedrive-michele:Backup/WhatsApp"

# Extensions mapping
IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".heic", ".webp", ".gif", ".tiff", ".bmp"}
VIDEO_EXTS = {".mp4", ".mov", ".3gp", ".avi", ".mkv", ".m4v"}
AUDIO_EXTS = {".opus", ".m4a", ".aac", ".mp3", ".wav", ".ogg", ".caf", ".amr"}
DOC_EXTS = {
    ".pdf", ".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx",
    ".csv", ".txt", ".vcf", ".zip", ".rar", ".7z", ".tar", ".gz"
}

# Regex to match WhatsApp message headers
# Supports iOS: [15/02/22, 08:24:58] Sender: ...
# Supports Android: 15/02/22, 08:24 - Sender: ...
MSG_HEADER_REGEX = re.compile(
    r'^[\u200e\u200f\s]*\[?(\d{1,2}/\d{1,2}/\d{2,4}),?\s+(\d{1,2}:\d{2}(?::\d{2})?(?:\s+[AP]M)?)\]?(?:\s+-\s+|\s+)(.*)$',
    re.IGNORECASE
)


def sanitize_folder_name(name: str) -> str:
    """Sanitize name for use as a folder in cloud storage."""
    cleaned = unicodedata.normalize('NFC', name)
    cleaned = re.sub(r"^(Chat\s+WhatsApp\s+con|WhatsApp\s+Chat\s+[-–—]|WhatsApp\s+Chat\s+with)\s+", "", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"\.zip$", "", cleaned, flags=re.IGNORECASE)
    cleaned = cleaned.replace(" _ ", " - ")
    cleaned = re.sub(r'[/\\:*?"<>|]', " - ", cleaned)
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    return cleaned or "Chat Senza Nome"


def detect_chat_name(source_path: Path, provided_name: str | None) -> str:
    if provided_name:
        return sanitize_folder_name(provided_name)
    return sanitize_folder_name(source_path.stem)


def get_file_category(filename: str) -> tuple[str, str]:
    """Returns (category, subfolder). Categories: 'Chat', 'Media', 'Docs'."""
    ext = Path(filename).suffix.lower()
    base = Path(filename).name.lower()

    if base in ("_chat.txt", "chat.txt") or (ext == ".txt" and "chat" in base):
        return ("Chat", "")

    if ext in IMAGE_EXTS:
        return ("Media", "Foto")
    elif ext in VIDEO_EXTS:
        return ("Media", "Video")
    elif ext in AUDIO_EXTS:
        return ("Media", "Audio")
    elif ext in DOC_EXTS:
        return ("Docs", "")
    else:
        return ("Docs", "")


def parse_timestamp(d_str: str, t_str: str) -> datetime:
    """Parse date and time string from WhatsApp header."""
    d_parts = [int(p) for p in re.split(r'[/.-]', d_str)]
    day, month, year = d_parts[0], d_parts[1], d_parts[2]
    if year < 100:
        year += 2000

    # Clean time (remove AM/PM if present)
    is_pm = "PM" in t_str.upper()
    is_am = "AM" in t_str.upper()
    t_clean = re.sub(r'[^\d:]', '', t_str)
    t_parts = [int(p) for p in t_clean.split(':')]
    hour = t_parts[0]
    minute = t_parts[1]
    second = t_parts[2] if len(t_parts) > 2 else 0

    if is_pm and hour < 12:
        hour += 12
    elif is_am and hour == 12:
        hour = 0

    return datetime(year, month, day, hour, minute, second)


def parse_chat_messages(filepath: Path) -> list[dict]:
    """Parse a single WhatsApp chat export txt file into structured messages."""
    messages = []
    current_msg = None

    try:
        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            for line in f:
                clean_line = line.lstrip("\u200e\u200f")
                m = MSG_HEADER_REGEX.match(clean_line)
                if m:
                    if current_msg:
                        messages.append(current_msg)
                    d_str, t_str, rest = m.groups()
                    try:
                        dt = parse_timestamp(d_str, t_str)
                    except Exception:
                        dt = datetime.min
                    current_msg = {
                        "dt": dt,
                        "header": f"[{d_str}, {t_str}]",
                        "first_line": rest.rstrip("\r\n"),
                        "extra_lines": []
                    }
                else:
                    if current_msg:
                        current_msg["extra_lines"].append(line.rstrip("\r\n"))
            if current_msg:
                messages.append(current_msg)
    except Exception as e:
        print(f"⚠️ Errore lettura file {filepath.name}: {e}", file=sys.stderr)

    return messages


def build_unified_chat(archives_dir: Path, output_file: Path) -> int:
    """Read all txt files in Archives/, deduplicate messages, sort chronologically, write output_file."""
    all_archive_files = sorted([f for f in archives_dir.glob("*.txt") if f.is_file()])
    if not all_archive_files:
        return 0

    seen_keys = set()
    unified_messages = []

    for af in all_archive_files:
        msgs = parse_chat_messages(af)
        for m in msgs:
            # Deduplication key: timestamp + first line (sender and text)
            full_text = "\n".join([m["first_line"]] + m["extra_lines"]).strip()
            # Remove invisible marks for key matching
            key_body = re.sub(r'[\u200e\u200f\s]+', ' ', full_text).strip()
            dedup_key = (m["dt"], key_body)

            if dedup_key not in seen_keys:
                seen_keys.add(dedup_key)
                unified_messages.append(m)

    # Sort chronologically
    unified_messages.sort(key=lambda m: m["dt"])

    # Write unified chat.txt
    with open(output_file, "w", encoding="utf-8") as out:
        for m in unified_messages:
            out.write(f"{m['header']} {m['first_line']}\n")
            for el in m["extra_lines"]:
                out.write(f"{el}\n")

    return len(unified_messages)


def organize_and_upload(
    source: Path,
    chat_name: str | None = None,
    remote_base: str = DEFAULT_REMOTE_BASE,
    dry_run: bool = False,
    keep_staging: bool = False,
    separate_media_subfolders: bool = True
) -> int:
    source = Path(source).expanduser().resolve()
    if not source.exists():
        print(f"❌ Errore: Sorgente non trovata: {source}", file=sys.stderr)
        return 1

    final_chat_name = detect_chat_name(source, chat_name)
    destination_remote = f"{remote_base}/{final_chat_name}"

    print(f"\n========================================================")
    print(f"📦 WhatsApp Backup Organizer")
    print(f"========================================================")
    print(f"• Sorgente:     {source}")
    print(f"• Nome Chat:    {final_chat_name}")
    print(f"• Destinazione: {destination_remote}")
    if dry_run:
        print(f"• Modalità:     DRY RUN (nessuna modifica effettiva)")
    print(f"========================================================\n")

    temp_dir = tempfile.mkdtemp(prefix="wa_backup_")
    staging_path = Path(temp_dir) / final_chat_name

    try:
        extracted_files_dir = Path(temp_dir) / "extracted"
        extracted_files_dir.mkdir(parents=True, exist_ok=True)

        if source.is_file() and zipfile.is_zipfile(source):
            print(f"📂 Estrazione archivio zip...")
            with zipfile.ZipFile(source, "r") as zf:
                zf.extractall(extracted_files_dir)
        elif source.is_dir():
            print(f"📂 Scansione cartella sorgente...")
            for item in source.rglob("*"):
                if item.is_file():
                    rel = item.relative_to(source)
                    dest_f = extracted_files_dir / rel
                    dest_f.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(item, dest_f)
        else:
            print(f"❌ Errore: la sorgente deve essere un file .zip o una directory.", file=sys.stderr)
            return 1

        all_files = [f for f in extracted_files_dir.rglob("*") if f.is_file()]
        chat_log = next((f for f in all_files if f.name.lower() in ("_chat.txt", "chat.txt")), None)

        export_date = datetime.now().strftime("%Y-%m-%d")
        if chat_log:
            try:
                export_date = datetime.fromtimestamp(chat_log.stat().st_mtime).strftime("%Y-%m-%d")
            except Exception:
                pass

        # Prepare staging Chat/Archives
        chat_staging_dir = staging_path / "Chat"
        archives_staging_dir = chat_staging_dir / "Archives"
        archives_staging_dir.mkdir(parents=True, exist_ok=True)

        # Download existing Archives/ from destination (if exists) to perform global merge
        existing_archives_temp = Path(temp_dir) / "remote_archives"
        existing_archives_temp.mkdir(parents=True, exist_ok=True)
        pull_cmd = [
            "rclone", "copy",
            f"{destination_remote}/Chat/Archives",
            str(existing_archives_temp)
        ]
        # Run silently (it's ok if remote doesn't exist yet)
        subprocess.run(pull_cmd, capture_output=True)

        # Copy existing archives into staging archives dir
        for existing_file in existing_archives_temp.glob("*.txt"):
            shutil.copy2(existing_file, archives_staging_dir / existing_file.name)

        # Store incoming raw chat into Archives/
        if chat_log:
            raw_archive_name = f"chat_{export_date}.txt"
            target_archive_file = archives_staging_dir / raw_archive_name
            # If a file with the same date exists, append timestamp
            if target_archive_file.exists():
                time_suffix = datetime.now().strftime("_%H%M%S")
                raw_archive_name = f"chat_{export_date}{time_suffix}.txt"
                target_archive_file = archives_staging_dir / raw_archive_name
            shutil.copy2(chat_log, target_archive_file)
            print(f"📄 Salvato archivio grezzo: Chat/Archives/{raw_archive_name}")

        # Build unified Chat/chat.txt
        unified_file = chat_staging_dir / "chat.txt"
        total_unique_msgs = build_unified_chat(archives_staging_dir, unified_file)
        num_archive_files = len(list(archives_staging_dir.glob("*.txt")))
        print(f"🔄 Generato Chat/chat.txt unificato: {total_unique_msgs} messaggi deduplicati (da {num_archive_files} file archivio)")

        # Categorize Media and Docs
        stats = {"Chat/Archives": num_archive_files, "Media/Foto": 0, "Media/Video": 0, "Media/Audio": 0, "Docs": 0}
        total_bytes = 0

        for file_path in all_files:
            cat, sub = get_file_category(file_path.name)
            total_bytes += file_path.stat().st_size

            if cat == "Chat":
                continue  # already handled via Archives & unified chat.txt
            elif cat == "Media":
                if separate_media_subfolders and sub:
                    target_dir = staging_path / "Media" / sub
                    stats[f"Media/{sub}"] += 1
                else:
                    target_dir = staging_path / "Media"
                    stats["Media"] = stats.get("Media", 0) + 1
                target_dir.mkdir(parents=True, exist_ok=True)
                shutil.copy2(file_path, target_dir / file_path.name)
            elif cat == "Docs":
                target_dir = staging_path / "Docs"
                target_dir.mkdir(parents=True, exist_ok=True)
                shutil.copy2(file_path, target_dir / file_path.name)
                stats["Docs"] += 1

        print("\n📊 Statistiche contenuti:")
        print(f"   • Chat/chat.txt  : 1 file unificato ({total_unique_msgs} messaggi)")
        for k, v in stats.items():
            if v > 0:
                print(f"   • {k:15}: {v} file")
        print(f"   • Dimensione tot: {total_bytes / (1024 * 1024):.2f} MB\n")

        # Step 3: Run rclone copy
        print(f"🚀 Caricamento su {destination_remote} ...")
        rclone_cmd = [
            "rclone", "copy",
            str(staging_path),
            destination_remote,
            "-v",
            "--stats", "2s"
        ]
        if dry_run:
            rclone_cmd.append("--dry-run")

        result = subprocess.run(rclone_cmd)
        if result.returncode != 0:
            print(f"❌ Errore durante il trasferimento rclone (exit code {result.returncode})", file=sys.stderr)
            return result.returncode

        print("\n✅ Backup completato con successo!")
        print(f"   Destinazione: {destination_remote}")
        return 0

    finally:
        if keep_staging:
            print(f"ℹ️ Cartella temporanea preservata in: {temp_dir}")
        else:
            shutil.rmtree(temp_dir, ignore_errors=True)


def main():
    parser = argparse.ArgumentParser(
        description="Backup e organizzazione incrementale di chat WhatsApp su Cloud tramite rclone."
    )
    parser.add_argument("source", help="Percorso del file .zip esportato o cartella della chat")
    parser.add_argument("-n", "--name", help="Nome personalizzato per la cartella della chat (default: rilevato dal file)")
    parser.add_argument(
        "-r", "--remote",
        default=DEFAULT_REMOTE_BASE,
        help=f"Destinazione remota rclone base (default: {DEFAULT_REMOTE_BASE})"
    )
    parser.add_argument("--dry-run", action="store_true", help="Simula l'operazione senza trasferire file")
    parser.add_argument("--keep-staging", action="store_true", help="Mantieni i file temporanei locali per verifica")
    parser.add_argument(
        "--no-media-subfolders",
        action="store_true",
        help="Non suddividere Media in Foto/Video/Audio, inserisci tutto in Media/"
    )

    args = parser.parse_args()
    ret = organize_and_upload(
        source=args.source,
        chat_name=args.name,
        remote_base=args.remote,
        dry_run=args.dry_run,
        keep_staging=args.keep_staging,
        separate_media_subfolders=not args.no_media_subfolders
    )
    sys.exit(ret)


if __name__ == "__main__":
    main()

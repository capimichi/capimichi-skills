#!/usr/bin/env python3
"""
Utility CLI per sincronizzare il foglio REGALI NOEMI con Google Drive via rclone.
"""

import sys
import subprocess
from pathlib import Path

REMOTE_PATH = "googledrive-capimichi:PERSONALE/REGALI NOEMI"
LOCAL_TMP = Path("/tmp/REGALI_NOEMI.xlsx")

def download_sheet():
    print(f"📥 Scaricamento in corso da {REMOTE_PATH}...")
    cmd = ["rclone", "copyto", REMOTE_PATH, str(LOCAL_TMP)]
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode == 0:
        print(f"✅ File salvato temporaneamente in {LOCAL_TMP}")
    else:
        print(f"❌ Errore durante il download: {res.stderr}")
        sys.exit(1)

def upload_sheet():
    if not LOCAL_TMP.exists():
        print(f"❌ Errore: File {LOCAL_TMP} non trovato.")
        sys.exit(1)
    print(f"📤 Caricamento e sovrascrittura in-place su {REMOTE_PATH}...")
    cmd = [
        "rclone", "copyto", str(LOCAL_TMP), REMOTE_PATH,
        "--drive-import-formats", "xlsx",
        "--drive-allow-import-name-change",
        "-v"
    ]
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode == 0:
        print("✅ Aggiornamento completato con successo (ID e link preservati)!")
    else:
        print(f"❌ Errore durante il caricamento: {res.stderr}")
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) < 2 or sys.argv[1] not in ["pull", "push"]:
        print("Uso: python sync_sheet.py [pull|push]")
        sys.exit(1)
    
    action = sys.argv[1]
    if action == "pull":
        download_sheet()
    elif action == "push":
        upload_sheet()

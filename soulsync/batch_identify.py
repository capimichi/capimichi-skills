import os
import sys
import io
import json

sys.path.insert(0, '/app')

# Redirect stdout/stderr to suppress startup logs
old_stdout = sys.stdout
old_stderr = sys.stderr
sys.stdout = io.StringIO()
sys.stderr = io.StringIO()

try:
    import web_server
finally:
    sys.stdout = old_stdout
    sys.stderr = old_stderr

import logging
logging.getLogger().setLevel(logging.ERROR)
logging.root.setLevel(logging.ERROR)
for logger_name in list(logging.root.manager.loggerDict.keys()):
    logging.getLogger(logger_name).setLevel(logging.ERROR)

from core.auto_import_worker import AutoImportWorker, FolderCandidate, _read_file_tags, _compute_folder_hash
from core.imports.staging import AUDIO_EXTENSIONS

db = web_server.get_database()
config = web_server.config_manager

worker = AutoImportWorker(
    database=db,
    staging_path=web_server._ai_staging,
    transfer_path=web_server._ai_transfer,
    config_manager=config
)

def identify_file(file_path):
    try:
        tags = _read_file_tags(file_path)
    except Exception:
        tags = {}
        
    single_hash = _compute_folder_hash([file_path])
    single_candidate = FolderCandidate(
        path=os.path.dirname(file_path),
        name=os.path.basename(os.path.dirname(file_path)),
        audio_files=[file_path],
        folder_hash=single_hash
    )
    
    ident = None
    method = None
    for m_name, fn in [
        ('Exact IDs', worker._identify_from_exact_ids),
        ('Tags', worker._identify_from_tags),
        ('Folder Name', worker._identify_from_folder_name),
        ('AcoustID', worker._identify_from_acoustid)
    ]:
        try:
            res = fn(single_candidate)
            if res:
                ident = res
                method = m_name
                break
        except Exception:
            pass
            
    if not ident:
        return {
            "identified": False,
            "title": tags.get('title'),
            "artist": tags.get('artist'),
            "album": tags.get('album')
        }
        
    return {
        "identified": True,
        "method": method,
        "album_name": ident.get('album_name'),
        "artist_name": ident.get('artist_name'),
        "album_id": ident.get('album_id'),
        "source": ident.get('source'),
        "title": tags.get('title'),
        "artist": tags.get('artist'),
        "album": tags.get('album')
    }

def main():
    paths = ["/app/Staging/883", "/app/Staging/Max Pezzali -883"]
    files = []
    for path in paths:
        if not os.path.exists(path):
            continue
        for root, dirs, f_list in os.walk(path):
            for f in f_list:
                if os.path.splitext(f)[1].lower() in AUDIO_EXTENSIONS:
                    files.append(os.path.join(root, f))
                    
    results = []
    total = len(files)
    for idx, f in enumerate(files):
        sys.stderr.write(f"Processing {idx+1}/{total}: {os.path.basename(f)}\n")
        sys.stderr.flush()
        res = identify_file(f)
        res["file_path"] = f
        res["file_name"] = os.path.basename(f)
        results.append(res)
        
    print(json.dumps(results, indent=2))

if __name__ == "__main__":
    main()

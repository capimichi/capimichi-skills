import sys
import os
import io
import json

# Parse arguments dynamically
opts = [a for a in sys.argv[1:] if a.startswith('--')]
args = [a for a in sys.argv[1:] if not a.startswith('--')]

# We need at least the directory path
if len(args) < 1:
    print("Usage: docker exec -it soulsync-webui python3 /app/cli_import.py <directory_path_in_container> [--prefetch <size>] [--auto] [--min-confidence <percent>] [--no-album-parenthesis]")
    print("Example: docker exec -it soulsync-webui python3 /app/cli_import.py /app/Staging/pau/J-Ax\\ &\\ Friends --prefetch 10 --auto --no-album-parenthesis")
    sys.exit(1)

target_dir = args[0]
if not os.path.isdir(target_dir):
    print(f"Error: {target_dir} is not a directory.")
    sys.exit(1)

# Default values
prefetch_val = 1
auto_mode = '--auto' in sys.argv
no_album_parenthesis = ('--no-album-parenthesis' in sys.argv or '--no-album-parentesis' in sys.argv)
min_conf_val = 0.90 # 90% default

# Support both '--prefetch 10' and '--prefetch=10'
if '--prefetch' in sys.argv:
    idx = sys.argv.index('--prefetch')
    if idx + 1 < len(sys.argv):
        try:
            prefetch_val = int(sys.argv[idx + 1])
        except ValueError:
            print("Warning: --prefetch value must be an integer. Using default (1).")

for arg in sys.argv[1:]:
    if arg.startswith('--prefetch='):
        try:
            prefetch_val = int(arg.split('=', 1)[1])
        except ValueError:
            print("Warning: --prefetch value must be an integer. Using default (1).")

# Support both '--min-confidence 85' and '--min-confidence=85'
if '--min-confidence' in sys.argv:
    idx = sys.argv.index('--min-confidence')
    if idx + 1 < len(sys.argv):
        try:
            min_conf_val = float(sys.argv[idx + 1]) / 100.0
        except ValueError:
            print("Warning: --min-confidence value must be a number (e.g. 75). Using default (90).")

for arg in sys.argv[1:]:
    if arg.startswith('--min-confidence='):
        try:
            min_conf_val = float(arg.split('=', 1)[1]) / 100.0
        except ValueError:
            print("Warning: --min-confidence value must be a number (e.g. 75). Using default (90).")

# Set python path
sys.path.insert(0, '/app')

print("Initializing SoulSync context, please wait...")

# Temporarily redirect stdout and stderr to suppress startup logs
old_stdout = sys.stdout
old_stderr = sys.stderr
sys.stdout = io.StringIO()
sys.stderr = io.StringIO()

try:
    # Import web_server (which initializes config, database, and workers)
    import web_server
finally:
    # Restore stdout and stderr
    sys.stdout = old_stdout
    sys.stderr = old_stderr

# Suppress background logging to keep the CLI interactive interface clean
import logging
logging.getLogger().setLevel(logging.WARNING)
logging.root.setLevel(logging.WARNING)
for logger_name in list(logging.root.manager.loggerDict):
    logging.getLogger(logger_name).setLevel(logging.WARNING)

from core.auto_import_worker import AutoImportWorker, FolderCandidate, _read_file_tags, _compute_folder_hash

# Get database and config
db = web_server.get_database()
config = web_server.config_manager

# Instantiate worker
worker = AutoImportWorker(
    database=db,
    staging_path=web_server._ai_staging,
    transfer_path=web_server._ai_transfer,
    config_manager=config
)

def get_field(obj, field, default=None):
    if hasattr(obj, field):
        return getattr(obj, field)
    if isinstance(obj, dict):
        return obj.get(field, default)
    try:
        return obj[field]
    except (KeyError, TypeError):
        return default

def get_source_url(source, album_id):
    if source == 'spotify':
        return f"https://open.spotify.com/album/{album_id}"
    elif source == 'deezer':
        return f"https://www.deezer.com/album/{album_id}"
    elif source == 'itunes':
        return f"https://music.apple.com/us/album/{album_id}"
    return f"Source ID: {album_id} ({source})"

# Build FolderCandidate manually
from core.imports.staging import AUDIO_EXTENSIONS
audio_files = []
for root, dirs, files in os.walk(target_dir):
    for f in files:
        if os.path.splitext(f)[1].lower() in AUDIO_EXTENSIONS:
            audio_files.append(os.path.join(root, f))

if not audio_files:
    print("No audio files found in directory.")
    sys.exit(0)

# If prefetch_val is 0 or less, we process all files in a single batch
if prefetch_val <= 0:
    prefetch_val = len(audio_files)

print(f"Found {len(audio_files)} audio files.")
folder_hash = _compute_folder_hash(audio_files)
candidate = FolderCandidate(
    path=target_dir,
    name=os.path.basename(target_dir),
    audio_files=audio_files,
    folder_hash=folder_hash
)

# Read file tags early so we can show them
file_tags = {}
for f in candidate.audio_files:
    try:
        file_tags[f] = _read_file_tags(f)
    except Exception:
        file_tags[f] = {}

# Print physical paths and tags immediately so the user always has context
print("\n============================================================")
print("Percorso file fisici:")
for f in candidate.audio_files[:5]:
    print(f"  - {f}")
if len(candidate.audio_files) > 5:
    print(f"  - ... and {len(candidate.audio_files) - 5} more files")

print("\nTag estratti dai file:")
for f in candidate.audio_files[:5]:
    tags = file_tags[f]
    print(f"  File: {os.path.basename(f)}")
    print(f"    - Titolo:  {tags.get('title')}")
    print(f"    - Artista: {tags.get('artist')}")
    print(f"    - Album:   {tags.get('album')}")
if len(candidate.audio_files) > 5:
    print("  - ...")
print("============================================================\n")

# Split candidate audio files into batches using the prefetch flag value
chunks = [audio_files[i:i + prefetch_val] for i in range(0, len(audio_files), prefetch_val)]
print(f"\nDivided {len(audio_files)} files into {len(chunks)} batches of size {prefetch_val} (via --prefetch).")
if auto_mode:
    print(f"Auto mode active. Skipping matches below {min_conf_val * 100:.1f}% confidence.")
if no_album_parenthesis:
    print("Parentheses stripping active for album searches.")

for chunk_idx, chunk in enumerate(chunks):
    print(f"\n============================================================")
    print(f"BATCH {chunk_idx + 1}/{len(chunks)} ({len(chunk)} files)")
    print(f"============================================================")

    selected_matches = []

    for f_idx, f in enumerate(chunk):
        print(f"\n------------------------------------------------------------")
        print(f"FILE {f_idx + 1}/{len(chunk)}: '{f}'")
        tags = file_tags[f]
        print(f"  Tag estratti:")
        print(f"    - Titolo:  {tags.get('title')}")
        print(f"    - Artista: {tags.get('artist')}")
        print(f"    - Album:   {tags.get('album')}")
        print(f"------------------------------------------------------------")

        # Build default query string from tags
        f_artist = tags.get('artist') or ''
        if isinstance(f_artist, list):
            f_artist = f_artist[0] if f_artist else ''
        f_album = tags.get('album') or ''
        if isinstance(f_album, list):
            f_album = f_album[0] if f_album else ''
            
        # Clean artist name for query by replacing separators (like ;, /, \) with spaces
        clean_artist = f_artist.replace(';', ' ').replace('/', ' ').replace('\\', ' ')
        clean_artist = " ".join(clean_artist.split())
        
        # Clean album name if option is active
        clean_album = f_album
        if no_album_parenthesis:
            import re
            clean_album = re.sub(r'[\(\[\{].*?[\)\]\}]', '', f_album)
            clean_album = " ".join(clean_album.split()).strip()
        
        default_query = f"{clean_artist} {clean_album}".strip()

        # Attempt to identify this file by searching the metadata source directly
        ident = None
        method = "Search"
        auto_album_ratio = 0.0
        
        if clean_album and clean_artist:
            print(f"Identifying file via metadata search (query: '{default_query}')...")
            from core.metadata_service import get_primary_source, get_client_for_source
            source = get_primary_source()
            client = get_client_for_source(source)
            if client and hasattr(client, 'search_albums'):
                try:
                    # Search using artist and album
                    results = client.search_albums(default_query, limit=5)
                    if results:
                        # Sort results by name similarity to clean_album and track count descending
                        from difflib import SequenceMatcher
                        def rank_album(album_obj):
                            name = get_field(album_obj, 'name', '') or ''
                            ratio = SequenceMatcher(None, name.lower(), clean_album.lower()).ratio()
                            tracks_cnt = get_field(album_obj, 'total_tracks') or get_field(album_obj, 'track_count') or 0
                            # Round ratio to 1 decimal place to group similar matches, then sort by track count
                            return (round(ratio, 1), tracks_cnt)
                        
                        sorted_results = sorted(results, key=rank_album, reverse=True)
                        best_match = sorted_results[0]
                        
                        best_name = get_field(best_match, 'name', '') or ''
                        auto_album_ratio = SequenceMatcher(None, best_name.lower(), clean_album.lower()).ratio()
                        
                        artists_raw = get_field(best_match, 'artists')
                        artists_list = []
                        if artists_raw:
                            for a in artists_raw:
                                if isinstance(a, str):
                                    artists_list.append(a)
                                elif isinstance(a, dict):
                                    artists_list.append(a.get('name') or '')
                                elif hasattr(a, 'name'):
                                    artists_list.append(a.name)
                        artist = ", ".join(artists_list) if artists_list else (get_field(best_match, 'artist') or 'Unknown')
                        
                        images = get_field(best_match, 'images')
                        image_url = get_field(best_match, 'image_url') or ''
                        if not image_url and images:
                            image_url = images[0].get('url') if isinstance(images[0], dict) else getattr(images[0], 'url', '')
                            
                        ident = {
                            'album_id': get_field(best_match, 'id'),
                            'album_name': get_field(best_match, 'name'),
                            'artist_name': artist,
                            'artist_id': '',
                            'source': source,
                            'image_url': image_url,
                            'release_date': get_field(best_match, 'release_date', '')
                        }
                except Exception as e:
                    print("Error during auto search identification:", e)

        if ident:
            source = ident.get('source')
            album_id = ident.get('album_id')
            
            # Fetch track count for the matched album
            total_tracks = None
            try:
                from core.metadata_service import get_client_for_source
                client = get_client_for_source(source)
                album_data = None
                if hasattr(client, 'get_album'):
                    album_data = client.get_album(album_id)
                elif hasattr(client, 'get_album_metadata'):
                    album_data = client.get_album_metadata(str(album_id), include_tracks=False)
                
                if album_data:
                    total_tracks = get_field(album_data, 'total_tracks') or get_field(album_data, 'track_count')
                    if not total_tracks and hasattr(album_data, 'tracks'):
                        raw = getattr(album_data, 'tracks')
                        total_tracks = len(getattr(raw, 'data')) if hasattr(raw, 'data') else len(raw)
            except Exception:
                pass
            
            tracks_str = f" ({total_tracks} tracce)" if total_tracks is not None else ""
            
            # In auto_mode, check if the best match satisfies the confidence threshold
            if auto_mode:
                if auto_album_ratio >= min_conf_val:
                    print(f"[Auto-Mode] Automatically selected album: '{ident.get('album_name')}'{tracks_str} (Simmetria: {auto_album_ratio:.1%})")
                else:
                    print(f"[Auto-Mode] Album match too weak ({auto_album_ratio:.1%} < {min_conf_val * 100:.1%}). Skipping file.")
                    continue
            else:
                print("============================================================")
                print(f"Tag del risultato di ricerca trovato ({source} - via {method}):")
                print(f"  - Artista: {ident.get('artist_name')}")
                print(f"  - Album:   {ident.get('album_name')}{tracks_str}")
                print(f"  - ID:      {album_id}")
                print(f"  - Link:    {get_source_url(source, album_id)}")
                print("============================================================\n")
                
                ans = input("Confermi questa identificazione? [Y/n/s (skip)]: ").strip().lower()
                if ans in ('s', 'skip'):
                    print("File saltato.")
                    continue
                elif ans not in ('', 'y', 'yes'):
                    ident = None
        
        if not ident:
            if auto_mode:
                print(f"[Auto-Mode] Album not identified for query '{default_query}'. Skipping file.")
                continue
                
            print("\n--- Manual Identification ---")
            prompt = f"Enter search query (invio per '{default_query}', 's' per saltare): "
            query = input(prompt).strip()
            
            if query == "":
                query = default_query
                
            if query.lower() in ('s', 'skip'):
                print("File saltato.")
                continue
                
            if query:
                from core.metadata_service import get_primary_source, get_client_for_source
                source = get_primary_source()
                client = get_client_for_source(source)
                if client and hasattr(client, 'search_albums'):
                    try:
                        print(f"Searching {source} for '{query}'...")
                        results = client.search_albums(query, limit=5)
                        if results:
                            print("\nSelect the correct album:")
                            for idx, r in enumerate(results):
                                name = get_field(r, 'name')
                                artists_raw = get_field(r, 'artists')
                                artists_list = []
                                if artists_raw:
                                    for a in artists_raw:
                                        if isinstance(a, str):
                                            artists_list.append(a)
                                        elif isinstance(a, dict):
                                            artists_list.append(a.get('name') or '')
                                        elif hasattr(a, 'name'):
                                            artists_list.append(a.name)
                                artist = ", ".join(artists_list) if artists_list else (get_field(r, 'artist') or 'Unknown')
                                url = get_source_url(source, get_field(r, 'id'))
                                total_tracks = get_field(r, 'total_tracks') or get_field(r, 'track_count')
                                tracks_str = f" ({total_tracks} tracce)" if total_tracks is not None else ""
                                print(f"  [{idx + 1}] {name} by {artist}{tracks_str}")
                                print(f"      ID: {get_field(r, 'id')} | Link: {url}")
                            print("  [0] Skip/None")
                            sel = input("Choice: ").strip()
                            if sel.lower() in ('s', 'skip', '0'):
                                print("File saltato.")
                                continue
                            elif sel.isdigit() and 1 <= int(sel) <= len(results):
                                selected = results[int(sel) - 1]
                                artists_raw = get_field(selected, 'artists')
                                artists_list = []
                                if artists_raw:
                                    for a in artists_raw:
                                        if isinstance(a, str):
                                            artists_list.append(a)
                                        elif isinstance(a, dict):
                                            artists_list.append(a.get('name') or '')
                                        elif hasattr(a, 'name'):
                                            artists_list.append(a.name)
                                artist = ", ".join(artists_list) if artists_list else (get_field(selected, 'artist') or 'Unknown')
                                
                                images = get_field(selected, 'images')
                                image_url = get_field(selected, 'image_url') or ''
                                if not image_url and images:
                                    image_url = images[0].get('url') if isinstance(images[0], dict) else getattr(images[0], 'url', '')
                                
                                ident = {
                                    'album_id': get_field(selected, 'id'),
                                    'album_name': get_field(selected, 'name'),
                                    'artist_name': artist,
                                    'artist_id': '',
                                    'source': source,
                                    'image_url': image_url,
                                    'release_date': get_field(selected, 'release_date', '')
                                }
                            else:
                                print("Scelta non valida. File saltato.")
                                continue
                        else:
                            print("No search results found. File saltato.")
                            continue
                    except Exception as e:
                        print("Search error:", e)
                        continue
            else:
                print("Nessuna chiave di ricerca inserita. File saltato.")
                continue

        if not ident:
            print("Album non identificato. File saltato.")
            continue

        # Fetch tracklist for this album
        print("Fetching tracklist...")
        from core.metadata_service import get_client_for_source
        client = get_client_for_source(ident['source'])
        album_data = None
        try:
            if hasattr(client, 'get_album'):
                album_data = client.get_album(ident['album_id'])
            if not album_data and hasattr(client, 'get_album_metadata'):
                album_data = client.get_album_metadata(str(ident['album_id']), include_tracks=True)
            if not album_data and hasattr(client, 'get_album_tracks'):
                tracks_data = client.get_album_tracks(str(ident['album_id']))
                if tracks_data:
                    album_data = {'id': ident['album_id'], 'name': ident.get('album_name'), 'tracks': tracks_data}
        except Exception as e:
            print("Error fetching tracklist:", e)
            continue

        tracks = []
        if isinstance(album_data, dict):
            if 'tracks' in album_data:
                raw = album_data['tracks']
                if isinstance(raw, dict) and 'items' in raw:
                    tracks = raw['items']
                elif isinstance(raw, dict) and 'data' in raw:
                    tracks = raw['data']
                elif isinstance(raw, list):
                    tracks = raw
            elif 'items' in album_data:
                tracks = album_data['items']
        elif hasattr(album_data, 'tracks'):
            raw = getattr(album_data, 'tracks')
            if hasattr(raw, 'data'):
                tracks = getattr(raw, 'data')
            else:
                tracks = raw

        if not tracks:
            print("Could not retrieve tracklist. File saltato.")
            continue

        # Convert to flat list
        flat_tracks = []
        for t in tracks:
            if isinstance(t, dict):
                flat_tracks.append(t)
            else:
                # Convert object to dict to keep match logic uniform
                flat_tracks.append({
                    'id': getattr(t, 'id', ''),
                    'name': getattr(t, 'name', ''),
                    'track_number': getattr(t, 'track_number', getattr(t, 'position', 1)),
                    'disc_number': getattr(t, 'disc_number', 1),
                    'duration_ms': getattr(t, 'duration_ms', 0),
                    'artists': getattr(t, 'artists', []),
                    'uri': getattr(t, 'uri', '')
                })

        # Print tracklist with textual similarity distance
        print("\nTracklist dell'album:")
        file_title = tags.get('title') or ''
        if isinstance(file_title, list):
            file_title = file_title[0] if file_title else ''
        file_title_clean = str(file_title).strip().lower()
        
        from difflib import SequenceMatcher
        
        for idx, t in enumerate(flat_tracks):
            disc = t.get('disc_number') or 1
            num = t.get('track_number') or (idx + 1)
            name = t.get('name')
            artists = []
            if t.get('artists'):
                for a in t.get('artists'):
                    if isinstance(a, dict) and a.get('name'):
                        artists.append(a.get('name'))
                    elif isinstance(a, str):
                        artists.append(a)
                    elif hasattr(a, 'name'):
                        artists.append(a.name)
            artist_str = f" (feat. {', '.join(artists)})" if artists and artists[0].lower() != ident.get('artist_name', '').lower() else ""
            
            # Calculate sequence similarity ratio
            ratio = SequenceMatcher(None, file_title_clean, str(name).strip().lower()).ratio()
            sim_str = f" | Simmetria: {ratio:.1%}" if ratio > 0.2 else ""
            
            print(f"  [{idx + 1}] Disco {disc}, Traccia #{num}: {name}{artist_str}{sim_str}")

        # Select best matching track by text similarity
        best_text_idx = None
        best_text_ratio = 0.0
        for idx, t in enumerate(flat_tracks):
            t_name = str(t.get('name') or '').strip().lower()
            ratio = SequenceMatcher(None, file_title_clean, t_name).ratio()
            if ratio > best_text_ratio:
                best_text_ratio = ratio
                best_text_idx = idx
                
        default_idx = None
        default_conf = 0.0
        if best_text_idx is not None and best_text_ratio > 0.3:
            default_idx = best_text_idx
            default_conf = best_text_ratio

        # In auto_mode, check if the best match satisfies the confidence threshold
        if auto_mode:
            if default_idx is not None and default_conf >= min_conf_val:
                selected_idx = default_idx
                print(f"[Auto-Mode] Automatically selected track: '{flat_tracks[selected_idx].get('name')}' (Simmetria: {default_conf:.1%})")
            else:
                if default_idx is not None:
                    print(f"[Auto-Mode] Track match too weak ({default_conf:.1%} < {min_conf_val * 100:.1%}). Skipping file.")
                else:
                    print(f"[Auto-Mode] No track match found. Skipping file.")
                continue
        else:
            if default_idx is not None:
                default_track_name = flat_tracks[default_idx].get('name')
                default_disc = flat_tracks[default_idx].get('disc_number') or 1
                default_num = flat_tracks[default_idx].get('track_number') or 1
                prompt = f"Associa alla traccia (invio per default [{default_idx + 1}] - Disco {default_disc} #{default_num} \"{default_track_name}\" (Simmetria: {default_conf:.1%}), o inserisci indice, 's' per saltare): "
            else:
                prompt = "Associa alla traccia (inserisci il numero dell'indice, 's' per saltare): "

            ans = input(prompt).strip()
            
            selected_idx = None
            if ans == "":
                if default_idx is not None:
                    selected_idx = default_idx
                else:
                    print("File saltato (nessuna scelta di default).")
                    continue
            elif ans.lower() in ('s', 'skip'):
                print("File saltato.")
                continue
            elif ans.isdigit():
                val = int(ans)
                if 1 <= val <= len(flat_tracks):
                    selected_idx = val - 1
                else:
                    print("Indice non valido. File saltato.")
                    continue
            else:
                print("Scelta non valida. File saltato.")
                continue

        selected_track = flat_tracks[selected_idx]
        conf = 1.0 if selected_idx != default_idx else default_conf
        
        selected_matches.append({
            'file': f,
            'track': selected_track,
            'ident': ident,
            'flat_tracks': flat_tracks,
            'album_data': album_data,
            'confidence': conf
        })
        print(f"  -> Selezionato: Disco {selected_track.get('disc_number') or 1} #{selected_track.get('track_number') or 1} - \"{selected_track.get('name')}\" per l'album \"{ident['album_name']}\"")

    if not selected_matches:
        print("\nNessun file confermata per l'importazione in questo batch.")
        continue

    # Print summary for batch with text similarity percentages
    print("\n--- Riepilogo Importazione Batch ---")
    for m in selected_matches:
        conf_str = f" (Simmetria: {m['confidence']:.1%})" if m.get('confidence') is not None else ""
        print(f"  - {os.path.basename(m['file'])} -> Album: \"{m['ident']['album_name']}\" | Disco {m['track'].get('disc_number') or 1} #{m['track'].get('track_number') or 1} - \"{m['track'].get('name')}\"{conf_str}")

    confirm = input(f"\nProcedere con l'importazione di questo batch ({len(selected_matches)} file)? [Y/n]: ").strip().lower()
    if confirm not in ('', 'y', 'yes'):
        print("Importazione batch annullata.")
        continue

    # Compute duration sum of the chunk
    album_total_duration_ms = sum(int(m.get('track', {}).get('duration_ms', 0) or 0) for m in selected_matches)

    print("\nStarting import pipeline for batch...")
    for m in selected_matches:
        file_path = m['file']
        track = m['track']
        ident = m['ident']
        flat_tracks = m['flat_tracks']
        album_data = m['album_data']
        
        track_name = track.get('name')
        track_number = track.get('track_number') or 1
        disc_number = track.get('disc_number') or 1
        track_id = track.get('id') or ''
        track_isrc = str(track.get('isrc', '') or '')
        track_mbid = str(track.get('musicbrainz_recording_id', '') or track.get('mbid', '') or '')

        release_date = get_field(album_data, 'release_date') or ident.get('release_date') or ''
        
        images = get_field(album_data, 'images')
        image_url = get_field(album_data, 'image_url') or ident.get('image_url') or ''
        if not image_url and images:
            image_url = images[0].get('url') if isinstance(images[0], dict) else getattr(images[0], 'url', '')

        # Aggregate genres for this specific file
        genres = set()
        g_list = file_tags[file_path].get('genres') or []
        for g in g_list:
            if g:
                genres.add(str(g).strip())

        total_discs = 1
        disc_num_file = file_tags[file_path].get('disc_number', 1) or 1
        total_discs = max(disc_number, disc_num_file)

        # Use track duration for single file context
        track_duration_ms = track.get('duration_ms', 0)

        context_key = f"cli_import_{candidate.folder_hash}_{track_number}"
        context = {
            'source': ident['source'],
            '_download_username': 'auto_import',
            'spotify_artist': {
                'id': '',
                'name': ident.get('artist_name'),
                'genres': list(genres),
            },
            'spotify_album': {
                'id': ident['album_id'],
                'name': ident['album_name'],
                'release_date': release_date,
                'total_tracks': len(flat_tracks),
                'total_discs': total_discs,
                'image_url': image_url,
                'images': [{'url': image_url}] if image_url else [],
                'artists': [{'name': ident.get('artist_name'), 'id': ''}],
                'album_type': 'album',
                'duration_ms': track_duration_ms,
            },
            'track_info': {
                'name': track_name,
                'id': track_id,
                'track_number': track_number,
                'disc_number': disc_number,
                'duration_ms': track_duration_ms,
                'artists': [{'name': a} for a in track.get('artists', [ident.get('artist_name')])],
                'uri': track.get('uri', ''),
                'album_id': ident['album_id'],
                'isrc': track_isrc,
                'musicbrainz_recording_id': track_mbid,
            },
            'original_search_result': {
                'title': track_name,
                'artist': ident.get('artist_name'),
                'album': ident['album_name'],
                'track_number': track_number,
                'disc_number': disc_number,
                'spotify_clean_title': track_name,
                'spotify_clean_album': ident['album_name'],
                'spotify_clean_artist': ident.get('artist_name'),
                'artists': [{'name': a} for a in track.get('artists', [ident.get('artist_name')])],
            },
            'is_album_download': True,
            'has_clean_spotify_data': True,
            'has_full_spotify_metadata': True,
        }

        try:
            web_server._post_process_matched_download(context_key, context, file_path)
            print(f"  {os.path.basename(file_path)}: SUCCESS")
        except Exception as e:
            print(f"  {os.path.basename(file_path)}: FAILED -> {e}")

print("\nAll batches completed!")

import csv
import os
import sys
import re
import json
import asyncio
import argparse
from cloakbrowser import launch_persistent_context_async

def log(msg):
    print(msg, flush=True)

def sanitize_name(name):
    """Rimuove caratteri non ammessi nei nomi di directory su filesystem (mantenendo &, +, spazi)."""
    if not name:
        return "Unknown"
    # Sostituisce solo caratteri illegali sul filesystem: / \ * ? : " < > |
    cleaned = re.sub(r'[/\\*?:"<>|]', '-', name)
    cleaned = cleaned.strip('. ')
    return cleaned if cleaned else "Unknown"

def extract_clean_amazon_url(href):
    """Estrae e normalizza l'URL traccia di Amazon Music per Lucida.to."""
    if not href:
        return None
    
    # Ignora esplicitamente link ad album, playlist o artisti (a meno che non contengano trackAsin)
    if ("/albums/" in href or "/playlists/" in href or "/artists/" in href) and "trackAsin=" not in href:
        return None

    # 1. Se contiene un trackAsin (es. playlist o album con parametro trackAsin), estraiamo l'ID traccia
    asin_match = re.search(r'trackAsin=([A-Z0-9]+)', href)
    if asin_match:
        return f"https://music.amazon.it/tracks/{asin_match.group(1)}"
    
    # 2. Se è già un percorso traccia diretto
    if "/tracks/" in href:
        track_match = re.search(r'/tracks/([A-Z0-9]+)', href)
        if track_match:
            return f"https://music.amazon.it/tracks/{track_match.group(1)}"
            
    # 3. Altrimenti normalizza
    if href.startswith("http"):
        return href
    if href.startswith("/"):
        return f"https://music.amazon.it{href}"
    return f"https://music.amazon.it/{href}"

def load_progress(progress_file):
    if os.path.exists(progress_file):
        try:
            with open(progress_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def save_progress(progress_file, progress_data):
    try:
        with open(progress_file, "w", encoding="utf-8") as f:
            json.dump(progress_data, f, indent=2, ensure_ascii=False)
    except Exception as e:
        log(f"[WARNING] Impossibile salvare progress file: {e}")

def get_track_output_dir(base_output_dir, artist, album, group_albums=False):
    """Calcola la cartella di destinazione in base alla modalità di raggruppamento."""
    base_dir = os.path.expanduser(base_output_dir)
    if not group_albums:
        return base_dir
    
    safe_artist = sanitize_name(artist)
    safe_album = sanitize_name(album) if album else "Singles"
    target_dir = os.path.join(base_dir, safe_artist, safe_album)
    os.makedirs(target_dir, exist_ok=True)
    return target_dir

async def dismiss_amazon_cancel_buttons(page):
    """Verifica e clicca eventuali tasti di chiusura/annulla ([name='cancel'], banner, popup o clear)."""
    try:
        cancel_selectors = [
            'music-button[name="cancel"]',
            'button[name="cancel"]',
            '[name="cancel"]',
            'music-button[icon-name="cancel"]',
            '[icon-name="cancel"]',
            'music-button[aria-label="Chiudi"]',
            'music-button[aria-label="Close"]',
            'button[aria-label="Close"]'
        ]
        for sel in cancel_selectors:
            elements = await page.query_selector_all(sel)
            for el in elements:
                if await el.is_visible():
                    try:
                        log(f"    [Amazon Music] Tasto cancel/chiudi rilevato ({sel}), clicco...")
                        await el.click()
                        await page.wait_for_timeout(400)
                    except Exception:
                        pass
    except Exception:
        pass

async def search_single_track_amazon(page, artist, title, album=None):
    # Prima di iniziare la ricerca controlla se ci sono popup o tasti cancel
    await dismiss_amazon_cancel_buttons(page)
    
    query = f"{artist} {title}".strip()
    log(f"  [Amazon Music] Ricerca: '{query}'...")
    
    search_input = page.locator("#navbarSearchInput")
    await search_input.focus()
    await search_input.fill("")
    await search_input.fill(query)
    await search_input.press("Enter")
    
    await page.wait_for_timeout(3500)
    
    # Controlla nuovamente se è apparso un popup promozionale o banner con cancel
    await dismiss_amazon_cancel_buttons(page)
    
    # 1. Cerca tra elementi orizzontali (brani singoli)
    h_items = await page.query_selector_all("music-horizontal-item")
    for item in h_items:
        href = await item.get_attribute("primary-href")
        item_title = await item.get_attribute("primary-text") or ""
        clean_url = extract_clean_amazon_url(href)
        if clean_url:
            log(f"    -> Trovato brano: '{item_title}' -> {clean_url}")
            return clean_url
            
    # 2. Cerca tra gli shoveler qualsiasi link contenente trackAsin o brani
    shovelers = await page.query_selector_all("music-shoveler")
    for s in shovelers:
        v_items = await s.query_selector_all("music-vertical-item")
        for item in v_items:
            href = await item.get_attribute("primary-href")
            clean_url = extract_clean_amazon_url(href)
            if clean_url and "/tracks/" in clean_url:
                log(f"    -> Trovato elemento alternativo: {clean_url}")
                return clean_url
                
    log("    -> [!] Nessun risultato utile trovato su Amazon Music.")
    return None

async def download_single_track_lucida(page, url, out_dir):
    log(f"  [Lucida.to] Invio URL: {url}")
    os.makedirs(out_dir, exist_ok=True)
    
    await page.goto("https://lucida.to/")
    try:
        await page.wait_for_selector("#download", timeout=30000)
    except Exception:
        log("    -> [!] Timeout caricamento interfaccia Lucida.to.")
        return False, "TIMEOUT_LUCIDA_LOAD", None
        
    search_input = page.locator("#download")
    await search_input.fill("")
    await search_input.fill(url)
    
    go_button = page.locator("#go")
    await go_button.click()
    
    await page.wait_for_timeout(3000)
    
    error_locator = page.locator("text=/An error occur/i")
    download_locator = page.locator(".download-button").or_(page.locator("text=/scarica traccia/i"))
    combined_locator = error_locator.or_(download_locator)
    
    try:
        await combined_locator.first.wait_for(state="visible", timeout=60000)
    except Exception:
        log("    -> [!] Timeout attesa risposta da Lucida.")
        return False, "TIMEOUT_LUCIDA_PROCESS", None
        
    if await error_locator.is_visible():
        log("    -> [!] Lucida ha restituito errore per questo URL.")
        return False, "LUCIDA_ERROR", None
        
    if await download_locator.first.is_visible():
        log("    -> Brano pronto! Avvio download...")
        try:
            async with page.expect_download(timeout=60000) as download_info:
                await download_locator.first.evaluate("el => el.click()")
            download = await download_info.value
            dest_path = os.path.join(out_dir, download.suggested_filename)
            await download.save_as(dest_path)
            log(f"    -> [SUCCESS] Salvato in: {dest_path}")
            return True, "SUCCESS", dest_path
        except Exception as e:
            log(f"    -> [!] Errore durante il salvataggio del download: {e}")
            return False, f"DOWNLOAD_FAILED: {e}", None
        
    return False, "UNKNOWN_STATE", None

async def run_pipeline(csv_path, output_dir, limit=None, skip=0, resume=True, group_albums=False, filter_album=None, filter_artist=None):
    out_dir = os.path.expanduser(output_dir)
    os.makedirs(out_dir, exist_ok=True)
    
    progress_file = os.path.join(out_dir, ".wishlist_progress.json")
    progress = load_progress(progress_file) if resume else {}
    
    if not os.path.exists(csv_path):
        log(f"File CSV non trovato: {csv_path}")
        sys.exit(1)
        
    all_tracks = []
    with open(csv_path, mode="r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            all_tracks.append(row)
            
    # Filtro opzionale per artista o album
    filtered_tracks = []
    for t in all_tracks:
        if filter_artist and filter_artist.lower() not in t.get("Artist", "").lower():
            continue
        if filter_album and filter_album.lower() not in t.get("Album", "").lower():
            continue
        filtered_tracks.append(t)
            
    total_tracks = len(filtered_tracks)
    log("="*60)
    log("AVVIO BATCH DOWNLOADER")
    log(f"Cartella base: {out_dir}")
    log(f"Raggruppamento per Album: {'ABILITATO (<Artista>/<Album>/)' if group_albums else 'DISABILITATO (Cartella unica)'}")
    if skip > 0:
        log(f"Offset / Righe da skippare: {skip} (conteggio totale preservato)")
    if limit:
        log(f"Limite elaborazione: {limit} brani")
    if filter_artist:
        log(f"Filtro Artista: {filter_artist}")
    if filter_album:
        log(f"Filtro Album: {filter_album}")
    log(f"Totale brani nella selezione: {total_tracks}")
    log("="*60)
    
    if total_tracks == 0:
        log("Nessun brano trovato con i filtri specificati.")
        return
        
    xdg_data = os.environ.get('XDG_DATA_HOME', os.path.expanduser('~/.local/share'))
    amazon_profile = os.path.join(xdg_data, 'browser-profiles', 'amazon-music')
    lucida_profile = os.path.join(xdg_data, 'browser-profiles', 'lucida')
    
    log(f"[1/2] Avvio sessione Amazon Music...")
    amz_context = await launch_persistent_context_async(amazon_profile, headless=False)
    amz_page = await amz_context.new_page()
    await amz_page.set_viewport_size({"width": 1280, "height": 800})
    await amz_page.goto("https://music.amazon.it/")
    await amz_page.wait_for_timeout(6000)
    
    log(f"[2/2] Avvio sessione Lucida.to...")
    lucida_context = await launch_persistent_context_async(lucida_profile, headless=False)
    lucida_page = await lucida_context.new_page()
    await lucida_page.set_viewport_size({"width": 1280, "height": 800})
    await lucida_page.goto("https://lucida.to/")
    try:
        await lucida_page.wait_for_selector("#download", timeout=60000)
    except Exception:
        log("[WARNING] Superamento Cloudflare iniziale su Lucida richiesto...")
        
    success_count = 0
    skipped_count = 0
    processed_in_session = 0
    
    try:
        for idx, track in enumerate(filtered_tracks, 1):
            track_id = track.get("ID") or track.get("Track ID") or f"{track.get('Artist')}_{track.get('Title')}"
            artist = track.get("Artist", "").strip()
            title = track.get("Title", "").strip()
            album = track.get("Album", "").strip()
            
            # Gestione dello SKIP/OFFSET mantenendo il conteggio totale
            if idx <= skip:
                log(f"\n[{idx}/{total_tracks}] [SKIP OFFSET MANUALE ({idx}/{skip})] {artist} - {title} ({album})")
                skipped_count += 1
                continue
                
            # Controllo limite brani elaborati in questa sessione
            if limit and processed_in_session >= limit:
                log(f"\n[INFO] Raggiunto limite sessione di {limit} brani elaborati. Arresto programmato.")
                break
                
            # Calcola la cartella specifica per questo brano
            target_track_dir = get_track_output_dir(out_dir, artist, album, group_albums=group_albums)
            
            # Controllo se già scaricato con successo
            if resume and track_id in progress and progress[track_id].get("status") == "SUCCESS":
                saved_f = progress[track_id].get("file", "")
                if os.path.exists(saved_f):
                    log(f"\n[{idx}/{total_tracks}] [SKIP GIÀ SCARICATO] {artist} - {title} ({album})")
                    success_count += 1
                    processed_in_session += 1
                    continue
                    
            log(f"\n[{idx}/{total_tracks}] Elaborazione: {artist} - {title} | Album: '{album}'")
            log(f"    -> Cartella destinazione: {target_track_dir}")
            processed_in_session += 1
            
            # Step 1: Trova link Amazon
            try:
                amazon_url = await search_single_track_amazon(amz_page, artist, title, album=album)
            except Exception as e:
                log(f"    -> [ERRORE RICERCA AMAZON]: {e}")
                amazon_url = None
                
            if not amazon_url:
                log(f"    -> [SKIP] Nessun link trovato su Amazon. Procedo con il prossimo brano.")
                progress[track_id] = {"status": "AMAZON_NOT_FOUND", "artist": artist, "title": title, "album": album}
                save_progress(progress_file, progress)
                skipped_count += 1
                continue
                
            # Step 2: Scarica da Lucida salvando nella cartella appropriata
            try:
                ok, status_msg, saved_path = await download_single_track_lucida(lucida_page, amazon_url, target_track_dir)
            except Exception as e:
                log(f"    -> [ERRORE DOWNLOAD LUCIDA]: {e}")
                ok, status_msg, saved_path = False, f"ERROR: {e}", None
                
            if ok:
                success_count += 1
                progress[track_id] = {
                    "status": "SUCCESS",
                    "artist": artist,
                    "title": title,
                    "album": album,
                    "amazon_url": amazon_url,
                    "file": saved_path
                }
            else:
                skipped_count += 1
                progress[track_id] = {
                    "status": status_msg,
                    "artist": artist,
                    "title": title,
                    "album": album,
                    "amazon_url": amazon_url
                }
                log(f"    -> [SKIP] Errore ({status_msg}). Procedo con il prossimo brano.")
                
            save_progress(progress_file, progress)
            
    finally:
        log("\nChiusura sessioni browser...")
        try:
            await amz_context.close()
        except Exception:
            pass
        try:
            await lucida_context.close()
        except Exception:
            pass
            
    log("\n" + "="*50)
    log("RIEPILOGO FINALE DOWNLOAD")
    log("="*50)
    log(f"Completati con successo: {success_count}/{total_tracks}")
    log(f"Saltati / Errori: {skipped_count}/{total_tracks}")
    log(f"Progress file: {progress_file}")

def main():
    parser = argparse.ArgumentParser(description="Download Sequenziale Wishlist/Album (Amazon Music -> Lucida.to)")
    default_downloads = os.path.expanduser("~/Downloads")
    default_csv = os.path.join(default_downloads, "wishlist_tracks.csv")
    parser.add_argument("--csv", default=default_csv, help="Percorso del file CSV wishlist")
    parser.add_argument("--skip", type=int, default=0, help="Numero di righe iniziali da saltare mantenendo il conteggio totale (default: 0)")
    parser.add_argument("--limit", type=int, default=None, help="Limite brani da processare in questa sessione (default: tutti)")
    parser.add_argument("--output-dir", default=default_downloads, help="Directory base di download (default: ~/Downloads)")
    parser.add_argument("--group-albums", action="store_true", help="Salva i brani in sottocartelle create come: <Artista>/<Album>/")
    parser.add_argument("--album", default=None, help="Filtra e scarica solo un album specifico (es: 'J-Ax & Friends')")
    parser.add_argument("--artist", default=None, help="Filtra e scarica solo un artista specifico (es: 'Articolo 31')")
    parser.add_argument("--no-resume", action="store_true", help="Non riprendere dai brani già scaricati")
    
    args = parser.parse_args()
    asyncio.run(run_pipeline(
        csv_path=args.csv,
        output_dir=args.output_dir,
        limit=args.limit,
        skip=args.skip,
        resume=not args.no_resume,
        group_albums=args.group_albums,
        filter_album=args.album,
        filter_artist=args.artist
    ))

if __name__ == "__main__":
    main()

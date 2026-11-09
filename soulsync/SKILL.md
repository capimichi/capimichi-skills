# SoulSync Knowledge Base & Operational Skill

Questa guida raccoglie le conoscenze architetturali, diagnostiche e operative per la gestione dell'istanza **SoulSync**, della sua integrazione con **Navidrome** e **slskd**, dell'analisi dei log, della risoluzione dei disallineamenti di percorso e dell'estrazione dei dati.

---

## 1. Architettura & Deployment

* **Host del server:** `192.168.1.100` (`root@192.168.1.100`)
* **Container Docker:** `soulsync-webui`
* **Cartella radice sul server:** `/home/capimichi/docker/soulsync`
* **Database SQLite:** 
  * Volume Docker: `soulsync_soulsync_database`
  * Percorso Host: `/var/lib/docker/volumes/soulsync_soulsync_database/_data/music_library.db`
  * Percorso Container: `/app/data/music_library.db`
* **Storage Musicale (Mounts):**
  * Host Libreria: `/mnt/wd/media/audio/navidrome` $\rightarrow$ Container SoulSync: `/app/Transfer`
  * Host Import (Staging): `/mnt/wd/media/audio/import` $\rightarrow$ Container SoulSync: `/app/Staging`
  * Container Navidrome: `/music` (sola lettura su `/mnt/wd/media/audio/navidrome`)
* **File di Configurazione:** `/home/capimichi/docker/soulsync/config/config.json`

---

## 2. Consultazione Log & Monitoraggio

I log applicativi di SoulSync vengono scritti sul file `/app/logs/app.log` (mappato sull'host in `/home/capimichi/docker/soulsync/logs/app.log`).

### Comandi diagnostici rapidi:
```bash
# Vedere gli ultimi log in tempo reale
ssh root@192.168.1.100 "tail -f /home/capimichi/docker/soulsync/logs/app.log"

# Filtrare per errori e warning recenti
ssh root@192.168.1.100 "grep -E 'ERROR|WARNING' /home/capimichi/docker/soulsync/logs/app.log | tail -n 50"

# Monitorare i log diretti del container
ssh root@192.168.1.100 "docker logs --tail 100 -f soulsync-webui"
```

---

## 3. Gestione Dead File Cleaner & Disallineamento Percorsi (Navidrome Subsonic)

### Il Problema:
Quando si esegue il job **Dead File Cleaner** o **Orphan File Detector** in SoulSync, potrebbe apparire l'errore:
> `X of X tracks point to paths SoulSync can't reach — almost always a path-mapping issue (Docker mount, or Settings → Library → Music Paths), not deleted files. No findings created.`

### La Causa Tecnica:
1. **Template personalizzati su disco:** Su disco, SoulSync salva i brani usando il template configurato (es. `$albumartist/$albumartist - $album/$track - $title` $\rightarrow$ `Queen/Queen - Greatest Hits/01 - Bohemian Rhapsody.mp3`).
2. **Percorsi Virtuali di Navidrome:** Quando SoulSync sincronizza la libreria tramite l'API Subsonic di Navidrome, Navidrome restituisce percorsi virtuali standardizzati basati sui metadati:
   `<Artist>/<Album>/<Disc>-<Track> - <Title>.<ext>` $\rightarrow$ `Queen/Greatest Hits/01-01 - Bohemian Rhapsody.mp3`.
3. **Mancata corrispondenza nel Resolver:** SoulSync memorizza il percorso virtuale nel database (`tracks.file_path`). Quando il Dead File Cleaner cerca quel file in `/app/Transfer`, fallisce per discrepanza sia del nome cartella dell'album sia del prefisso del disco. La soglia di sicurezza di SoulSync blocca l'operazione se oltre il 50% dei brani risulta non trovato.

### La Soluzione Definitiva:
1. Accedere alla **Web UI di Navidrome** (es. `https://navidrome.michelecapicchioni.com`).
2. Cliccare sull'icona del proprio **Profilo** in alto a destra $\rightarrow$ **Players** (Lettori).
3. Selezionare il client **SoulSync** nella lista dei dispositivi connessi.
4. Abilitare l'opzione **`Report Real Path`** (Invia percorsi reali).
5. Salvare e tornare nella **Web UI di SoulSync**.
6. Eseguire un **"Full database refresh"** (oppure un **Deep Scan** dalla Dashboard).

---

## 4. Servizi di Enrichment in "Pause" (Yield Policy)

Se nella dashboard o nella sezione Enrichment i servizi di metadata background (MusicBrainz, Spotify, Deezer, Last.fm, Genius, ecc.) risultano in stato **Pause**:

* **Auto-Yield Policy:** SoulSync mette **automaticamente in pausa** tutti i worker di arricchimento di background quando ci sono **download attivi o in fase di post-processing**.
* **Motivazione:** Evitare la saturazione delle quote e dei rate-limit delle API esterne (es. MusicBrainz a 1 req/sec), che altrimenti farebbero durare i download dei singoli brani diversi minuti.
* **Comportamento:** Non appena la coda dei download termina, SoulSync riprende automaticamente tutti i worker (*"Auto-resumed after foreground work finished"*).
* **Outage di servizi specifici:** Se un singolo servizio esterno risponde con errori 5xx (es. Amazon proxy `503 Service Unavailable`), SoulSync attiva un cooldown temporaneo senza bloccare l'intero sistema.

---

## 5. Esportazione Completa della Wishlist in CSV

La Wishlist contiene tutti i brani che hanno fallito il download, non hanno trovato corrispondenze su Soulseek o sono stati accodati tramite download discografia.

### Tabella Database:
* Tabella: `wishlist_tracks`
* Colonne chiave: `id`, `spotify_track_id`, `spotify_data` (JSON contenente artista, album, titolo), `failure_reason`, `retry_count`, `date_added`, `source_type`.

### Utilizzo dello Script di Esportazione:
Per esportare l'intera Wishlist (anche con migliaia di brani) in un CSV pulito sul Mac locale:

```bash
# Esecuzione script (salva di default in ~/Downloads/wishlist_tracks.csv)
python3 soulsync/export_wishlist_csv.py

# Specificare un percorso di output personalizzato
python3 soulsync/export_wishlist_csv.py -o /percorso/desiderato/wishlist.csv
```

---

## 6. API REST di SoulSync (Wishlist & Automazione)

* **URL Base:** `https://soulsync.michelecapicchioni.com`
* **Autenticazione:** `Authorization: Bearer <API_KEY>` (letta dalla variabile d'ambiente `SOULSYNC_API_KEY`)

### Endpoint Principali:
* `GET /api/v1/wishlist` — Lista brani in wishlist (JSON)
* `POST /api/v1/wishlist/process` — Forza il ri-processamento immediato dei brani in wishlist
* `DELETE /api/v1/wishlist/<track_id>` — Rimuove un brano dalla wishlist
* `GET /api/enrichment/status-all` — Stato cumulativo di tutti i servizi di enrichment

---

## 7. Importazione Interattiva da CLI (File Misti o Parziali)

Quando si caricano album parziali o singoli brani sparsi nella cartella Staging, l'auto-importer automatico di SoulSync potrebbe penalizzarne il punteggio a causa delle politiche di copertura dell'album:
$$\text{Confidence} = \text{Album Confidence} \times \text{Average Track Confidence} \times \text{Coverage}$$

Per superare questo limite e importare correttamente i brani risolvendo eventuali disallineamenti di tag (ad es. collisioni di dischi o tracce duplicate in edizioni multioro/multiplatinum), è disponibile lo script di importazione interattiva `cli_import.py`.

### Comportamento & Funzionalità:
* **Analisi Per-File**: Rileva singolarmente l'album di appartenenza di ogni brano tramite Exact IDs (ISRC), AcoustID e Tag.
* **Supporto Cartelle Miste**: Puoi caricare cartelle con tracce di album diversi. Ogni file verrà associato al proprio album di destinazione.
* **Correzione Manuale**: Se l'identificazione automatica fallisce o associa il singolo release promozionale anziché l'album, è possibile effettuare una ricerca manuale inserendo l'album (la ricerca propone già una chiave pre-compilata basata sui tag del file).
* **Selezione Traccia**: Mostra la tracklist dell'album con indicazione delle tracce per disco e consente di digitare il numero corrispondente per mappare il file fisici.
* **Visualizzazione Tracce Album**: Mostra il numero totale di tracce dell'album nei risultati di ricerca per riconoscere subito i dischi completi da EP o singoli.

### Gestione Singoli vs Album Completi (Best Practice per LLM / Agenti):
Molte tracce musicali sono pubblicate inizialmente come "Singoli" o "EP" (contenenti solo 1 o 2 brani) e successivamente incluse in un "Album Studio" o "Compilation" completo (10-20 tracce). Durante l'importazione interattiva guidata dall'LLM:
* **Verificare il Conteggio Tracce**: Controllare sempre il campo `total_tracks` (o `track_count`) associato al risultato di ricerca dell'album.
* **Privilegiare Album Completi**: Preferire e raccomandare nei suggerimenti l'album con il maggior numero di tracce (es. 12 tracce anziché 1 o 2). Evita di catalogare i brani sparsi in singoli o EP scollegati se esiste l'album di studio di riferimento.
* **Interazione con l'Utente**: Evidenziare la discrepanza all'utente prima dell'import (es. *"Ho trovato la traccia sia come Singolo (1 traccia) sia all'interno dell'album X (15 tracce). Di default propongo l'album, confermi?"*).

---

## 8. Strumentazione MCP (`mcp_import.py`)

Per l'integrazione con l'LLM, è presente lo script di orchestrazione [mcp_import.py](file:///Users/michele/PycharmProjects/capimichi-skills/soulsync/mcp_import.py) sul Mac locale, che esegue comandi remoti nel container e restituisce risposte in formato **JSON**.

### Sotto-comandi disponibili:

1. **`scan <directory_path> [limit=20] [offset=0]`**
   * Esegue la scansione paginata della cartella di staging.
   * Restituisce:
     ```json
     {
       "total_files": 27,
       "limit": 20,
       "offset": 0,
       "files": [
         {
           "file_path": "/app/Staging/Eminem/...",
           "file_name": "Eminem - Not Afraid.flac",
           "title": "Not Afraid",
           "artist": "Eminem",
           "album": "Recovery"
         }
       ]
     }
     ```

2. **`identify <file_path>`**
   * Tenta l'identificazione automatica per un singolo file (Exact IDs, AcoustID, Tag).
   * Restituisce:
     ```json
     {
       "identified": true,
       "method": "Exact IDs",
       "album_name": "Recovery",
       "artist_name": "Eminem",
       "album_id": "595243",
       "source": "deezer",
       "total_tracks": 17,
       "release_date": "2010-01-01",
       "link": "https://www.deezer.com/album/595243"
     }
     ```

3. **`search "<query>" [source]`**
   * Ricerca manuale di album (con indicazione di tracce totali e link) sulle API di metadati.

4. **`tracklist <album_id> <source>`**
   * Restituisce l'elenco piatto delle tracce di un album per la selezione dell'indice.

5. **`fuzzy_match <file_path> <album_id> <source>`**
   * Calcola l'associazione ottimale proponendo l'indice di default e la confidenza.

6. **`import <file_path> <album_id> <source> <track_index>`**
   * Esegue la pipeline di importazione nativa per il singolo brano mappato.

---

## 9. Comandi Operativi (CLI Tradizionale)
Per avviare l'importazione interattiva classica all'interno del container `soulsync-webui`:

```bash
# Avvio in modalità file-by-file (default, elabora e importa un file alla volta)
docker exec -it soulsync-webui python3 /app/cli_import.py "/app/Staging/<cartella_artista>"

# Avvio con prefetch (es. mappa 10 file per volta e poi esegue l'import del batch)
docker exec -it soulsync-webui python3 /app/cli_import.py "/app/Staging/<cartella_artista>" --prefetch 10

# Avvio globale (mappa tutti i file della cartella e chiede un'unica conferma di importazione alla fine)
docker exec -it soulsync-webui python3 /app/cli_import.py "/app/Staging/<cartella_artista>" --prefetch 0

# Avvio automatico con conferma a fine batch (--auto)
# Rileva e mappa automaticamente gli elementi. Di default skippa tutto ciò che ha fiducia < 90%.
docker exec -it soulsync-webui python3 /app/cli_import.py "/app/Staging/<cartella_artista>" --prefetch 10 --auto

# Avvio automatico con soglia di confidenza personalizzata (es. 80%)
docker exec -it soulsync-webui python3 /app/cli_import.py "/app/Staging/<cartella_artista>" --prefetch 10 --auto --min-confidence 80

# Pulizia automatica delle parentesi nei nomi degli album per le ricerche
# (Rimuove il testo tra tonde, quadre e graffe, es. "Listen (Deluxe)" diventa "Listen")
docker exec -it soulsync-webui python3 /app/cli_import.py "/app/Staging/<cartella_artista>" --prefetch 10 --auto --no-album-parenthesis
```

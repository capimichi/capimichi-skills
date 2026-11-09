# ListenBrainz Playlist Automation Skill

Questa guida descrive come gestire le playlist su **ListenBrainz** programmaticamente tramite le loro API ufficiali REST. A differenza di Last.fm, ListenBrainz offre un supporto completo e nativo per la creazione e modifica delle playlist, eliminando la necessità di utilizzare simulatori di browser (come Playwright/CloakBrowser).

---

## 1. Autenticazione e Lettura del Token

ListenBrainz richiede un **User Token** che viene esposto tramite la variabile d'ambiente `LISTENBRAINZ_TOKEN` (gestita via Bitwarden e `.zshrc`).

Nelle chiamate API, il token va inviato nell'header HTTP `Authorization`:
```http
Authorization: Token <USER_TOKEN>
```

### Lettura del Token in Python:
```python
import os

def get_listenbrainz_token():
    token = os.environ.get("LISTENBRAINZ_TOKEN")
    if not token:
        raise ValueError("Variabile d'ambiente LISTENBRAINZ_TOKEN non impostata.")
    return token
```

---

## 2. Creazione di una Playlist

Per creare una playlist, si invia una richiesta `POST` con la struttura della playlist in formato **JSPF** (*JSON Shareable Playlist Format*).

*   **Endpoint:** `POST https://api.listenbrainz.org/1/playlist/create`
*   **Header:** 
    *   `Authorization: Token <USER_TOKEN>`
    *   `Content-Type: application/json`

### Esempio Python (Creazione Playlist Vuota o Popolata):
```python
import requests

def create_playlist(title, description="Mia Playlist", tracks=None):
    token = get_listenbrainz_token()
    url = "https://api.listenbrainz.org/1/playlist/create"
    
    headers = {
        "Authorization": f"Token {token}",
        "Content-Type": "application/json"
    }
    
    # Struttura base JSPF
    jspf_tracks = []
    if tracks:
        for t in tracks:
            # Ogni traccia richiede l'URL MusicBrainz Recording MBID come identifier
            jspf_tracks.append({
                "identifier": f"https://musicbrainz.org/recording/{t['mbid']}",
                "title": t.get("title", ""),
                "creator": t.get("artist", "")
            })
            
    payload = {
        "playlist": {
            "title": title,
            "annotation": description,
            "extension": {
                "https://musicbrainz.org/doc/jspf#playlist": {
                    "public": True
                }
            },
            "track": jspf_tracks
        }
    }
    
    response = requests.post(url, json=payload, headers=headers)
    if response.status_code == 200:
        data = response.json()
        playlist_mbid = data.get("playlist_mbid")
        print(f"Playlist creata con successo! MBID: {playlist_mbid}")
        return playlist_mbid
    else:
        print(f"Errore {response.status_code}: {response.text}")
        return None
```

---

## 3. Visualizzazione di una Playlist

Per recuperare i dati e l'elenco delle tracce di una playlist esistente:

*   **Endpoint:** `GET https://api.listenbrainz.org/1/playlist/<playlist_mbid>`
*   **Header:** `Authorization: Token <USER_TOKEN>` (richiesto se la playlist è privata)

### Esempio Python:
```python
def get_playlist_tracks(playlist_mbid):
    token = get_listenbrainz_token()
    url = f"https://api.listenbrainz.org/1/playlist/{playlist_mbid}"
    
    headers = {"Authorization": f"Token {token}"}
    
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        playlist_data = response.json().get("playlist", {})
        tracks = playlist_data.get("track", [])
        
        print(f"Playlist: {playlist_data.get('title')}")
        print(f"Descrizione: {playlist_data.get('annotation')}")
        print(f"Tracce ({len(tracks)}):")
        
        for idx, track in enumerate(tracks, 1):
            title = track.get("title", "Sconosciuto")
            artist = track.get("creator", "Sconosciuto")
            mbid = track.get("identifier", "").split("/")[-1]
            print(f"  {idx}. {artist} - {title} (MBID: {mbid})")
        return tracks
    else:
        print(f"Errore {response.status_code}: {response.text}")
        return None
```

---

## 4. Aggiunta di Tracce a una Playlist

Per aggiungere nuove tracce in coda a una playlist esistente:

*   **Endpoint:** `POST https://api.listenbrainz.org/1/playlist/<playlist_mbid>/item/add`
*   **Header:**
    *   `Authorization: Token <USER_TOKEN>`
    *   `Content-Type: application/json`

### Esempio Python:
```python
def add_tracks_to_playlist(playlist_mbid, tracks):
    token = get_listenbrainz_token()
    url = f"https://api.listenbrainz.org/1/playlist/{playlist_mbid}/item/add"
    
    headers = {
        "Authorization": f"Token {token}",
        "Content-Type": "application/json"
    }
    
    jspf_tracks = []
    for t in tracks:
        jspf_tracks.append({
            "identifier": f"https://musicbrainz.org/recording/{t['mbid']}",
            "title": t.get("title", ""),
            "creator": t.get("artist", "")
        })
        
    payload = {
        "playlist": {
            "track": jspf_tracks
        }
    }
    
    response = requests.post(url, json=payload, headers=headers)
    if response.status_code == 200:
        print("Tracce aggiunte con successo alla playlist.")
        return True
    else:
        print(f"Errore {response.status_code}: {response.text}")
        return False
```

---

## 5. Rimozione di una Traccia dalla Playlist

Per eliminare una o più tracce partendo da un determinato indice all'interno della playlist:

*   **Endpoint:** `POST https://api.listenbrainz.org/1/playlist/<playlist_mbid>/item/delete`
*   **Header:**
    *   `Authorization: Token <USER_TOKEN>`
    *   `Content-Type: application/json`

### Esempio Python:
```python
def delete_track_from_playlist(playlist_mbid, index, count=1):
    """
    Rimuove 'count' elementi a partire dall'indice specificato (0-indexed).
    """
    token = get_listenbrainz_token()
    url = f"https://api.listenbrainz.org/1/playlist/{playlist_mbid}/item/delete"
    
    headers = {
        "Authorization": f"Token {token}",
        "Content-Type": "application/json"
    }
    
    # Specifica l'indice di partenza (0-indexed) e il numero di tracce da rimuovere
    payload = {
        "index": index,
        "count": count
    }
    
    response = requests.post(url, json=payload, headers=headers)
    if response.status_code == 200:
        print(f"Rimosse {count} tracce a partire dall'indice {index}.")
        return True
    else:
        print(f"Errore {response.status_code}: {response.text}")
        return False
```

---

## 6. Eliminazione di una Playlist

Per cancellare l'intera playlist:

*   **Endpoint:** `POST https://api.listenbrainz.org/1/playlist/<playlist_mbid>/delete`
*   **Header:** `Authorization: Token <USER_TOKEN>`

### Esempio Python:
```python
def delete_playlist(playlist_mbid):
    token = get_listenbrainz_token()
    url = f"https://api.listenbrainz.org/1/playlist/{playlist_mbid}/delete"
    
    headers = {"Authorization": f"Token {token}"}
    
    response = requests.post(url, headers=headers)
    if response.status_code == 200:
        print("Playlist eliminata con successo.")
        return True
    else:
        print(f"Errore {response.status_code}: {response.text}")
        return False
```

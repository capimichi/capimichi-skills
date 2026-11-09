# Last.fm Playlist Automation with CloakBrowser

Questa guida descrive come automatizzare la gestione delle playlist su Last.fm utilizzando Python e **CloakBrowser** (un browser stealth basato su Playwright per superare i controlli anti-bot).

---

## 1. Gestione della Sessione Persistente

Per evitare di effettuare il login ad ogni avvio (evitando anche blocchi di sicurezza), utilizziamo un profilo browser persistente.

*   **Directory del profilo:** `$XDG_DATA_HOME/browser-profiles/cloak` (default: `~/.local/share/browser-profiles/cloak`).
*   **Funzione da utilizzare:** `launch_persistent_context` di `cloakbrowser`.

### Avvio del Browser (Modalità Interattiva per Login)
Per effettuare il login manuale la prima volta:
```python
import os
from cloakbrowser import launch_persistent_context

profile_dir = os.path.join(os.environ.get('XDG_DATA_HOME', os.path.expanduser('~/.local/share')), 'browser-profiles', 'cloak')
context = launch_persistent_context(profile_dir, headless=False)
page = context.new_page()

# Naviga alla pagina di login
page.goto("https://www.last.fm/login")

# Attendere che l'utente effettui il login e prema invio in console prima di chiudere
input("Premi Invio per chiudere il browser dopo il login...")
context.close()
```

---

## 2. Recupero Dinamico dell'Username

Invece di cablare l'username nei link, lo si può estrarre dinamicamente dopo il caricamento della homepage (essendo loggati) dall'elemento dell'header:

*   **Selettore:** `.auth-dropdown-profile-info .username`

### Esempio Python:
```python
page.goto("https://www.last.fm")
page.wait_for_timeout(3000)

username_elem = page.query_selector(".auth-dropdown-profile-info .username")
if username_elem:
    username = username_elem.inner_text().strip()
    print(f"Username rilevato: {username}")
else:
    print("Utente non loggato.")
```

---

## 3. Individuazione delle Playlist

Per trovare l'elenco delle playlist dell'utente loggato:
*   **URL:** `https://www.last.fm/user/<username>/playlists`
*   **Selettore elemento playlist:** `.playlisting-playlists-item`

Ogni elemento contiene il titolo e il link relativo (contenente `/playlists/`).

### Esempio Python:
```python
page.goto(f"https://www.last.fm/user/{username}/playlists")
page.wait_for_timeout(3000)

items = page.query_selector_all(".playlisting-playlists-item")
for item in items:
    # Cerca il link della playlist
    a_tag = item.query_selector("a[href*='/playlists/']")
    if a_tag:
        title = a_tag.inner_text().strip()
        link = "https://www.last.fm" + a_tag.get_attribute("href")
        print(f"Playlist: {title} -> {link}")
```

---

## 4. Visualizzazione dei Brani in una Playlist

Per estrarre i brani correnti all'interno di una specifica playlist:
*   **URL:** `https://www.last.fm/user/<username>/playlists/<playlist_id>`
*   **Selettore della riga brano:** `.chartlist-row`
*   **Selettori interni alla riga:**
    *   Artista: `.chartlist-artist`
    *   Titolo traccia: `.chartlist-name`

### Esempio Python:
```python
rows = page.query_selector_all(".chartlist-row")
for index, row in enumerate(rows, 1):
    artist_elem = row.query_selector(".chartlist-artist")
    name_elem = row.query_selector(".chartlist-name")
    
    artist = artist_elem.inner_text().strip() if artist_elem else "Sconosciuto"
    track = name_elem.inner_text().strip() if name_elem else "Sconosciuta"
    
    print(f"{index}. {artist} - {track}")
```

---

## 5. Aggiunta di un Brano alla Playlist (Strategia di Ricerca a Due Stadi)

L'aggiunta avviene interagendo con l'interfaccia di ricerca nella pagina della playlist. Poiché la ricerca di Last.fm tende a proporre risultati errati (cover, remix, ecc.) se interrogata con query complesse, utilizziamo una **strategia in due stadi**:

### Algoritmo di Ricerca e Selezione:
1. **Stadio 1: Ricerca del Solo Titolo**
   * Digitare nel campo `#track-search` **solo il titolo del brano** (senza artista).
   * Cliccare su `button.search-submit[data-analytics-action="search"]` (quello visibile) e attendere **4-5 secondi**.
   * Scorrere i risultati nel dropdown `.playlisting-search-dropdown .chartlist-row`.
   * Controllare il testo dell'artista all'interno di `.chartlist-artist` per ciascun risultato.
   * Se viene trovato un risultato in cui l'artista corrisponde a quello desiderato, cliccare sul relativo `.chartlist-action-button` e attendere **5 secondi**. L'operazione è completata.

2. **Stadio 2: Ricerca Completa (Fallback)**
   * Se nessuno dei risultati dello Stadio 1 corrisponde all'artista desiderato, eseguire una seconda ricerca.
   * Pulire il campo e inserire la **query completa** (Titolo + Artista, es. `"Chop Suey! System of a Down"`).
   * Cliccare su Cerca e attendere **4-5 secondi**.
   * Verificare nuovamente i risultati nel dropdown cercando la riga corretta.
   * Cliccare su `.chartlist-action-button` della riga corretta e attendere **5 secondi**.

### Esempio Python:
```python
def search_and_add(page, query, expected_artist):
    # Rendi visibile l'input se nascosto
    search_input = page.query_selector("#track-search")
    if not search_input or not search_input.is_visible():
        btn = page.query_selector(".btn-add-tracks")
        if btn:
            btn.evaluate("el => el.click()")
            page.wait_for_timeout(2000)
            search_input = page.query_selector("#track-search")
            
    if not search_input:
        return False
        
    search_input.click()
    search_input.fill("")
    search_input.fill(query)
    
    # Clicca cerca (pulsante corretto visibile)
    search_btn = page.query_selector('button.search-submit[data-analytics-action="search"]')
    if not search_btn:
        return False
        
    search_btn.evaluate("el => el.click()")
    page.wait_for_timeout(5000)
    
    results = page.query_selector_all(".playlisting-search-dropdown .chartlist-row")
    for idx, row in enumerate(results):
        artist_elem = row.query_selector(".chartlist-artist")
        artist_text = artist_elem.inner_text().strip() if artist_elem else ""
        
        # Confronto case-insensitive flessibile
        if expected_artist.lower() in artist_text.lower() or artist_text.lower() in expected_artist.lower():
            add_btn = row.query_selector(".chartlist-action-button")
            if add_btn:
                add_btn.evaluate("el => el.click()")
                page.wait_for_timeout(5000)
                return True
    return False

# Utilizzo:
# success = search_and_add(page, "chop suey", "System of a Down")
# if not success:
#     success = search_and_add(page, "chop suey system of a down", "System of a Down")
```

---

## 6. Rimozione di un Brano dalla Playlist

La rimozione richiede di interagire con il dropdown di opzioni del singolo brano. Cliccare sugli elementi tramite Javascript (`evaluate("el => el.click()")`) per evitare che elementi sovrapposti (come l'header) blocchino l'interazione.

1.  Trovare la riga del brano desiderato (`.chartlist-row`).
2.  All'interno di quella riga, individuare e cliccare sul pulsante **Altro** (`.chartlist-more-button`):
    ```python
    more_btn = target_row.query_selector(".chartlist-more-button")
    more_btn.evaluate("el => el.click()")
    ```
3.  Attendere **1 secondo** per far comparire il menu a tendina.
4.  Individuare il pulsante di eliminazione **esclusivamente all'interno della stessa riga**:
    ```python
    # IMPORTANTE: Cercare all'interno del nodo target_row e non globalmente nella pagina!
    delete_btn = target_row.query_selector(".more-item--delete")
    delete_btn.evaluate("el => el.click()")
    ```
5.  Attendere **5 secondi** per il completamento dell'operazione.

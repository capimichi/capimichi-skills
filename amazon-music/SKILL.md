# Amazon Music Automation with CloakBrowser

Questa guida descrive come automatizzare l'interazione con **Amazon Music** (https://music.amazon.it/) utilizzando Python e **CloakBrowser** (un browser stealth basato su Playwright per superare i controlli anti-bot).

---

## 1. Informazioni Generali e URL di Base

*   **URL del Servizio:** `https://music.amazon.it/`
*   **Composizione Link Completi:**
    *   Gli attributi `primary-href` o `secondary-href` degli elementi restituiscono percorsi relativi (es. `/albums/B0GZKWGZV4?trackAsin=B0GZKYQZS6`).
    *   Per ottenere il link completo, unire il dominio di base con l'attributo estratto:
        `https://music.amazon.it` + `primary-href`

---

## 2. Gestione della Sessione Persistente

Per evitare di effettuare il login ad ogni avvio, utilizziamo un profilo browser persistente separato per Amazon Music.

*   **Directory del profilo:** `$XDG_DATA_HOME/browser-profiles/amazon-music` (default: `~/.local/share/browser-profiles/amazon-music`).
*   **Funzione da utilizzare:** `launch_persistent_context` di `cloakbrowser`.

### Avvio del Browser per Login Iniziale
Per effettuare il login manuale la prima volta e salvare la sessione:
```python
import os
from cloakbrowser import launch_persistent_context

profile_dir = os.path.join(os.environ.get('XDG_DATA_HOME', os.path.expanduser('~/.local/share')), 'browser-profiles', 'amazon-music')
context = launch_persistent_context(profile_dir, headless=False)
page = context.new_page()

# Naviga ad Amazon Music Italia
page.goto("https://music.amazon.it/")

# Attendere che l'utente effettui il login e prema invio in console prima di chiudere
input("Premi Invio per chiudere il browser dopo aver effettuato l'accesso...")
context.close()
```
*Uno script pronto all'uso è disponibile in `amazon-music/login.py`.*

---

## 3. Ricerca di un Brano o Contenuto

Per effettuare una ricerca su Amazon Music:
1. Attendere **7 secondi** dopo l'apertura della pagina per consentire il caricamento completo dell'interfaccia.
2. Fare focus sul campo di ricerca `#navbarSearchInput`.
3. Inserire la stringa di ricerca.
4. Premere Invio (`Enter`).
5. Attendere **4 secondi** per consentire il caricamento dei risultati.

### Esempio Python:
```python
# Attesa caricamento iniziale
page.wait_for_timeout(7000)

# Focus e inserimento query
search_input = page.locator("#navbarSearchInput")
search_input.focus()
search_input.fill("Pinguini Tattici Nucleari Rubami la Notte")
search_input.press("Enter")

# Attesa del caricamento dei risultati
page.wait_for_timeout(4000)
```

---

## 4. Navigazione dei Risultati (Shoveler, Vertical e Horizontal Items)

I risultati di ricerca e le varie sezioni sono organizzati all'interno di slider denominati `music-shoveler`.
*   L'attributo `primary-text` del tag `music-shoveler` indica la categoria dei risultati (es. "Risultati migliori", "Brani", "Album", "Artisti", "Playlist").

Gli elementi all'interno di ciascun shoveler cambiano a seconda del tipo di layout:

### A. Layout Orizzontale (`music-horizontal-item`)
Utilizzato per Risultati Migliori, Brani, ecc.
*   **Attributi principali:** `primary-text` (titolo/nome del brano), `secondary-text` (artista/autore), `primary-href` (contiene il parametro `trackAsin` per identificare la traccia specifica, es. `/albums/...?trackAsin=B0GZKYQZS6`).
*   **Pulsante Opzioni (Altro):** `<music-button slot="buttons" icon-name="more">`.

### B. Layout Verticale (`music-vertical-item`)
Utilizzato per Album, Artisti, Playlist, ecc.
*   **Attributi principali:** `primary-text` (titolo/nome), `secondary-text` (artista/autore), `primary-href`.
*   **Pulsante Opzioni (Altro):** `<music-button slot="rightButton" icon-name="more">`.

---

## 5. Esempio di Parsing dei Risultati

Ecco come scorrere gli shoveler ed estrarre i dati indipendentemente dal layout utilizzato:

```python
shovelers = page.query_selector_all("music-shoveler")

for shoveler in shovelers:
    shoveler_type = shoveler.get_attribute("primary-text")
    print(f"\n--- Sezione: {shoveler_type} ---")
    
    # 1. Cerca elementi orizzontali (es. Brani)
    h_items = shoveler.query_selector_all("music-horizontal-item")
    for item in h_items:
        title = item.get_attribute("primary-text")
        artist = item.get_attribute("secondary-text") or ""
        href = item.get_attribute("primary-href")
        print(f"[Orizzontale] {title} - {artist} (https://music.amazon.it{href})")
        
    # 2. Cerca elementi verticali (es. Album, Playlist)
    v_items = shoveler.query_selector_all("music-vertical-item")
    for item in v_items:
        title = item.get_attribute("primary-text")
        artist = item.get_attribute("secondary-text") or ""
        href = item.get_attribute("primary-href")
        print(f"[Verticale] {title} - {artist} (https://music.amazon.it{href})")
```
*Uno script pronto all'uso è disponibile in `amazon-music/test_search.py`.*

---

## 6. Interazione con il Pulsante Opzioni (Altro)

Per aprire il menu a tendina delle opzioni (per aggiunta a playlist, preferiti, ecc.) di un brano:

```python
def open_options_for_track(page, track_title):
    # Cerca prima tra gli elementi orizzontali (es. sotto 'Brani')
    item = page.query_selector(f"music-horizontal-item[primary-text='{track_title}']")
    button_selector = "music-button[slot='buttons']"
    
    # Se non trovato, cerca tra gli elementi verticali
    if not item:
        item = page.query_selector(f"music-vertical-item[primary-text='{track_title}']")
        button_selector = "music-button[slot='rightButton']"
        
    if item:
        more_btn = item.query_selector(button_selector)
        if more_btn:
            more_btn.click()
            page.wait_for_timeout(2000)
            print(f"Menu opzioni aperto per: {track_title}")
            return True
            
    print(f"Brano '{track_title}' non trovato.")
    return False
```

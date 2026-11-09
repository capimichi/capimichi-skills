# Spotify Public Search Skill

Questa guida descrive come cercare brani, album ed artisti pubblicamente su **Spotify** senza effettuare il login, utilizzando Playwright per effettuare lo scraping dei risultati.

---

## 1. Struttura degli URL di Ricerca

Per effettuare una ricerca su Spotify Web, l'URL pubblico ha questo formato:
```text
https://open.spotify.com/search/<query>
```
La query deve essere formattata sostituendo gli spazi con `%20` (o usando la codifica URL standard).

---

## 2. Elementi della Pagina e Selettori

Quando non si è autenticati, Spotify utilizza i seguenti elementi accessibili nel DOM:

### A. Brani (Tracks)
I singoli brani nei risultati di ricerca sono contenuti in elementi con ruolo `row`:
*   **Selettore Righe:** `[role="row"]`
*   **Filtro Brani:** Una riga è un brano se contiene un link a `/track/` (`a[href*="/track/"]`).
*   **Titolo del brano:** Il testo del link `a[href*="/track/"]`.
*   **Link del brano:** L'attributo `href` del link `a[href*="/track/"]`.
*   **Artisti:** Tutti i link all'interno della riga che puntano ad `/artist/` (`a[href*="/artist/"]`).

### B. Risultato più rilevante (Top Result)
*   **Selettore Card:** `[data-testid="top-result-card"]`
*   Contiene il link al brano, artista o album principale suggerito da Spotify.

### C. Album, Artisti e Playlist
Nelle griglie sottostanti, le card degli album o artisti hanno la seguente struttura:
*   **Contenitore Album:** Link con pattern `/album/` (`a[href*="/album/"]`).
*   **Contenitore Artisti:** Link con pattern `/artist/` (`a[href*="/artist/"]`).
*   **Contenitore Playlist:** Link con pattern `/playlist/` (`a[href*="/playlist/"]`).

---

## 3. Esecuzione tramite CloakBrowser

Per caricare l'interfaccia pubblica correttamente, usiamo `cloakbrowser` con un profilo dedicato ed in modalità headless (o visibile per debugging).

### Esempio Python di Scraping:
```python
import os
from cloakbrowser import launch_persistent_context

profile_dir = os.path.join(os.environ.get('XDG_DATA_HOME', os.path.expanduser('~/.local/share')), 'browser-profiles', 'spotify')
context = launch_persistent_context(profile_dir, headless=True)
page = context.new_page()

# Navigazione
query = "Sergio Mendes Funky Bahia"
url = f"https://open.spotify.com/search/{query.replace(' ', '%20')}"
page.goto(url)
page.wait_for_timeout(5000)

# Parsing dei brani
for row in page.locator("[role='row']").all():
    track_el = row.locator("a[href*='/track/']")
    if track_el.count() > 0:
        title = track_el.first.inner_text().strip()
        href = track_el.first.get_attribute("href")
        
        # Estrazione artisti
        artist_els = row.locator("a[href*='/artist/']").all()
        artists = [a.inner_text().strip() for a in artist_els]
        
        print(f"Brano: {title} | Artisti: {', '.join(artists)} | Link: https://open.spotify.com{href}")
```

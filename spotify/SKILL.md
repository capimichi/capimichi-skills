---
name: spotify
description: Ricerca pubblica e scraping di brani, album o artisti su Spotify (senza login) tramite interfaccia web e automazione browser.
---

# Spotify Public Search Skill

Questa guida descrive come cercare brani, album ed artisti pubblicamente su **Spotify** senza effettuare il login, utilizzando Playwright/CloakBrowser per effettuare lo scraping dei risultati.

---

## 🛠️ 1. Uso Rapido via CLI (`cli.py`)

La skill dispone di una CLI basata su **Click** posizionata nella root:

```bash
python3 $USER_SKILLS_DIR/spotify/cli.py search "<titolo artista o brano>"
```

### Opzioni utili:
* Output in JSON strutturato:
  ```bash
  python3 $USER_SKILLS_DIR/spotify/cli.py search "Sergio Mendes Funky Bahia" --json
  ```
* Debugging visivo con browser aperto:
  ```bash
  python3 $USER_SKILLS_DIR/spotify/cli.py search "Daft Punk" --headful
  ```

---

## 2. Struttura degli URL di Ricerca

Per effettuare una ricerca su Spotify Web, l'URL pubblico ha questo formato:
```text
https://open.spotify.com/search/<query>
```
La query viene codificata con `%20` per gli spazi.

---

## 3. Elementi della Pagina e Selettori

Quando non si è autenticati, Spotify utilizza i seguenti elementi accessibili nel DOM:

### A. Brani (Tracks)
I singoli brani nei risultati di ricerca sono contenuti in elementi con ruolo `row`:
* **Selettore Righe:** `[role="row"]`
* **Filtro Brani:** Una riga è un brano se contiene un link a `/track/` (`a[href*="/track/"]`).
* **Titolo del brano:** Il testo del link `a[href*="/track/"]`.
* **Link del brano:** L'attributo `href` del link `a[href*="/track/"]`.
* **Artisti:** Tutti i link all'interno della riga che puntano ad `/artist/` (`a[href*="/artist/"]`).

### B. Risultato più rilevante (Top Result)
* **Selettore Card:** `[data-testid="top-result-card"]`
* Contiene il link al brano, artista o album principale suggerito da Spotify.

### C. Album, Artisti e Playlist
Nelle griglie sottostanti, le card degli album o artisti hanno la seguente struttura:
* **Contenitore Album:** Link con pattern `/album/` (`a[href*="/album/"]`).
* **Contenitore Artisti:** Link con pattern `/artist/` (`a[href*="/artist/"]`).
* **Contenitore Playlist:** Link con pattern `/playlist/` (`a[href*="/playlist/"]`).

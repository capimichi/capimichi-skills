---
name: Stremio API Skill
description: Istruzioni su come autenticarsi con le API di Stremio, salvare i token in ~/.stremio-mcp e recuperare la libreria, film e serie TV viste con stagioni, episodi e progresso di visione.
---

# Stremio API Skill

Questa skill fornisce le istruzioni e gli strumenti per autenticarsi con le API di **Stremio** e recuperare la cronologia di visione, la libreria personale, le serie TV guardate (con stagioni ed episodi completati o in corso) e i film visti.

---

## 🔐 1. Configurazione e Credenziali

Le credenziali e il token di sessione (`authKey`) sono esposti tramite le variabili d'ambiente di sistema (gestite via Bitwarden e `.zshrc`):
- `STREMIO_AUTH_KEY`
- `STREMIO_EMAIL`

Negli script Python leggi direttamente la chiave da `os.environ["STREMIO_AUTH_KEY"]`.

---

## 🔑 2. Flusso di Autenticazione

Stremio utilizza un endpoint REST per l'autenticazione con email e password.

### Endpoint di Login:
* **Metodo:** `POST`
* **URL:** `https://api.strem.io/api/login`
* **Headers:** `Content-Type: application/json`, `User-Agent: Mozilla/5.0 ...`
* **Payload:**
  ```json
  {
    "email": "utente@example.com",
    "password": "tua_password"
  }
  ```

### Risposta:
```json
{
  "result": {
    "authKey": "8f3b...e21a",
    "user": {
      "_id": "...",
      "email": "utente@example.com"
    }
  }
}
```

> **Nota per Account Social (Google / Facebook):**
> Se l'utente accede tramite Google o Facebook, non può usare il login diretto via password. In questo caso l'utente può estrarre il proprio `authKey` da [web.stremio.com](https://web.stremio.com):
> 1. Aprire Developer Tools (`F12`) -> Scheda **Application** -> **Local Storage** -> `https://web.stremio.com`.
> 2. Copiare il valore della chiave `authKey`.
> 3. Salvarlo manualmente in `~/.stremio-mcp` oppure usare `python auth.py --token <chiave>`.

---

## 📡 3. Recupero Libreria e Cronologia (`datastoreGet`)

La libreria e la cronologia di visione sono memorizzate nella collection `library` del datastore Stremio.

### Endpoint:
* **Metodo:** `POST`
* **URL:** `https://api.strem.io/api/datastoreGet`
* **Payload:**
  ```json
  {
    "authKey": "YOUR_STREMIO_AUTH_KEY",
    "collection": "library"
  }
  ```

---

## 📊 4. Struttura dei Dati Restituiti

L'API restituisce una lista di oggetti media. Ogni oggetto contiene le informazioni generali e un sotto-oggetto `state` che traccia lo stato di visione:

### Schema di un Elemento:
* `_id`: ID univoco IMDb (es. `tt0903747`).
* `name`: Titolo del contenuto (es. `Breaking Bad` o `Inception`).
* `type`: Tipologia (`series` per serie TV, `movie` per film).
* `poster`: URL della locandina.
* `state`:
  * `lastWatched`: Data e ora dell'ultima visione in formato ISO 8601 (es. `2026-08-15T21:30:00.000Z`).
  * `timeWatched`: Millisecondi di visione raggiunti nell'ultimo video riprodotto.
  * `duration`: Durata totale del video in millisecondi.
  * `timesWatched`: Numero totale di volte in cui il contenuto/video è stato completato.
  * `video_id`: ID dell'ultimo video/episodio (per le serie TV ha formato `{imdb_id}:{season}:{episode}`, es. `tt0903747:3:5`).
  * `season`: Ultima stagione vista (numero intero).
  * `episode`: Ultimo episodio visto (numero intero).
  * `watched`: Stringa/hash interno che codifica lo storico degli episodi visti.

---

## 🎬 5. Distinzione tra Serie TV e Film

### Serie TV (`type == "series"`)
* **Ultimo Episodio Guardato:** Estratto da `state.season` e `state.episode` (o parsato da `state.video_id`).
* **Progresso:** `state.timeWatched` rispetto a `state.duration` (in percentuale).
* **Data Ultima Visione:** `state.lastWatched`.

### Film (`type == "movie"`)
* **Completato:** `state.timesWatched > 0` oppure percentuale di visione (`state.timeWatched / state.duration`) > 85%.
* **In Corso:** `state.timeWatched > 0` con percentuale < 85%.
* **Data Ultima Visione:** `state.lastWatched`.

---

## 🐍 6. Script di Supporto

Nella directory dello skill sono disponibili i seguenti script pronti all'uso:
* `auth.py`: Script per effettuare il login o salvare l'authKey in `~/.stremio-mcp`.
* `report_watched.py`: Script che legge `~/.stremio-mcp`, interroga l'API e genera un report dettagliato di Serie TV e Film (supporta opzioni `--type series`, `--type movie`, `--json`, `--csv`).

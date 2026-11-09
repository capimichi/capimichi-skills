---
name: Nuvio API Skill
description: Istruzioni su come autenticarsi con le API di Nuvio (backend Supabase), salvare i token in ~/.nuvio-mcp e recuperare la libreria, film e serie TV viste con stagioni, episodi e progresso.
---

# Nuvio API Skill

Questa skill fornisce le istruzioni e gli strumenti per autenticarsi con le API di **Nuvio** (basate su infrastruttura Supabase) e recuperare la cronologia di visione, la libreria personale, le serie TV (con dettaglio di stagioni ed episodi) e i film visti o in corso.

---

## 🔐 1. Configurazione e Credenziali

I token di sessione, la chiave API e le informazioni account sono esposti tramite le variabili d'ambiente di sistema (gestite via Bitwarden e `.zshrc`):
- `NUVIO_BASE_URL` (default: `https://api.nuvio.tv`)
- `NUVIO_API_KEY`
- `NUVIO_ACCESS_TOKEN`
- `NUVIO_REFRESH_TOKEN`
- `NUVIO_EMAIL`

Negli script Python leggi direttamente le variabili da `os.environ`.

*Nota: Se utilizzi un'istanza Nuvio self-hosted, il `base_url` corrisponderà al tuo dominio (es. `https://nuvio.tuodominio.com`).*

---

## 🔑 2. Flusso di Autenticazione (OAuth / Password Grant)

Nuvio utilizza l'infrastruttura Supabase Auth (`/auth/v1/`).

### A. Login Iniziale (Email e Password):
* **Metodo:** `POST`
* **URL:** `{base_url}/auth/v1/token?grant_type=password`
* **Headers:**
  * `apikey: {api_key}`
  * `Content-Type: application/json`
  * `User-Agent: Mozilla/5.0 ...`
* **Payload:**
  ```json
  {
    "email": "utente@example.com",
    "password": "tua_password"
  }
  ```
* **Risposta:** restituisce `access_token` (JWT), `refresh_token`, `expires_in` e le informazioni utente.

### B. Refresh del Token Scaduto:
* **Metodo:** `POST`
* **URL:** `{base_url}/auth/v1/token?grant_type=refresh_token`
* **Headers:**
  * `apikey: {api_key}`
  * `Content-Type: application/json`
* **Payload:**
  ```json
  {
    "refresh_token": "IL_TUO_REFRESH_TOKEN"
  }
  ```

---

## 📡 3. Endpoint API Principali (RPC & REST)

Tutte le richieste di lettura dati richiedono gli header:
```http
apikey: <api_key>
Authorization: Bearer <access_token>
Content-Type: application/json
User-Agent: Mozilla/5.0 ...
```

### 1. Elenco Profili Utente
* **Endpoint:** `POST {base_url}/rest/v1/rpc/sync_pull_profiles` (oppure `GET /rest/v1/profiles`)
* Permette di ottenere la lista dei profili associati all'account e il rispettivo `profile_id`.

### 2. Storico Elementi Visti (Watched Items)
* **Endpoint:** `POST {base_url}/rest/v1/rpc/sync_pull_watched_items`
* **Payload:**
  ```json
  {
    "profile_id": 0
  }
  ```
* Restituisce la cronologia degli episodi e film completati o registrati.

### 3. Progresso di Visione Corrente (Watch Progress / Continue Watching)
* **Endpoint:** `POST {base_url}/rest/v1/rpc/sync_pull_watch_progress`
* **Payload:**
  ```json
  {
    "profile_id": 0
  }
  ```
* Restituisce il punto esatto di riproduzione (secondi, percentuale, ultimo episodio avviato).

### 4. Libreria Personale (Saved / Bookmarked Items)
* **Endpoint:** `POST {base_url}/rest/v1/rpc/sync_pull_library`
* **Payload:**
  ```json
  {
    "profile_id": 0
  }
  ```

---

## 📊 4. Struttura dei Dati e Distinzione Contenuti

Gli oggetti restituiti da Nuvio contengono le seguenti informazioni chiave:

### Serie TV:
* `id` / `imdb_id` / `item_id`: Identificativo univoco (es. `tt0903747`).
* `title` / `name`: Nome della serie.
* `type`: `"series"` o `"tv"`.
* `season`: Numero della stagione.
* `episode`: Numero dell'episodio.
* `watched_at` / `last_watched`: Timestamp di visione.
* `time_offset` / `progress`: Avanzamento nella puntata.

### Film:
* `id` / `imdb_id`: Identificativo IMDb.
* `title` / `name`: Titolo del film.
* `type`: `"movie"`.
* `watched_at` / `last_watched`: Timestamp dell'ultima riproduzione.
* `progress` / `time_offset`: Progresso e percentuale di completamento.

---

## 🐍 5. Script di Supporto

Nella directory dello skill sono inclusi:
* `auth.py`: Script per eseguire il login con email/password, specificare server custom o importare un token di sessione esistente, salvando tutto in `~/.nuvio-mcp`.
* `report_watched.py`: Script che si occupa di rigenerare il token se scaduto, contattare gli endpoint RPC e produrre il report ordinato di Serie TV e Film (con opzioni `--type`, `--json`, `--csv`).

---
name: ticktick
description: "Gestisci, crea, visualizza, filtra, completa ed elimina attività e liste/progetti su TickTick tramite le Open API ufficiali (api.ticktick.com/open/v1) usando la CLI Python dedicata."
---

# TickTick Skill & CLI Suite

Questa skill fornisce all'agente le istruzioni, l'architettura delle credenziali e uno script CLI Python dedicato per gestire in modo autonomo attività, promemoria e liste/progetti sull'account **TickTick** dell'utente.

---

## 🔐 1. Credenziali & Variabili d'Ambiente

Le credenziali dell'account personale TickTick sono gestite tramite **chezmoi** sincronizzato con **Bitwarden**:

* **Item Bitwarden:** `"ticktick.com"` (ID: `a4415a3a-3795-4a01-ae6e-b501006a3492`)
* **Template Chezmoi:** `~/.local/share/chezmoi/private_dot_config/zsh/envs/personal.zsh.tmpl`
* **File d'ambiente generato:** `~/.config/zsh/envs/personal.zsh` (caricato da `.zshrc`)

### Variabili d'ambiente esportate:
| Variabile | Descrizione | Default / Valore |
| :--- | :--- | :--- |
| `TICKTICK_API_KEY` | Token Open API per TickTick | *(Estratto da Bitwarden)* |
| `TICKTICK_TOKEN` | Alias di `TICKTICK_API_KEY` | *(Stesso valore)* |
| `TICKTICK_API_TOKEN` | Alias di `TICKTICK_API_KEY` | *(Stesso valore)* |

> [!NOTE]
> Lo script CLI `ticktick_cli.py` legge automaticamente `TICKTICK_API_KEY` / `TICKTICK_TOKEN` dall'ambiente. Se la variabile non è presente nella shell corrente, effettua un fallback automatico leggendola direttamente da `~/.config/zsh/envs/personal.zsh`.

---

## 🛠️ 2. Script CLI

Lo script principale si trova in:
```bash
/Users/michele/workspace/capimichi-skills/ticktick/scripts/ticktick_cli.py
```

Può essere eseguito sia con `python3` che con `uv run` o direttamente come binario eseguibile.

---

## 📋 3. Riferimento Comandi CLI

### 1. Elenco Liste e Progetti
```bash
python3 /Users/michele/workspace/capimichi-skills/ticktick/scripts/ticktick_cli.py lists
# oppure con output JSON strutturato
python3 /Users/michele/workspace/capimichi-skills/ticktick/scripts/ticktick_cli.py lists --json
```

### 2. Visualizzare le Attività
```bash
# Mostra le attività attive su tutte le liste
python3 /Users/michele/workspace/capimichi-skills/ticktick/scripts/ticktick_cli.py tasks

# Filtra per una specifica lista (per nome o per ID)
python3 /Users/michele/workspace/capimichi-skills/ticktick/scripts/ticktick_cli.py tasks --list "Memo"

# Mostra sia le attività completate che quelle attive
python3 /Users/michele/workspace/capimichi-skills/ticktick/scripts/ticktick_cli.py tasks --all

# Mostra solo le attività completate
python3 /Users/michele/workspace/capimichi-skills/ticktick/scripts/ticktick_cli.py tasks --completed

# Output JSON completo
python3 /Users/michele/workspace/capimichi-skills/ticktick/scripts/ticktick_cli.py tasks --list "Memo" --json
```

### 3. Creare una Nuova Attività
```bash
# Attività semplice
python3 /Users/michele/workspace/capimichi-skills/ticktick/scripts/ticktick_cli.py add "Comprare il latte"

# Con lista, scadenza, orario, priorità e promemoria
python3 /Users/michele/workspace/capimichi-skills/ticktick/scripts/ticktick_cli.py add "Riunione marketing" \
  --list "Memo" \
  --due "domani 15:30" \
  --remind "0,15" \
  --priority 3 \
  --notes "Discutere il budget Q1 e nuovi canali"
```

#### Opzioni supportate per `add`:
* `--list`, `-l`: Nome o ID del progetto (es. `Memo`). Se omesso, usa la prima lista disponibile.
* `--due`, `-d`: Data/ora di scadenza. Supporta espressioni naturali:
  * Relativi: `today`, `tomorrow`, `oggi`, `domani`, `+2d`
  * Orari specifici: `oggi 18:00`, `domani 09:30`, `15:45`
  * Formato data: `YYYY-MM-DD`, `YYYY-MM-DD HH:MM`
* `--all-day`: Imposta l'attività per tutta la giornata senza un'ora specifica.
* `--priority`, `-p`: Livello di priorità (`0` = Nessuna, `1` = Bassa, `3` = Media, `5` = Alta).
* `--remind`, `-r`: Promemoria automatici (es. `0` all'orario esatto, `15` per 15 min prima, oppure multipli `0,15`).
* `--notes`, `-n`: Note o descrizione testuale dell'attività.

### 4. Completare un'Attività
```bash
python3 /Users/michele/workspace/capimichi-skills/ticktick/scripts/ticktick_cli.py done <task_id>
```

### 5. Eliminare un'Attività
```bash
python3 /Users/michele/workspace/capimichi-skills/ticktick/scripts/ticktick_cli.py delete <task_id>
```

### 6. Gestire Liste e Progetti
```bash
# Creare una nuova lista
python3 /Users/michele/workspace/capimichi-skills/ticktick/scripts/ticktick_cli.py add-list "Progetti Lavoro" --view-mode list

# Eliminare una lista per nome o ID
python3 /Users/michele/workspace/capimichi-skills/ticktick/scripts/ticktick_cli.py delete-list "Progetti Lavoro"
```

---

## 🌐 4. Dettagli Open API TickTick

Per chiamate HTTP dirette (es. tramite `curl` o librerie esterne):
* **Base URL:** `https://api.ticktick.com/open/v1`
* **Header Autenticazione:** `Authorization: Bearer $TICKTICK_API_KEY`
* **Content-Type:** `application/json`

Endpoint principali:
* `GET /open/v1/project` — Elenco progetti
* `GET /open/v1/project/{id}/data` — Dati e attività di un progetto
* `POST /open/v1/task` — Creazione attività
* `POST /open/v1/project/{projectId}/task/{taskId}/complete` — Completamento attività
* `DELETE /open/v1/project/{projectId}/task/{taskId}` — Eliminazione attività

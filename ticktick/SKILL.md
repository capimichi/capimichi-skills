---
name: ticktick
description: "Gestisci, crea, visualizza, filtra, completa ed elimina attività e liste/progetti su TickTick tramite le Open API ufficiali (api.ticktick.com/open/v1) usando la CLI Python dedicata."
---

# TickTick Skill & CLI Suite

Questa skill permette di interagire con le Open API di **TickTick** per gestire attività, scadenze, promemoria e liste/progetti tramite uno script CLI Python dedicato.

---

## 🔐 1. Prerequisiti & Variabili d'Ambiente

La skill è completamente agnostica rispetto a come le variabili d'ambiente vengono generate o salvate. Richiede unicamente:

| Variabile | Descrizione | Obbligatoria |
| :--- | :--- | :--- |
| `TICKTICK_APIKEY` | Token di autenticazione per le Open API di TickTick | **Sì** |
| `USER_SKILLS_DIR` | Percorso radice del repository delle skill | **Sì** |

> [!NOTE]
> Se `TICKTICK_APIKEY` non è valorizzata, la CLI verificherà anche `TICKTICK_API_KEY` come fallback.

---

## 🛠️ 2. CLI Helper

Lo script CLI si trova all'interno della cartella della skill:
```bash
$USER_SKILLS_DIR/ticktick/scripts/ticktick_cli.py
```

Tutti i comandi possono essere eseguiti invocando:
```bash
python3 "$USER_SKILLS_DIR/ticktick/scripts/ticktick_cli.py" <comando> [opzioni]
```

---

## 📋 3. Riferimento Comandi CLI

### 1. Elenco Liste e Progetti
Include per impostazione predefinita la cartella speciale **Inbox** oltre alle liste create dall'utente:
```bash
python3 "$USER_SKILLS_DIR/ticktick/scripts/ticktick_cli.py" lists
# oppure con output JSON strutturato
python3 "$USER_SKILLS_DIR/ticktick/scripts/ticktick_cli.py" lists --json
```

### 2. Visualizzare le Attività
```bash
# Mostra le attività attive su tutte le liste
python3 "$USER_SKILLS_DIR/ticktick/scripts/ticktick_cli.py" tasks

# Filtra per una specifica lista (per nome o per ID)
python3 "$USER_SKILLS_DIR/ticktick/scripts/ticktick_cli.py" tasks --list "Memo"

# Mostra sia le attività completate che quelle attive
python3 "$USER_SKILLS_DIR/ticktick/scripts/ticktick_cli.py" tasks --all

# Mostra solo le attività completate
python3 "$USER_SKILLS_DIR/ticktick/scripts/ticktick_cli.py" tasks --completed

# Output JSON completo
python3 "$USER_SKILLS_DIR/ticktick/scripts/ticktick_cli.py" tasks --list "Memo" --json
```

### 3. Creare una Nuova Attività
Se la lista non viene specificata con `--list`, l'attività viene inserita automaticamente in **Inbox**:
```bash
# Attività rapida in Inbox
python3 "$USER_SKILLS_DIR/ticktick/scripts/ticktick_cli.py" add "Comprare il latte"

# Con lista, scadenza, orario, priorità e promemoria
python3 "$USER_SKILLS_DIR/ticktick/scripts/ticktick_cli.py" add "Riunione marketing" \
  --list "Memo" \
  --due "domani 15:30" \
  --remind "0,15" \
  --priority 3 \
  --notes "Discutere il budget Q1 e nuovi canali"
```

#### Opzioni supportate per `add`:
* `--list`, `-l`: Nome o ID del progetto (default: `Inbox`).
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
python3 "$USER_SKILLS_DIR/ticktick/scripts/ticktick_cli.py" done <task_id>
```

### 5. Eliminare un'Attività
```bash
python3 "$USER_SKILLS_DIR/ticktick/scripts/ticktick_cli.py" delete <task_id>
```

### 6. Gestire Liste e Progetti
```bash
# Creare una nuova lista
python3 "$USER_SKILLS_DIR/ticktick/scripts/ticktick_cli.py" add-list "Progetti 2026" --view-mode list

# Eliminare una lista per nome o ID (richiede corrispondenza esatta)
python3 "$USER_SKILLS_DIR/ticktick/scripts/ticktick_cli.py" delete-list "Progetti 2026"
```

---

## 🌐 4. Dettagli Open API TickTick

Per chiamate HTTP dirette (es. tramite `curl` o script personalizzati):
* **Base URL:** `https://api.ticktick.com/open/v1`
* **Header Autenticazione:** `Authorization: Bearer $TICKTICK_APIKEY`
* **Content-Type:** `application/json`

Endpoint principali:
* `GET /open/v1/project` — Elenco progetti
* `GET /open/v1/project/{id}/data` — Dati e attività di un progetto
* `POST /open/v1/task` — Creazione attività
* `POST /open/v1/project/{projectId}/task/{taskId}/complete` — Completamento attività
* `DELETE /open/v1/project/{projectId}/task/{taskId}` — Eliminazione attività

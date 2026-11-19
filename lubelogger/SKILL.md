---
name: lubelogger
description: Gestione veicoli personali, chilometraggio, tagliandi, manutenzione, rifornimenti, scadenze e note tramite API LubeLogger.
---

# LubeLogger Skill

Interfaccia di automazione e gestione completa per la propria istanza self-hosted di **LubeLogger** (`https://lubelogger.michelecapicchioni.com`).
Permette di consultare e aggiornare le auto nel garage, registrare tagliandi e manutenzioni, aggiornare il chilometraggio, tracciare i rifornimenti di carburante, impostare promemoria e scadenze (bollo, revisione, assicurazione) e salvare note tecniche.

---

## 🔐 Configurazione & Variabili d'Ambiente

La skill legge le credenziali direttamente dall'ambiente di sistema (es. esportate da `~/.config/zsh/envs/personal.zsh`).

| Variabile d'Ambiente | Obbligatoria | Descrizione | Default |
| :--- | :--- | :--- | :--- |
| **`LUBELOGGER_API_KEY`** (o `LUBELOGGER_APIKEY`) | **Sì** | API Key generata dall'interfaccia LubeLogger (*Profilo utente ➔ Manage API Keys*) | - |
| **`LUBELOGGER_URL`** (o `LUBELOGGER_BASE_URL`) | No | URL base dell'istanza LubeLogger | `https://lubelogger.michelecapicchioni.com` |

---

## 🚀 Script CLI e Utilizzo

La skill dispone di una CLI unificata basata su **Click** posizionata in `$USER_SKILLS_DIR/lubelogger/cli.py`:

```bash
python3 $USER_SKILLS_DIR/lubelogger/cli.py <gruppo> <comando> [opzioni]
```

### 1. Gestione Veicoli (`vehicles`)
```bash
# Elenca tutti i veicoli presenti nel garage con relativi ID e targhe
python3 $USER_SKILLS_DIR/lubelogger/cli.py vehicles list

# Dettagli completi di un veicolo
python3 $USER_SKILLS_DIR/lubelogger/cli.py vehicles info --id 1

# Aggiungi un nuovo veicolo
python3 $USER_SKILLS_DIR/lubelogger/cli.py vehicles add \
  --year 2021 \
  --make "Volkswagen" \
  --model "Golf" \
  --plate "AB123CD" \
  --fuel "Diesel"
```

### 2. Chilometri / Odometro (`odometer`)
```bash
# Mostra l'ultimo chilometraggio registrato per il veicolo ID 1
python3 $USER_SKILLS_DIR/lubelogger/cli.py odometer latest --vehicle-id 1

# Elenco storico di tutte le letture chilometriche
python3 $USER_SKILLS_DIR/lubelogger/cli.py odometer list --vehicle-id 1

# Registra una nuova lettura del contachilometri (default data odierna)
python3 $USER_SKILLS_DIR/lubelogger/cli.py odometer add \
  --vehicle-id 1 \
  --km 124500 \
  --notes "Controllo mensile"
```

### 3. Tagliandi e Manutenzioni (`services`)
```bash
# Elenco di tutti i tagliandi e interventi eseguiti
python3 $USER_SKILLS_DIR/lubelogger/cli.py services list --vehicle-id 1

# Registra un nuovo tagliando / manutenzione
python3 $USER_SKILLS_DIR/lubelogger/cli.py services add \
  --vehicle-id 1 \
  --km 120000 \
  --desc "Tagliando completo (olio, filtri, candele)" \
  --cost 280.00 \
  --tag tagliando --tag olio \
  --notes "Eseguito da officina Rossi"
```

### 4. Rifornimenti Carburante (`gas`)
```bash
# Elenco rifornimenti carburante
python3 $USER_SKILLS_DIR/lubelogger/cli.py gas list --vehicle-id 1

# Registra un rifornimento di carburante (pieno)
python3 $USER_SKILLS_DIR/lubelogger/cli.py gas add \
  --vehicle-id 1 \
  --km 124200 \
  --liters 45.5 \
  --cost 78.50 \
  --notes "Eni Station"
```

### 5. Promemoria e Scadenze (`reminders`)
```bash
# Visualizza scadenze attive (revisione ministeriale, bollo, tagliando programmato)
python3 $USER_SKILLS_DIR/lubelogger/cli.py reminders list --vehicle-id 1
```

### 6. Note e Diario di Bordo (`notes`)
```bash
# Visualizza le note salvate per il veicolo
python3 $USER_SKILLS_DIR/lubelogger/cli.py notes list --vehicle-id 1

# Aggiungi una nota (supporta formattazione Markdown)
python3 $USER_SKILLS_DIR/lubelogger/cli.py notes add \
  --vehicle-id 1 \
  --title "Specifiche pneumatici e ricambi" \
  --text "Gomme estive: 205/55 R16 91V\nGomme invernali: 195/65 R15 91T\nOlio motore: 5W-30 Longlife" \
  --pin
```

---

## 🐍 Utilizzo da Modulo Python (`client.py`)

```python
import os
import sys
from pathlib import Path

# Import conforme a ADD_SKILL_RULES.md
skills_dir = os.environ.get("USER_SKILLS_DIR", str(Path.home() / "workspace/capimichi-skills"))
sys.path.insert(0, str(Path(skills_dir) / "lubelogger"))

from client import LubeLoggerClient

client = LubeLoggerClient()

# Ottieni l'elenco veicoli
vehicles = client.get_vehicles()

# Registra un tagliando
client.add_service_record(
    vehicle_id=1,
    date="2026-11-14",
    mileage=120000,
    description="Cambio pastiglie freni anteriori",
    cost=140.00,
    notes="Brembo P 85 020"
)
```

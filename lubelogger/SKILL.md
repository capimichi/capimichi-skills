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

Tutti i comandi usano la variabile d'ambiente standard `$USER_SKILLS_DIR`.

### 1. Gestione Veicoli (`manage_vehicles.py`)
```bash
# Elenca tutti i veicoli presenti nel garage con relativi ID e targhe
python3 $USER_SKILLS_DIR/lubelogger/manage_vehicles.py list

# Dettagli completi di un veicolo
python3 $USER_SKILLS_DIR/lubelogger/manage_vehicles.py info --id 1

# Aggiungi un nuovo veicolo
python3 $USER_SKILLS_DIR/lubelogger/manage_vehicles.py add \
  --year 2021 \
  --make "Volkswagen" \
  --model "Golf" \
  --plate "AB123CD" \
  --fuel "Diesel"
```

### 2. Chilometri / Odometro (`manage_odometer.py`)
```bash
# Mostra l'ultimo chilometraggio registrato per il veicolo ID 1
python3 $USER_SKILLS_DIR/lubelogger/manage_odometer.py latest --vehicle-id 1

# Elenco storico di tutte le letture chilometriche
python3 $USER_SKILLS_DIR/lubelogger/manage_odometer.py list --vehicle-id 1

# Registra una nuova lettura del contachilometri (default data odierna)
python3 $USER_SKILLS_DIR/lubelogger/manage_odometer.py add \
  --vehicle-id 1 \
  --km 124500 \
  --notes "Controllo mensile"
```

### 3. Tagliandi e Manutenzioni (`manage_services.py`)
```bash
# Elenco di tutti i tagliandi e interventi eseguiti
python3 $USER_SKILLS_DIR/lubelogger/manage_services.py list --vehicle-id 1

# Registra un nuovo tagliando / manutenzione
python3 $USER_SKILLS_DIR/lubelogger/manage_services.py add \
  --vehicle-id 1 \
  --km 120000 \
  --desc "Tagliando completo (olio, filtri, candele)" \
  --cost 280.00 \
  --tags tagliando olio filtri \
  --notes "Eseguito da officina Rossi"
```

### 4. Rifornimenti Carburante (`manage_gas.py`)
```bash
# Elenco rifornimenti carburante
python3 $USER_SKILLS_DIR/lubelogger/manage_gas.py list --vehicle-id 1

# Registra un rifornimento di carburante (pieno)
python3 $USER_SKILLS_DIR/lubelogger/manage_gas.py add \
  --vehicle-id 1 \
  --km 124200 \
  --liters 45.5 \
  --cost 78.50 \
  --notes "Eni Station"
```

### 5. Promemoria e Scadenze (`manage_reminders.py`)
```bash
# Visualizza scadenze attive (revisione ministeriale, bollo, tagliando programmato)
python3 $USER_SKILLS_DIR/lubelogger/manage_reminders.py --vehicle-id 1
```

### 6. Note e Diario di Bordo (`manage_notes.py`)
```bash
# Visualizza le note salvate per il veicolo
python3 $USER_SKILLS_DIR/lubelogger/manage_notes.py list --vehicle-id 1

# Aggiungi una nota (supporta formattazione Markdown)
python3 $USER_SKILLS_DIR/lubelogger/manage_notes.py add \
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

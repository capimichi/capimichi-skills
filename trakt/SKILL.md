---
name: trakt
description: Sincronizzazione visioni, scrobbling e tracciamento film/serie su Trakt.tv da Nuvio.
---

# Trakt API & Sync Skill

Questa skill fornisce gli strumenti per autenticarsi con le API di **Trakt.tv** e sincronizzare automaticamente la cronologia di visione dei film e delle serie TV da Nuvio.

---

## 🛠️ 1. Utilizzo CLI Unificata (`cli.py`)

La skill dispone di una CLI unificata basata su **Click** posizionata in `$USER_SKILLS_DIR/trakt/cli.py`:

### A. Sincronizzazione da Nuvio a Trakt
Estrae le serie TV e i film guardati di recente su Nuvio e li invia a Trakt.tv:

```bash
# Sincronizzazione standard (ultimi 31 giorni)
python3 $USER_SKILLS_DIR/trakt/cli.py sync

# Simula l'operazione senza inviare modifiche (Dry-Run)
python3 $USER_SKILLS_DIR/trakt/cli.py sync --dry-run

# Specifica finestra temporale (es. ultimi 60 giorni) e soglia minima di progresso
python3 $USER_SKILLS_DIR/trakt/cli.py sync --days 60 --min-progress 75.0
```

### B. Autenticazione OAuth (PIN)
```bash
# Mostra il link per ottenere il codice PIN
python3 $USER_SKILLS_DIR/trakt/cli.py auth

# Scambia il PIN con i token di accesso
python3 $USER_SKILLS_DIR/trakt/cli.py auth --pin <CODICE_PIN>
```

---

## 🔐 2. Credenziali & Variabili d'Ambiente

Le credenziali e i token di accesso sono esposti tramite le variabili d'ambiente di sistema:
* `TRAKT_CLIENT_ID`
* `TRAKT_CLIENT_SECRET`
* `TRAKT_ACCESS_TOKEN`
* `TRAKT_REFRESH_TOKEN`

Per la sincronizzazione da Nuvio, sono necessarie anche:
* `NUVIO_ACCESS_TOKEN`
* `NUVIO_API_KEY`
* `NUVIO_BASE_URL`

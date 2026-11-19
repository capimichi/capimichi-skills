---
name: ibkr
description: Consultazione portafoglio Interactive Brokers (IBKR), posizioni aperte, saldo liquidità, conto e ordini/eseguiti recenti in sola lettura via Web API / Client Portal Gateway.
---

# Interactive Brokers (IBKR) Skill

Integrazione per la consultazione del proprio conto e portafoglio **Interactive Brokers** tramite le Web API ufficiali (Client Portal Gateway - CPGW) in modalità **sola lettura**.

Permette di:
* Monitorare il valore netto del portafoglio (Net Liquidation Value / NAV).
* Verificare la liquidità totale, il contante regolato e il potere d'acquisto (Buying Power).
* Elencare le posizioni aperte (azioni, ETF, obbligazioni, opzioni) con quote, prezzi medi, valori di mercato e PnL non realizzato.
* Consultare i saldi di cassa suddivisi per valuta (EUR, USD, ecc.).
* Verificare gli eseguiti e i trade recenti.

---

## 🏗️ Architettura & Standard XDG (Docker vs Nativo)

Interactive Brokers espone le Web API tramite un gateway locale (**Client Portal Gateway** o `cpgw`).
Il gateway fa da proxy sicuro verso i server IBKR e mantiene attiva la sessione autenticata (confermando il 2FA tramite IB Key su smartphone).

Tutti i file sono memorizzati secondo le specifiche **XDG Base Directory**:
* **File di configurazione e Docker Compose**: `$XDG_CONFIG_HOME/ibkr/docker/` (default: `~/.config/ibkr/docker/`)
  * `docker-compose.yml`
  * `Dockerfile`
  * `conf.yaml` (con whitelist per bridge Docker già configurata per evitare *Access Denied*)
* **Dati e runtime persistenti / log**: `$XDG_DATA_HOME/ibkr/` (default: `~/.local/share/ibkr/`)

---

## 🔐 Configurazione & Variabili d'Ambiente

La skill legge le impostazioni dall'ambiente di sistema (es. esportate in `~/.config/zsh/envs/personal.zsh` o nella sessione shell corrente):

| Variabile d'Ambiente | Obbligatoria | Descrizione | Default |
| :--- | :--- | :--- | :--- |
| **`IBKR_GATEWAY_URL`** | No | URL base del Client Portal Gateway locale | `https://localhost:5001` |
| **`IBKR_ACCOUNT_ID`** | No | ID del conto predefinito (es. `U1234567`). Se omesso, viene risolto automaticamente il primo conto disponibile | Primo conto rilevato |
| **`IBKR_SSL_VERIFY`** | No | Verifica certificato SSL (impostare a `false` per il certificato autofirmato di CPGW) | `false` |

---

## 🚀 Avvio del Gateway & Autenticazione 2FA

Prima di interrogare le API via CLI, il Gateway deve essere avviato e autenticato:

### 1. Avvio con Docker (Raccomandato)
Assicurati che Docker sia attivo (se usi Colima: `colima start`).
```bash
# Avvia il container IBKR Gateway in background da ~/.config/ibkr/docker
bash $USER_SKILLS_DIR/ibkr/run_gateway.sh docker
```
*(In alternativa, puoi arrestarlo quando hai finito con `bash $USER_SKILLS_DIR/ibkr/run_gateway.sh stop`)*.

### 2. Alternativa: Avvio Nativo (Java)
Se preferisci non usare Docker, lo script scarica ed esegue il Gateway direttamente in `$XDG_DATA_HOME/ibkr/gateway` (default `~/.local/share/ibkr/gateway`) su porta 5001:
```bash
bash $USER_SKILLS_DIR/ibkr/run_gateway.sh native
```

### 3. Autenticazione (Una volta al giorno / a sessione)
1. Apri nel browser: **`https://localhost:5001`**
   *(Accetta l'avviso di sicurezza del browser per il certificato self-signed locale)*.
2. Inserisci il tuo **Username** e **Password** di Interactive Brokers.
3. Conferma la notifica **2FA** sull'app IBKR Mobile (IB Key) del tuo smartphone.
4. Quando il browser conferma l'accesso (*"Client login succeeded"*), la sessione è attiva.

---

## 📊 Utilizzo Script CLI (`cli.py`)

La skill dispone di una CLI unificata basata su **Click** posizionata in `$USER_SKILLS_DIR/ibkr/cli.py`.
Tutti i comandi supportano il flag opzionale `--json` per ottenere l'output grezzo (ideale per elaborazioni programmatiche o agenti AI).

### 1. Verifica Stato e Sessione
```bash
python3 $USER_SKILLS_DIR/ibkr/cli.py status
```
Mostra se il Gateway è raggiungibile, connesso a IBKR e se la sessione utente è autenticata.

### 2. Elenco Conti
```bash
python3 $USER_SKILLS_DIR/ibkr/cli.py accounts
```

### 3. Riepilogo Finanziario (NAV, Liquidità, PnL)
```bash
# Riepilogo del conto predefinito
python3 $USER_SKILLS_DIR/ibkr/cli.py summary

# Per un conto specifico
python3 $USER_SKILLS_DIR/ibkr/cli.py summary --account U1234567
```

### 4. Posizioni Aperte in Portafoglio
```bash
# Mostra la tabella completa delle posizioni (ticker, quote, prezzi, PnL)
python3 $USER_SKILLS_DIR/ibkr/cli.py positions

# In formato JSON
python3 $USER_SKILLS_DIR/ibkr/cli.py positions --json
```

### 5. Saldi di Cassa per Valuta (Ledger)
```bash
python3 $USER_SKILLS_DIR/ibkr/cli.py ledger
```

### 6. Eseguiti e Transazioni Recenti
```bash
python3 $USER_SKILLS_DIR/ibkr/cli.py trades
```

### 7. Keep-Alive Ping (Tickle)
```bash
# Invia un ping per mantenere viva la sessione attiva
python3 $USER_SKILLS_DIR/ibkr/cli.py tickle
```

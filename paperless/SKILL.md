---
name: paperless
description: "Interroga, cerca documenti, estrae testo OCR, scarica e carica file sull'istanza Paperless-ngx dell'utente (https://paperless.michelecapicchioni.com) tramite API e script Python dedicati."
---

# Paperless-ngx Skill & Operational Suite

Questa skill fornisce all'agente le istruzioni, l'architettura delle credenziali e un set completo di script CLI e client Python per interrogare e gestire in modo autonomo l'istanza **Paperless-ngx** dell'utente (`https://paperless.michelecapicchioni.com`).

---

## 🔐 1. Configurazione & Variabili d'Ambiente

L'istanza e le credenziali di Paperless-ngx sono gestite tramite le variabili d'ambiente di sistema:

* **File d'ambiente di shell:** `~/.config/zsh/envs/personal.zsh` (o `.zshrc`)

### Variabili d'ambiente esportate:
| Variabile | Descrizione | Default / Valore |
| :--- | :--- | :--- |
| `PAPERLESS_BASE_URL` (o `PAPERLESS_URL`) | URL base dell'istanza Paperless | `https://paperless.michelecapicchioni.com` |
| `PAPERLESS_API_KEY` (o `PAPERLESS_TOKEN`) | API Auth Token per l'utente | *(Token da ambiente)* |

All'interno di tutti gli script della cartella `paperless/`, la classe `PaperlessClient` legge automaticamente queste variabili d'ambiente. Se per qualsiasi motivo non fossero presenti nella shell corrente, è sufficiente eseguire:
```bash
source ~/.config/zsh/envs/personal.zsh
```

---

## 🛡️ 2. Requisito Fondamentale: Bypass Cloudflare / WAF

L'istanza Paperless è protetta dietro Cloudflare. Tutte le richieste HTTP **DEVONO** obbligatoriamente includere uno `User-Agent` che simuli un browser reale, altrimenti Cloudflare bloccherà la richiesta con HTTP `403 Forbidden` / `Error 1010`:

```python
headers = {
    "Authorization": f"Token {api_key}",
    "Accept": "application/json",
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}
```
*(Questo comportamento è già integrato e gestito automaticamente in tutti gli script forniti).*

---

## 🛠️ 3. CLI Helper Unificata (`cli.py`)

La skill dispone di una CLI unificata basata su **Click** posizionata in `$USER_SKILLS_DIR/paperless/cli.py`:

### A. Ricerca Documenti (`search`)
Esegue ricerche full-text nel testo OCR e nei titoli, con supporto a filtri per mittente, tag, tipo documento o anno:

```bash
# Ricerca full-text semplice
python3 $USER_SKILLS_DIR/paperless/cli.py search "bolletta aass"

# Filtrare per mittente (es. AASS) e anno
python3 $USER_SKILLS_DIR/paperless/cli.py search -c AASS -y 2026

# Filtrare per tag specifici
python3 $USER_SKILLS_DIR/paperless/cli.py search -t bolletta -t elettricita

# Mostrare uno snippet del testo OCR nei risultati
python3 $USER_SKILLS_DIR/paperless/cli.py search -c AASS -n 5 --content

# Output in JSON grezzo (utile per parsing programmatico)
python3 $USER_SKILLS_DIR/paperless/cli.py search "stipendio" --json
```

### B. Dettagli e Testo OCR (`get`)
Mostra tutte le informazioni, metadati, note e il contenuto testuale OCR estratto da un singolo documento:

```bash
# Metadati documento
python3 $USER_SKILLS_DIR/paperless/cli.py get 1023

# Stampa a video l'intero testo OCR estratto (pronto per analisi LLM)
python3 $USER_SKILLS_DIR/paperless/cli.py get 1023

# Escludi il testo OCR (solo metadati)
python3 $USER_SKILLS_DIR/paperless/cli.py get 1023 --no-content

# Output JSON completo
python3 $USER_SKILLS_DIR/paperless/cli.py get 1023 --json
```

### C. Download Documenti (`download`)
Scarica il file (PDF originale o PDF processato/archiviato):

```bash
# Scarica la versione archiviata
python3 $USER_SKILLS_DIR/paperless/cli.py download 1023 -o /tmp/bolletta.pdf

# Scarica il file originale caricato
python3 $USER_SKILLS_DIR/paperless/cli.py download 1023 --original -o ~/Downloads/
```

### D. Upload Documenti con Auto-Riparazione (`upload`)
Invia nuovi documenti all'istanza Paperless per l'elaborazione OCR automatica.
Include una funzione di verifica preventiva e riparazione dei PDF con `qpdf` per prevenire errori di elaborazione:

```bash
# Upload semplice
python3 $USER_SKILLS_DIR/paperless/cli.py upload /percorso/fattura.pdf

# Upload specificando titolo, mittente, tipo e tag
python3 $USER_SKILLS_DIR/paperless/cli.py upload /percorso/fattura.pdf \
  -t "Fattura Luce Novembre 2026" \
  -c "AASS" \
  --type "Fattura" \
  --tag "bolletta" --tag "luce" \
  --created 2026-11-01
```

### E. Consultazione e Gestione Metadati (`metadata`)
Visualizza mittenti (corrispondenti), tag e tipi di documento esistenti:

```bash
# Visualizza tutti i tag e corrispondenti
python3 $USER_SKILLS_DIR/paperless/cli.py metadata

# Visualizza solo corrispondenti o solo tag
python3 $USER_SKILLS_DIR/paperless/cli.py metadata --type correspondents
python3 $USER_SKILLS_DIR/paperless/cli.py metadata --type tags
python3 $USER_SKILLS_DIR/paperless/cli.py metadata --json
```

---

## 🐍 4. Utilizzo Programmatico con Python (`client.py`)

Se all'agente occorre eseguire query avanzate o comporre logiche complesse, può importare e usare direttamente `PaperlessClient`:

```python
import sys
sys.path.insert(0, "$USER_SKILLS_DIR")
from paperless.client import PaperlessClient

client = PaperlessClient()

# Ricerca (risolve automaticamente nomi in ID)
results = client.search_documents(
    query="energia elettrica",
    correspondent="AASS",
    year=2026,
    page_size=5
)

for doc in results.get("results", []):
    print(doc["id"], doc["title"])
    # Lettura testo OCR
    ocr_text = doc.get("content", "")
```

---

## 🔧 5. Gestione PDF Corrotti / Danneggiati (`qpdf`)

Se Paperless restituisce errori in fase di ingestione (es. `ValueError: max_workers must be greater than 0` dovuto a tabelle `xref` corrotte):

1. **Verifica:**
   ```bash
   qpdf --check percorso/file.pdf
   ```
2. **Riparazione manuale (se non usi `upload_document.py`):**
   ```bash
   qpdf percorso/file.pdf percorso/file_riparato.pdf
   ```
   *(Nota: exit code 0 o 3 indica che il file è stato riparato).*
3. Lo script `upload_document.py` esegue questo controllo e auto-riparazione in automatico prima di inviare il file all'API.

---

## 💡 6. Workflow per l'Agente quando l'Utente pone domande

Quando l'utente chiede informazioni su documenti o fatture (es. *"Quanto ho speso di luce nelle ultime bollette AASS?"* oppure *"Trova la ricevuta del tagliando"*):

1. Esegui `python3 $USER_SKILLS_DIR/paperless/cli.py search -c AASS --content -n 5` o `python3 $USER_SKILLS_DIR/paperless/cli.py get <id>`.
2. Analizza l'output OCR per estrarre date, importi, scadenze o dettagli contrattuali.
3. Rispondi all'utente citando il titolo del documento, la data e l'ID corrispondente per trasparenza.

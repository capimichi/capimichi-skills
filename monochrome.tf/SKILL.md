# Monochrome.tf Downloader Automation with CloakBrowser

Questa skill consente di automatizzare la ricerca e il download di album musicali ad alta qualità da **Monochrome.tf** (https://monochrome.tf/) utilizzando Python e **CloakBrowser**.

---

## 1. Informazioni Generali e URL di Base

*   **URL del Servizio:** `https://monochrome.tf/`
*   **Directory del profilo:** `$XDG_DATA_HOME/browser-profiles/monochrome` (default: `~/.local/share/browser-profiles/monochrome`).
*   **Directory di download predefinita:** `~/Downloads`.

---

## 2. Struttura del Modulo

*   **[cli.py](file://$USER_SKILLS_DIR/monochrome.tf/cli.py)**: Entrypoint unificato basato su Click (`search`, `download`).
*   **[client.py](file://$USER_SKILLS_DIR/monochrome.tf/client.py)**: Logica di automazione del browser (configurazione preferenze download Chromium per evitare dialog modali, gestione dialog JS `window.prompt`, attesa e intercettazione evento download).

---

## 3. Esempi di Utilizzo da CLI

### A. Ricerca Album
```bash
# Cerca un album su Monochrome.tf
python3 monochrome.tf/cli.py search "Fake News"

# Mostra in formato JSON
python3 monochrome.tf/cli.py search "883" --json

# Esegui con browser visibile
python3 monochrome.tf/cli.py search "Coldplay" --visible
```

### B. Download Album
```bash
# Download tramite URL completo
python3 monochrome.tf/cli.py download "https://monochrome.tf/album/296803260"

# Download tramite ID numerico album
python3 monochrome.tf/cli.py download 296803260

# Specificare una cartella di output personalizzata e timeout
python3 monochrome.tf/cli.py download 296803260 -o ~/Musica -t 240
```

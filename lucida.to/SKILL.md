# Lucida.to Downloader Automation with CloakBrowser

Questa guida descrive come automatizzare l'estrazione e il download di brani da **Lucida.to** (https://lucida.to/) utilizzando Python e **CloakBrowser**.

---

## 1. Configurazione del Browser e Bypass di Cloudflare

Poiché Lucida.to è protetto da Cloudflare, il browser viene avviato in **modalità non-headless** (`headless=False`). Questo permette di risolvere manualmente eventuali sfide/captcha di Cloudflare all'avvio.

*   **Directory del profilo:** `$XDG_DATA_HOME/browser-profiles/lucida` (default: `~/.local/share/browser-profiles/lucida`).
*   **Gestione dei Download:** Playwright deve essere configurato per accettare i download e salvarli nella cartella dei download dell'utente (`~/Downloads`).

---

## 2. Dettagli di Implementazione Critici (Lezioni Apprese)

Durante lo sviluppo di questa automazione sono stati scoperti dettagli architetturali del sito fondamentali per evitare errori o blocchi:

### A. Evitare Selettori Combinati con `text=` e Virgole
Playwright non gestisce correttamente le virgole nei selettori stringa se combinati con l'engine `text=`. 
*   *Esempio problematico:* `"text=An error..., .download-button"` viene interpretato come ricerca letterale di una stringa contenente la virgola e la classe.
*   *Soluzione:* Creare locatori separati in Python e unirli programmaticamente usando **`locator.or_(other_locator)`**.

### B. Forzare il Click via JavaScript per Superare gli Overlay
A volte il pulsante di download appare visivamente pronto ma Playwright fallisce il click o rimane in attesa perché un elemento invisibile (es. un indicatore di caricamento o header fisso) intercetta il click fisico.
*   *Soluzione:* Utilizzare il metodo **`evaluate("el => el.click()")`** sul locator. Questo esegue l'evento click direttamente tramite il motore JS del browser, ignorando eventuali overlays.

### C. Gestione di Corrispondenze Multiple
Se sono rimasti elementi di ricerche precedenti, potrebbero esserci più pulsanti di download nella pagina. Utilizzare sempre **`.first`** sul locator prima di effettuare l'azione di click per evitare errori di tipo *strict mode violation* di Playwright.

### D. Attese di Stabilizzazione
*   **Attesa Iniziale:** Attendere il caricamento di `#download` fino a 60 secondi (superamento di Cloudflare).
*   **Attesa Post-Invio:** Dopo aver fatto click su `#go`, attendere **3 secondi** (`page.wait_for_timeout(3000)`) prima di mettersi in attesa del risultato, così da consentire all'interfaccia di pulire lo stato precedente e avviare il loader.

---

## 3. Flusso di Lavoro ed Elementi della Pagina

1.  **Navigazione:** Vai su `https://lucida.to/` e attendi la comparsa dell'input `#download`.
2.  **Inserimento:** Incolla l'URL musicale nel campo `#download`.
3.  **Avvio:** Clicca sul pulsante con ID `#go` e attendi 3 secondi.
4.  **Attesa Risultato:** Aspetta la comparsa dell'errore `"An error occured trying to process your request."` o del pulsante di download (classe `.download-button` o testo `"scarica traccia"`).
5.  **Download:** Clicca sul primo pulsante di download disponibile con JS `evaluate` e salva il file in `~/Downloads`.

---

## 4. Esecuzione da CLI (`lucida.to/cli.py`)

Tutte le operazioni di download singolo o in blocco sono gestite tramite `cli.py`:

```bash
# Scarica un singolo brano musicale da URL
python3 lucida.to/cli.py track "<URL_DELLA_CANZONE>"

# Con cartella di output personalizzata
python3 lucida.to/cli.py track "<URL_DELLA_CANZONE>" -o ~/Musica

# Esegui mostrando il browser per visualizzare/risolvere Cloudflare
python3 lucida.to/cli.py track "<URL_DELLA_CANZONE>" --visible
```

---

## 5. Batch & Album Downloader (`cli.py batch`)

Per scaricare in blocco la Wishlist o interi album organizzandoli in cartelle:

```bash
# Scarica la wishlist raggruppando automaticamente per Artista/Album (<Artista>/<Album>/<Traccia>.flac)
python3 lucida.to/cli.py batch --group-albums

# Salta le prime N righe mantenendo il conteggio totale (es: salta le prime 50)
python3 lucida.to/cli.py batch --group-albums --skip 50

# Scarica solo un album specifico raggruppato in cartella
python3 lucida.to/cli.py batch --group-albums --album "J-Ax & Friends"

# Scarica limitando a N brani
python3 lucida.to/cli.py batch --group-albums --limit 5
```

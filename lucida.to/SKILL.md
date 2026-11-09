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

## 4. Esempio Python completo (`downloader.py`)

Di seguito lo script completo implementato in `lucida.to/downloader.py`:

```python
import os
import sys
from cloakbrowser import launch_persistent_context

def main():
    if len(sys.argv) < 2:
        print("Uso: python3 downloader.py <URL_DELLA_CANZONE>")
        sys.exit(1)
        
    track_url = sys.argv[1]
    profile_dir = os.path.join(os.environ.get('XDG_DATA_HOME', os.path.expanduser('~/.local/share')), 'browser-profiles', 'lucida')
    
    print(f"Avvio del browser con il profilo: {profile_dir}")
    context = launch_persistent_context(profile_dir, headless=False)
    page = context.new_page()
    page.set_viewport_size({"width": 1280, "height": 800})
    
    print("Navigazione su https://lucida.to/...")
    page.goto("https://lucida.to/")
    
    print("Attesa del caricamento dell'interfaccia (superamento protezione Cloudflare)...")
    try:
        page.wait_for_selector("#download", timeout=60000)
    except Exception:
        print("Errore: L'interfaccia di Lucida.to non si è caricata. Controlla la finestra del browser.")
        context.close()
        sys.exit(1)
        
    print("Interfaccia pronta! Inserimento dell'URL della canzone...")
    search_input = page.locator("#download")
    search_input.fill(track_url)
    
    # Clicchiamo sul tasto go
    go_button = page.locator("#go")
    go_button.click()
    print("Richiesta inviata. Attesa di 3 secondi per l'avvio dell'elaborazione...")
    page.wait_for_timeout(3000)
    print("Elaborazione in corso (questo potrebbe richiedere un po' di tempo)...")
    
    # Prepariamo i locatori per il controllo dell'esito
    error_locator = page.locator("text=/An error occur/i")
    download_locator = page.locator(".download-button").or_(page.locator("text=/scarica traccia/i"))
    
    combined_locator = error_locator.or_(download_locator)
    
    try:
        # Aspettiamo che appaia uno dei due elementi (il caricamento o l'errore)
        combined_locator.first.wait_for(state="visible", timeout=90000)
    except Exception:
        print("Errore: Timeout durante l'attesa del download o del messaggio di errore.")
        context.close()
        sys.exit(1)
        
    # Controlliamo prima se è apparso l'errore
    if error_locator.is_visible():
        print("[RISULTATO] Non funziona il link: il ripper ha restituito errore per questo URL.")
        context.close()
        sys.exit(1)
        
    # Se invece c'è il tasto download
    if download_locator.first.is_visible():
        print("Brano pronto! Avvio del download...")
        
        # Salviamo nella cartella dei Download dell'utente
        download_dir = os.path.expanduser('~/Downloads')
        os.makedirs(download_dir, exist_ok=True)
        
        try:
            # Registriamo il listener per intercettare l'avvio del download
            downloads = []
            page.on("download", lambda d: downloads.append(d))
            
            # Forziamo il click in JS sul tasto download
            download_locator.first.evaluate("el => el.click()")
            
            # Attendiamo l'esito (errore post-click o avvio effettivo del download)
            error_appeared = False
            for _ in range(45):  # Fino a 45 secondi
                page.wait_for_timeout(1000)
                if error_locator.is_visible():
                    error_appeared = True
                    break
                if downloads:
                    break
            
            if error_appeared:
                print("[RISULTATO] Non funziona il link: errore riscontrato dopo il click su scarica.")
                context.close()
                sys.exit(1)
                
            if not downloads:
                print("Errore: Timeout durante l'attesa dell'avvio del download.")
                context.close()
                sys.exit(1)
                
            download = downloads[0]
            # Salviamo il file mantenendo il nome suggerito dal portale
            suggested_filename = download.suggested_filename
            dest_path = os.path.join(download_dir, suggested_filename)
            download.save_as(dest_path)
            
            print(f"[SUCCESS] Download completato! File salvato in: {dest_path}")
        except Exception as e:
            print(f"Errore durante il download del file: {e}")
            
    context.close()

```

---

## 5. Batch & Album Downloader (`batch_downloader.py`)

Per scaricare in blocco la Wishlist o interi album organizzandoli in cartelle:

```bash
# Scarica la wishlist raggruppando automaticamente per Artista/Album (<Artista>/<Album>/<Traccia>.flac)
python3 batch_downloader.py --group-albums

# Salta le prime N righe mantenendo il conteggio totale (es: salta le prime 50)
python3 batch_downloader.py --group-albums --skip 50

# Scarica solo un album specifico raggruppato in cartella
python3 batch_downloader.py --group-albums --album "J-Ax & Friends"

# Scarica limitando a N brani
python3 batch_downloader.py --group-albums --limit 5
```

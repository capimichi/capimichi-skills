# Mircrew-releases.org Automation with CloakBrowser

Questa guida descrive come automatizzare l'interazione, la ricerca di release e l'estrazione dei magnet/torrent da **Mircrew-releases.org** (https://mircrew-releases.org/) utilizzando Python e **CloakBrowser**.

---

## 1. Configurazione del Browser e Bypass di Cloudflare

Mircrew-releases.org è protetto da Cloudflare con blocco per bot e richieste HTTP standard (403 Forbidden).
Utilizzando **CloakBrowser** con un profilo persistente, il browser supera trasparentemente la verifica Cloudflare e mantiene la sessione di login salvata nel profilo.

*   **Directory del profilo:** `$XDG_DATA_HOME/browser-profiles/mircrew` (default: `~/.local/share/browser-profiles/mircrew`).
*   **Modalità di avvio:** `headless=False` (oppure `headless=True` dopo aver salvato la sessione nel profilo).

---

## 2. Gestione Credenziali e Autenticazione

Il client supporta la risoluzione automatica delle credenziali attraverso tre canali, in ordine di priorità:
1. Parametri espliciti passati al metodo `login(username, password)` o alla CLI.
2. Variabili d'ambiente `MIRCREW_USERNAME` e `MIRCREW_PASSWORD`.
3. Ricerca automatica tramite Bitwarden CLI (`bw list items --search mircrew`).

Una volta effettuato il login con successo selezionando l'opzione di autologin, la sessione rimane valida e persistente all'interno del profilo `$XDG_DATA_HOME/browser-profiles/mircrew`.

---

## 3. Dettagli di Implementazione Critici

### A. Parametri di Ricerca Ottimizzati
La ricerca standard del forum può restituire singoli post o messaggi sparsi. Per ottenere direttamente l'elenco delle release ordinate per argomento:
*   `sr=topics`: Restituisce i risultati raggruppati per topic anziché per singoli post.
*   `sf=titleonly`: Limita la ricerca ai titoli delle release per evitare falsi positivi nel testo delle discussioni.
*   I selettori CSS chiave sono: `li.row a.topictitle` per il titolo e link del topic, `.forumtitle` per la sezione forum.

### B. Sblocco Contenuti Protetti (Tasto "Ringrazia / Thanks")
Su Mircrew molti link magnet e torrent sono racchiusi all'interno di un blocco nascosto (`.hidebox`) che richiede di lasciare un ringraziamento:
*   Il pulsante di ringraziamento viene intercettato con il selettore:
    ```css
    .post a:has(i.fa-thumbs-o-up), .post a:has(i.fa-thumbs-up), .post a:has(i.icon-thumbs-up)
    ```
*   Dopo aver cliccato il tasto, il contenuto del box viene sbloccato (`.hidebox.unhide dd`) rendendo visibile il link `magnet:?xt=...`.

---

## 4. Struttura del Modulo

*   `cli.py`: Entrypoint unificato basato su Click con i comandi `status`, `login`, `search`, `magnets`.
*   `client.py`: Classe principale `MircrewBrowser` che incapsula la gestione del ciclo di vita del browser Cloak, login, ricerca e sblocco/estrazione magnet.

---

## 5. Esempi di Utilizzo da CLI

### A. Verifica Stato o Esecuzione Login
```bash
# Verifica sessione esistente
python3 mircrew-releases.org/cli.py status

# Esecuzione login interattivo o con credenziali da env/bitwarden
python3 mircrew-releases.org/cli.py login
```

### B. Ricerca Release
```bash
# Cerca release per titolo
python3 mircrew-releases.org/cli.py search "Inception" --limit 5

# Cerca estraendo direttamente i magnet del primo risultato
python3 mircrew-releases.org/cli.py search "Matrix 1999" --magnets

# Cerca in tutti i campi (non solo titolo)
python3 mircrew-releases.org/cli.py search "Keanu Reeves" --all-fields
```

### C. Estrazione Magnet da Topic
```bash
# Tramite topic ID
python3 mircrew-releases.org/cli.py magnets 90873

# Tramite URL completo
python3 mircrew-releases.org/cli.py magnets "https://mircrew-releases.org/viewtopic.php?t=90873"
```

---

## 6. Utilizzo Programmatico in Python

```python
from client import MircrewBrowser

with MircrewBrowser(headless=False) as browser:
    # 1. Ricerca release
    results = browser.search("Dune", limit=5)
    for r in results:
        print(f"[{r['id']}] {r['title']} -> {r['url']}")
        
    # 2. Estrazione magnet del primo risultato
    if results:
        topic_info = browser.get_topic_details(results[0]["id"])
        print("Titolo:", topic_info["title"])
        for magnet in topic_info["magnets"]:
            print("Magnet:", magnet)
```

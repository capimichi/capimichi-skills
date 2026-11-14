---
name: amazon
description: Skill per navigare su Amazon (Amazon.it) con un browser virtuale stealth (CloakBrowser/Playwright). Gestisce il login manuale a video e salva in modo persistente la sessione, i cookie e i profili nelle directory conformi allo standard XDG.
---

# Amazon Browser Automation Skill

Questa skill fornisce gli strumenti per automatizzare la navigazione, la ricerca di prodotti, l'ispezione dei dettagli, la consultazione del carrello e la visualizzazione degli ordini su **Amazon.it** tramite un browser virtuale stealth (**CloakBrowser** basato su Playwright).

Il flusso di autenticazione è progettato per la massima affidabilità:
1. L'utente effettua il **login iniziale a mano** in una finestra visibile del browser (gestendo OTP, 2FA, passkey o app confirmation).
2. La sessione, i token e i cookie vengono salvati in modo persistente nella **directory standard XDG** (`$XDG_DATA_HOME/amazon/browser_session`).
3. Tutte le successive esecuzioni (anche in background / headless) riutilizzano automaticamente l'identità autenticata senza dover rifare l'accesso.

---

## 📁 1. Specifiche XDG Base Directory

Tutti i dati persistenti, configurazioni e file temporanei risiedono nella home utente rispettando lo standard **XDG Base Directory**:

| Directory | Variabile d'Ambiente | Percorso Predefinito | Contenuto |
| :--- | :--- | :--- | :--- |
| **Data (Profilo Browser)** | `AMAZON_BROWSER_PROFILE` o `XDG_DATA_HOME` | `~/.local/share/amazon/browser_session/` | Profilo Chromium completo (cookie, IndexedDB, localStorage, cache di sessione) |
| **Data (Storage State)** | `XDG_DATA_HOME` | `~/.local/share/amazon/storage_state.json` | Snapshot JSON dello stato di autenticazione Playwright |
| **Config** | `AMAZON_CONFIG_DIR` o `XDG_CONFIG_HOME` | `~/.config/amazon/` | Eventuali file di configurazione e preferenze |
| **Cache & Debug** | `AMAZON_CACHE_DIR` o `XDG_CACHE_HOME` | `~/.cache/amazon/screenshots/` | Screenshot di debug e file temporanei |

> [!NOTE]
> Se desideri usare un percorso dati alternativo, puoi impostare le variabili d'ambiente `AMAZON_DATA_DIR` o `AMAZON_BROWSER_PROFILE`.

---

## 🔐 2. Primo Accesso: Login Manuale

Per effettuare il login manuale e salvare la sessione:

```bash
cd $SKILL_PROJECT_PATH/amazon
python3 login.py
```

### Come funziona il login:
1. Si apre una finestra Chromium non-headless con protezioni stealth attive.
2. La pagina naviga automaticamente sul portale di accesso di Amazon.it.
3. **Effettua l'accesso a mano:** inserisci email, password e autorizza l'eventuale notifica 2FA/App Amazon sul tuo telefono.
4. Lo script rileva in tempo reale l'avvenuto login (o puoi premere `INVIO` nella console).
5. Il browser salva lo stato su disco nella directory XDG e si chiude pulitamente.

---

## 🛠️ 3. Strumenti e Script CLI Inclusi

Tutti gli script sono già configurati ed eseguibili direttamente da riga di comando.

### A. Ricerca Prodotti (`search.py`)
Cerca articoli estraendo titolo, prezzo, valutazione in stelle, numero recensioni, badge Prime e ASIN.

```bash
# Ricerca classica (default 10 risultati)
python3 search.py "cuffie bluetooth anc"

# Limita i risultati ed estrai in formato JSON
python3 search.py "logitech mx master 3s" --limit 5 --json

# Ordina per prezzo crescente
python3 search.py "cavo usb-c 2m" --sort price-asc-rank

# Modalità visibile (non headless) per debug
python3 search.py "kindle paperwhite" --visible
```

### B. Ispezione Dettaglio Prodotto (`inspect_product.py`)
Estrae la scheda tecnica completa di un prodotto indicando disponibilità, venditore (es. Venduto e Spedito da Amazon), prezzo e caratteristiche salienti tramite **ASIN** o **URL**.

```bash
# Tramite ASIN (10 caratteri)
python3 inspect_product.py B08N5WRWNW

# Tramite URL Amazon
python3 inspect_product.py "https://www.amazon.it/dp/B08N5WRWNW"

# Output in JSON
python3 inspect_product.py B08N5WRWNW --json
```

### C. Carrello della Spesa (`cart.py`)
Verifica il carrello attivo, il subtotale e i singoli articoli presenti.

```bash
# Ispezione del carrello corrente
python3 cart.py

# In formato JSON
python3 cart.py --json
```

### D. Storico Ordini Recenti (`orders.py`)
Consulta gli ultimi ordini effettuati sul proprio account Amazon.it (richiede login).

```bash
# Mostra gli ultimi 5 ordini
python3 orders.py

# Mostra gli ultimi 10 ordini in formato JSON
python3 orders.py --limit 10 --json
```

---

## 🐍 4. Utilizzo come Libreria Python

Puoi importare i moduli per creare workflow personalizzati:

```python
from amazon.browser import launch_amazon_browser, check_amazon_login, accept_cookies_if_present
from amazon.paths import get_browser_session_dir

# Avvia il browser riutilizzando la sessione XDG
context = launch_amazon_browser(headless=True)
page = context.new_page()

# Navigazione
page.goto("https://www.amazon.it")
accept_cookies_if_present(page)

# Controllo autenticazione
status = check_amazon_login(page)
print(f"Utente: {status['user_greeting']} (Autenticato: {status['is_logged_in']})")

context.close()
```

---

## 🛡️ 5. Stealth & Best Practices Anti-Bot

- **CloakBrowser:** Viene utilizzato per aggirare il fingerprinting di automazione (`navigator.webdriver`, canvas spoofing, WebGL vendor, cdc flags).
- **Viewport su Mac:** Il parametro `viewport=None` evita problemi di rendering e scaling su macOS, garantendo che le dimensioni della finestra non vengano tagliate.
- **Cookie Banner GDPR:** La funzione `accept_cookies_if_present` gestisce automaticamente il pop-up del consenso europeo (`#sp-cc-accept`).
- **Persistenza coerente:** La chiusura del contesto tramite `context.close()` garantisce che i database SQLite e i cookie di Chromium vengano correttamente salvati su filesystem.

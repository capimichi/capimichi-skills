---
name: google-browser
description: Skill per la navigazione generica sul web e su Google tramite CloakBrowser (Playwright stealth). Supporta ricerche organiche su Google, apertura di siti con bypass anti-bot, estrazione di testo e ispezione DOM con sessione persistente XDG.
---

# Google & Web Browser Automation Skill (CloakBrowser)

Questa skill fornisce gli strumenti per automatizzare la navigazione web, le ricerche organiche su **Google**, l'estrazione di metadati e l'ispezione di pagine web tramite un browser virtuale stealth (**CloakBrowser** basato su Playwright).

Il profilo browser è persistente e gestito secondo lo standard **XDG Base Directory**:
1. Le sessioni, i cookie e le preferenze vengono salvati in `$XDG_DATA_HOME/browser-profiles/google`.
2. I banner di consenso cookie di Google vengono gestiti e accettati automaticamente.
3. Se l'utente desidera effettuare il login al proprio account Google, può farlo una sola volta tramite la modalità interattiva visibile (`cli.py session login`).
4. Tutte le successive ricerche ed esplorazioni possono avvenire in background (**headless**) con fingerprint anti-bot camuffato.

---

## 📁 1. Specifiche XDG Base Directory

| Directory | Variabile d'Ambiente | Percorso Predefinito | Contenuto |
| :--- | :--- | :--- | :--- |
| **Data (Profilo Browser)** | `XDG_DATA_HOME` | `~/.local/share/browser-profiles/google/` | Profilo Chromium persistente (cookie, IndexedDB, localStorage) |
| **Cache & Screenshot** | `XDG_CACHE_HOME` | `~/.cache/google-browser/` | Screenshot di navigazione (`.png`) e file temporanei |

---

## 🛠️ 2. Struttura del Modulo

*   **[cli.py](file://$USER_SKILLS_DIR/google/browser/cli.py)**: Entrypoint unificato basato su **Click** (`search`, `open`, `inspect`, `session`).
*   **[client.py](file://$USER_SKILLS_DIR/google/browser/client.py)**: Logica operativa per ricerche Google, apertura pagine, estrazione snippet e testi.
*   **[browser.py](file://$USER_SKILLS_DIR/google/browser/browser.py)**: Gestione del ciclo di vita di CloakBrowser, pulizia lock orfani, risoluzione percorsi XDG e accettazione automatica dei cookie.

---

## 🚀 3. Esempi di Utilizzo da CLI

Tutte le operazioni si invocano con `python3 google/browser/cli.py <comando>`:

### A. Ricerca Organica su Google (`search`)
Estrae titolo, URL e snippet descrittivo dei risultati:

```bash
# Ricerca semplice (default 10 risultati)
python3 google/browser/cli.py search "pinguini tattici nucleari tour 2026"

# Limita i risultati ed esporta in JSON
python3 google/browser/cli.py search "fastapi tutorial" --limit 5 --json

# Specifica lingua e paese di ricerca
python3 google/browser/cli.py search "ristoranti bologna" --language it --country it

# Modalità visibile (non headless) per osservare il browser
python3 google/browser/cli.py search "apple macbook pro m4" --visible
```

### B. Apertura Pagine Web con Stealth Anti-Bot (`open`)
Naviga verso qualsiasi sito web superando controlli anti-bot e Cloudflare:

```bash
# Apertura semplice headless con attesa di caricamento
python3 google/browser/cli.py open "https://news.ycombinator.com" --wait 3

# Salva uno screenshot della pagina in ~/.cache/google-browser/
python3 google/browser/cli.py open "https://github.com" --screenshot github_home.png

# Estrae e stampa il testo leggibile della pagina
python3 google/browser/cli.py open "https://en.wikipedia.org/wiki/Python_(programming_language)" --text

# Modalità interattiva (apre la finestra visibile per interazione manuale dell'utente)
python3 google/browser/cli.py open "https://google.com" --interactive
```

### C. Ispezione Contenuto & Selettori CSS (`inspect`)
Estrae titolo, meta tag e nodi HTML mirati:

```bash
# Ispezione generica (titolo, meta description, intestazioni principali)
python3 google/browser/cli.py inspect "https://example.com"

# Estrazione selettore specifico (es. titoli articoli o link)
python3 google/browser/cli.py inspect "https://news.ycombinator.com" --selector "span.titleline a"

# Output strutturato in JSON
python3 google/browser/cli.py inspect "https://news.ycombinator.com" --selector ".titleline a" --json
```

### D. Gestione Sessione Google (`session`)
Consente di verificare o autenticare un account Google per ricerche personalizzate:

```bash
# Verifica se la sessione corrente ha un account Google collegato
python3 google/browser/cli.py session status

# Login manuale a video su Google Accounts (salva i cookie nel profilo persistente)
python3 google/browser/cli.py session login
```

---

## 🐍 4. Utilizzo Programmatico in Python

Puoi importare direttamente le funzioni per creare workflow complessi:

```python
from google.browser.client import search_google, open_webpage, inspect_webpage

# 1. Ricerca rapida
results = search_google("deepmind robotics", limit=5)
for r in results:
    print(f"- {r['title']}: {r['url']}")

# 2. Apertura e screenshot di una pagina
data = open_webpage("https://openai.com", screenshot_name="openai.png", wait_sec=3)
print("Titolo:", data["title"])
```

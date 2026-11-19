---
name: Meta Ads & Business Manager Skill
description: Automazione, gestione sessioni persistenti e interazione con Meta Business Suite, Ads Manager e Facebook via CloakBrowser.
---

# Meta Ads & Business Manager Skill

Questa skill fornisce gli strumenti per automatizzare l'accesso, la verifica e l'interazione con **Meta Business Suite**, **Facebook** e **Meta Ads Manager** ([business.facebook.com](https://business.facebook.com/)) utilizzando **Python** e **CloakBrowser**.

---

## 📂 1. Struttura dei Dati e Standard XDG

Tutti i dati e i profili browser persistenti risiedono nella home dell'utente (`~` / `$HOME`) rispettando le specifiche XDG:

| Directory | Percorso Predefinito | Scopo |
| :--- | :--- | :--- |
| **`XDG_DATA_HOME`** | `~/.local/share/meta/` | Root dei dati persistenti di Meta |
| └─ **`browser_session/`** | `~/.local/share/meta/browser_session/` | **Profilo Chromium / CloakBrowser**: cookie di sessione, local storage e 2FA |
| **`XDG_CACHE_HOME`** | `~/.cache/meta/` | Screenshot di debug (`.png`), dump HTML di analisi |

---

## 🔑 2. Credenziali & Configurazione

Le credenziali per l'accesso del profilo designato (Marcello Ferrari) sono memorizzate localmente in `~/.zshrc.local`:

```bash
export META_EMAIL="marcelloferrari627@outlook.it"
export META_PASSWORD="..."
```

Lo script [login.py](file://$USER_SKILLS_DIR/meta/login.py) legge automaticamente queste variabili d'ambiente (o direttamente il file `.zshrc.local`) per pre-compilare il form di accesso su Facebook.

---

## 🛠️ 3. Struttura del Modulo & Comandi CLI

Tutte le operazioni frequenti sono unificate in [cli.py](file://$USER_SKILLS_DIR/meta/cli.py):

*   **[cli.py](file://$USER_SKILLS_DIR/meta/cli.py)**: Entrypoint Click (`login`, `status`, `billing`, `ads-manager`, `suite`).
*   [paths.py](file://$USER_SKILLS_DIR/meta/paths.py): Helper per calcolare i percorsi XDG con home utente dinamica (`~`).
*   [browser.py](file://$USER_SKILLS_DIR/meta/browser.py): Factory per istanziare CloakBrowser agganciandosi automaticamente alla cartella `~/.local/share/meta/browser_session`.
*   [login.py](file://$USER_SKILLS_DIR/meta/login.py): Script interattivo (finestra visibile) per effettuare il login, gestire verifiche/2FA e verificare l'approdo su Meta Business Suite.
*   [get_account_status.py](file://$USER_SKILLS_DIR/meta/get_account_status.py): Ispezione automatica dello stato contabile, debiti residui, limiti di spesa e metodi di pagamento dell'ad account.
*   [open_billing.py](file://$USER_SKILLS_DIR/meta/open_billing.py): Apre una finestra visibile con dimensioni responsive direttamente nella schermata Metodi di Pagamento per inserimento manuale protetto di carte o PayPal.

---

## 🚀 4. Esempi di Utilizzo da CLI

```bash
# 1. Login interattivo (finestra visibile con pre-compilazione credenziali)
python3 meta/cli.py login

# 2. Verifica dello stato di autenticazione sessione
python3 meta/cli.py status

# 3. Ispezione stato contabile e metodi di pagamento (headless)
python3 meta/cli.py billing

# 4. Apertura interfaccia pagamenti per inserimento carta o PayPal
python3 meta/cli.py billing --open-ui

# 5. Apertura diretta di Ads Manager (Account #1116925509636183)
python3 meta/cli.py ads-manager

# 6. Apertura Meta Business Suite
python3 meta/cli.py suite
```

---

## 🏢 5. Asset e Account Pubblicitari Rilevati

Dalla verifica automatica della sessione autenticata risultano attivi e accessibili i seguenti asset:

*   **Meta Business Suite:** [business.facebook.com/latest/home](https://business.facebook.com/latest/home?asset_id=918101574729792)
    *   **Pagina Principale:** *Naturale e sostenibile*
    *   **Asset ID:** `918101574729792`
*   **Gestione Inserzioni (Ads Manager):** [adsmanager.facebook.com](https://adsmanager.facebook.com/adsmanager/manage/campaigns?act=1116925509636183)
    *   **ID Account Pubblicitario (`act`):** `1116925509636183`
*   **Fatturazione e Metodi di Pagamento:** [business.facebook.com/billing_hub](https://business.facebook.com/billing_hub/payment_settings/)


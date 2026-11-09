---
name: Meta Ads & Business Manager Skill
description: Automazione, gestione sessioni persistenti e interazione con Meta Business Suite, Ads Manager e Facebook via CloakBrowser.
---

# Meta Ads & Business Manager Skill

Questa skill fornisce gli strumenti per automatizzare l'accesso, la verifica e l'interazione con **Meta Business Suite**, **Facebook** e **Meta Ads Manager** ([business.facebook.com](https://business.facebook.com/)) utilizzando **Python** e **CloakBrowser**.

---

## 📂 1. Struttura dei Dati e Standard XDG

Tutti i dati e i profili browser persistenti risiedono nella home dell'utente (`/Users/michele`) rispettando le specifiche XDG:

| Directory | Percorso Predefinito | Scopo |
| :--- | :--- | :--- |
| **`XDG_DATA_HOME`** | `~/.local/share/meta/` | Root dei dati persistenti di Meta |
| └─ **`browser_session/`** | `~/.local/share/meta/browser_session/` | **Profilo Chromium / CloakBrowser**: cookie di sessione, local storage e 2FA |
| **`XDG_CACHE_HOME`** | `~/.cache/meta/` | Screenshot di debug (`.png`), dump HTML di analisi |

---

## 🔑 2. Credenziali & Configurazione

Le credenziali per l'accesso del profilo designato (Marcello Ferrari) sono memorizzate localmente in `/Users/michele/.zshrc.local`:

```bash
export META_EMAIL="marcelloferrari627@outlook.it"
export META_PASSWORD="..."
```

Lo script [login.py](file:///Users/michele/PycharmProjects/capimichi-skills/meta/login.py) legge automaticamente queste variabili d'ambiente (o direttamente il file `.zshrc.local`) per pre-compilare il form di accesso su Facebook.

---

## 🛠️ 3. File e Script della Skill

I file sono organizzati nella directory [meta/](file:///Users/michele/PycharmProjects/capimichi-skills/meta):

*   [paths.py](file:///Users/michele/PycharmProjects/capimichi-skills/meta/paths.py): Helper per calcolare i percorsi XDG con home puntata a `/Users/michele`.
*   [browser.py](file:///Users/michele/PycharmProjects/capimichi-skills/meta/browser.py): Factory per istanziare CloakBrowser agganciandosi automaticamente alla cartella `~/.local/share/meta/browser_session`. Include gestione `viewport=None` per evitare il troncamento dei contenuti sui display Retina Mac.
*   [login.py](file:///Users/michele/PycharmProjects/capimichi-skills/meta/login.py): Script interattivo (finestra visibile) per effettuare il login, gestire verifiche/2FA e verificare l'approdo su Meta Business Suite.
*   [explore.py](file:///Users/michele/PycharmProjects/capimichi-skills/meta/explore.py): Script per verificare la sessione, scattare screenshot e scaricare il sorgente HTML di Meta Business Suite.
*   [get_account_status.py](file:///Users/michele/PycharmProjects/capimichi-skills/meta/get_account_status.py): Ispezione automatica dello stato contabile, debiti residui, limiti di spesa e metodi di pagamento dell'ad account.
*   [open_billing.py](file:///Users/michele/PycharmProjects/capimichi-skills/meta/open_billing.py): Apre una finestra visibile con dimensioni responsive direttamente nella schermata Metodi di Pagamento per inserimento manuale protetto di carte o PayPal.

---

## 🚀 4. Flusso di Login & Primo Accesso

1. Esegui il login:
   ```bash
   python3 meta/login.py
   ```
2. Si aprirà la finestra di CloakBrowser su `facebook.com` con email e password già pre-inserite nel form.
3. Clicca su **Accedi** e completa eventuali verifiche di sicurezza/2FA richieste da Meta.
4. Una volta dentro, conferma in chat o nel terminale. Lo script verificherà il reindirizzamento su `business.facebook.com` e salverà la sessione persistente.

---

## 🏢 5. Asset e Account Pubblicitari Rilevati

Dalla verifica automatica della sessione autenticata risultano attivi e accessibili i seguenti asset:

*   **Meta Business Suite:** [business.facebook.com/latest/home](https://business.facebook.com/latest/home?asset_id=918101574729792)
    *   **Pagina Principale:** *Naturale e sostenibile*
    *   **Asset ID:** `918101574729792`
*   **Gestione Inserzioni (Ads Manager):** [adsmanager.facebook.com](https://adsmanager.facebook.com/adsmanager/manage/campaigns?act=1116925509636183)
    *   **ID Account Pubblicitario (`act`):** `1116925509636183`
*   **Fatturazione e Metodi di Pagamento:** [business.facebook.com/billing_hub](https://business.facebook.com/billing_hub/payment_settings/)


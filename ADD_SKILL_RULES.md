# Regole di Sviluppo e Standard per le Skill (`ADD_SKILL_RULES.md`)

Questo documento definisce gli standard architetturali e operativi obbligatori per la creazione, manutenzione e documentazione di tutte le skill presenti in questa repository.

Tutti gli sviluppatori e gli agenti AI **devono attenersi rigorosamente** a queste linee guida prima di aggiungere o modificare codice e documentazione.

---

## 1. Regola dei Percorsi Dinamici e Portabilità (No Hardcoded Paths)

Nessun file, script o documento markdown deve contenere percorsi assoluti fissi riferiti a uno specifico utente o macchina (es. `/Users/...` o `/home/...`).

### A. Riferimento alla Root del Repository delle Skill
* Per puntare alla cartella base delle skill, fare **esclusivamente** riferimento alla variabile d'ambiente:
  ```bash
  $SKILL_PROJECT_PATH
  ```
* **Esempi corretti:**
  * Bash / CLI: `uv run $SKILL_PROJECT_PATH/google-tasks/scripts/gtasks.py list`
  * Python: `sys.path.insert(0, os.environ.get("SKILL_PROJECT_PATH", "."))`
  * Markdown link: `[script](file://$SKILL_PROJECT_PATH/nome-skill/script.py)`

### B. Riferimento alla Home Utente
* Nei comandi shell e nei file Markdown usare la tilde `~` o la variabile `$HOME`.
* In Python risolvere dinamicamente la home:
  ```python
  from pathlib import Path
  import os

  home = Path(os.environ.get("HOME", Path.home()))
  # oppure
  path = os.path.expanduser("~/Downloads")
  ```

### C. Rispetto delle specifiche XDG Base Directory
Tutti i dati generati, le cache, i log e i profili browser persistenti devono rispettare le specifiche XDG:
* **Dati e profili persistenti:** `$XDG_DATA_HOME/<skill>` (default: `~/.local/share/<skill>`)
* **Configurazioni:** `$XDG_CONFIG_HOME/<skill>` (default: `~/.config/<skill>`)
* **File temporanei e cache:** `$XDG_CACHE_HOME/<skill>` (default: `~/.cache/<skill>`)

---

## 2. Agnosticità delle Configurazioni (Regola No Chezmoi / No Tool Esterni)

Le skill devono essere completamente **agnostiche** rispetto al modo in cui i file di sistema, le credenziali o i dotfile vengono compilati, distribuiti o sincronizzati sulla macchina:

* **Nessun riferimento a Chezmoi:** non citare file template (`.tmpl`), comandi `chezmoi apply` o percorsi interni a `~/.local/share/chezmoi`.
* **Esclusivo uso delle Variabili d'Ambiente di Sistema:** il codice deve verificare e consumare unicamente variabili d'ambiente standard (es. `os.environ.get("SERVICE_API_KEY")`).
* È responsabilità dell'ambiente utente (es. `.zshrc`, file d'ambiente sorgente, o sessione di shell) esportare tali variabili prima dell'esecuzione dello script.
* In caso di credenziale mancante, restituire un messaggio chiaro indicando il nome della variabile d'ambiente attesa (es. *"Variabile SERVICE_API_KEY non trovata nell'ambiente"*).

---

## 3. Pulizia e Struttura della Root Directory

Per mantenere il repository ordinato e ottimizzato per il contesto degli agenti AI:

* **Nella root del repository possono risiedere ESCLUSIVAMENTE:**
  1. `README.md` (Tabella di routing, indice compatto e trigger d'uso)
  2. `ADD_SKILL_RULES.md` (Questo documento di regole)
  3. `.gitignore`
* **Nessun file sparso:** vietato posizionare nella root script `.py`, piani operativi o file di note `.md`, cartelle di export o screenshot.
* Ogni file accessorio, script ausiliario o documento di supporto deve risiedere all'interno della cartella della rispettiva skill (es. `worldfilia/DOLORFIX_STRATEGY_PLAN.md`).

---

## 4. Struttura Obbligatoria di una Skill

Ogni skill deve essere collocata in una sottocartella dedicata e contenere:
1. **`SKILL.md` (Obbligatorio):**
   * Descrizione chiara del servizio e del relativo scopo.
   * Tabella delle variabili d'ambiente richieste con valori di default se applicabili.
   * Esempi di comandi CLI pronti all'uso basati su `$SKILL_PROJECT_PATH`.
2. **Script CLI / Automazione:**
   * Script Python autosufficienti con `argparse` o click.
   * Gestione corretta dei percorsi XDG tramite moduli helper (es. `paths.py`).

---

## 5. Registrazione della Nuova Skill nel `README.md`

Quando viene creata o integrata una nuova skill, è **obbligatorio aggiornare la tabella nel `README.md` della root** inserendo:
* **Categoria** (es. *Media & Video*, *Musica*, *Task & To-Do*, *Marketing*, *Documenti*)
* **Link alla cartella** ([`nome-skill`](file://$SKILL_PROJECT_PATH/nome-skill/SKILL.md))
* **Trigger Operativo univoco:** spiegazione esatta di *quando* l'agente deve attivare questa specifica skill (es. *"Se l'utente vuole consultare scontrini o fatture..."*).
* **Priorità / Note:** specificare se è la skill predefinita per un certo ambito o un'alternativa secondaria.

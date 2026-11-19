# Regole di Sviluppo e Standard per le Skill (`ADD_SKILL_RULES.md`)

Questo documento definisce gli standard architetturali e operativi obbligatori per la creazione, manutenzione e documentazione di tutte le skill presenti in questa repository.

Tutti gli sviluppatori e gli agenti AI **devono attenersi rigorosamente** a queste linee guida prima di aggiungere o modificare codice e documentazione.

---

## 1. Regola dei Percorsi Dinamici e Portabilità (No Hardcoded Paths)

Nessun file, script o documento markdown deve contenere percorsi assoluti fissi riferiti a uno specifico utente o macchina (es. `/Users/...` o `/home/...`).

### A. Riferimento alla Root del Repository delle Skill
* Per puntare alla cartella base delle skill, fare **esclusivamente** riferimento alla variabile d'ambiente:
  ```bash
  $USER_SKILLS_DIR
  ```
* **Esempi corretti:**
  * Bash / CLI: `python3 $USER_SKILLS_DIR/paperless/cli.py search "fattura"`
  * Python: `sys.path.insert(0, os.environ.get("USER_SKILLS_DIR", "."))`
  * Markdown link: `[script](file://$USER_SKILLS_DIR/nome-skill/cli.py)`

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

## 4. Runtime Python, Gestione Virtualenv e Dipendenze

Tutte le automazioni e funzionalità del repository devono essere sviluppate secondo questi principi:

### A. Linguaggio Unico: Solo Python
* Tutte le funzionalità, gli script operativi e le automazioni devono essere scritti in **Python**.

### B. Interprete Dinamico (Nessun Percorso Hardcoded)
* Gli script devono essere eseguiti con il comando standard:
  ```bash
  python3 $USER_SKILLS_DIR/<skill>/cli.py <comando>
  ```
* **Nessun percorso hardcoded** a virtualenv specifici (es. né `~/.venv`, né `/opt/homebrew/...`, né percorsi utente). Si utilizza l'interprete Python risolto automaticamente nel contesto o nella sessione corrente dell'utente (`python3` / `sys.executable`).

### C. Divieto Assoluto di Virtualenv Locali
* È **tassativamente vietato** creare directory `.venv`, `venv` o virtual environment locali all'interno di `$USER_SKILLS_DIR` o delle singole cartelle delle skill.
* La repository deve rimanere snella, portabile e priva di ambienti virtuali incorporati.

### D. Gestione Trasparente delle Dipendenze & Segnalazione Utente
* Le librerie esterne richieste (es. `click`, `requests`, `playwright`, ecc.) devono essere installate dall'utente nel proprio ambiente Python tramite `pip`.
* In caso di modulo mancante all'avvio dello script, intercettare l'errore e notificare chiaramente all'utente il comando di installazione:
  ```python
  try:
      import click
  except ImportError:
      sys.exit("Errore: modulo 'click' non trovato. Installa le dipendenze richieste eseguendo: pip install click")
  ```

---

## 5. Struttura Obbligatoria di una Skill e Standard `cli.py` (Click)

Ogni skill deve essere collocata in una sottocartella dedicata e contenere:

### 1. `SKILL.md` (Obbligatorio)
* Descrizione chiara del servizio e del relativo scopo.
* Tabella delle variabili d'ambiente richieste con valori di default se applicabili.
* Esempi di comandi CLI pronti all'uso basati su `python3 $USER_SKILLS_DIR/<skill>/cli.py <comando>`.

### 2. Entrypoint Unico `cli.py` con Click (Obbligatorio)
* Ogni skill deve esporre un file eseguibile **`cli.py`** posizionato nella root della skill:
  ```bash
  $USER_SKILLS_DIR/<skill>/cli.py
  ```
* L'interfaccia a riga di comando deve essere implementata con **Click**:
  * Un gruppo principale `@click.group()` che raggruppa tutti i sottocomandi.
  * Sottocomandi operativi `@cli.command()` per ciascuna funzionalità offerta dal servizio.
  * Ogni comando e opzione deve definire il parametro `help="..."` per garantire l'auto-documentazione (`--help`).
  * Ove opportuno, prevedere l'opzione `--json` per produrre un output strutturato leggibile dagli agenti AI.

### 3. Pattern Facade e Moduli di Supporto
* **`cli.py`** gestisce unicamente:
  * Il parsing di argomenti e opzioni da linea di comando.
  * La validazione di base dei parametri.
  * La formattazione e la stampa dell'output (testo o JSON).
  * La gestione amichevole degli errori verso l'utente.
* Tutta la logica di business e integrazione deve risiedere in moduli helper affiancati:
  * `client.py` o `browser.py`: logica di chiamata API o automazione browser.
  * `paths.py`: risoluzione dei percorsi XDG (`~/.config`, `~/.local/share`, `~/.cache`).
  * `models.py` / `utils.py`: elaborazione o trasformazione dati.

### 4. Modularità per Skill Complesse (Sottocartella `commands/`)
Per evitare la saturazione di `cli.py` nelle skill con molteplici comandi o aree funzionali distinte (oltre 5–6 comandi o molteplici domini logici):
* Creare una sottocartella `commands/` all'interno della skill.
* Suddividere i comandi in moduli tematici (es. `commands/odometer.py`, `commands/services.py`).
* Ciascun modulo definisce un gruppo o comandi Click (es. `@click.group("odometer")`).
* `cli.py` funge da snodo leggero (sotto le 50 righe) registrando i gruppi tramite `cli.add_command(...)`.
* Per skill semplici (1–5 comandi lineari), i comandi possono rimanere direttamente definiti dentro `cli.py`.

---

## 6. Registrazione della Nuova Skill nel `README.md`

Quando viene creata o integrata una nuova skill, è **obbligatorio aggiornare la tabella nel `README.md` della root** inserendo:
* **Categoria** (es. *Media & Video*, *Musica*, *Task & To-Do*, *Marketing*, *Documenti*)
* **Link alla cartella** ([`nome-skill`](file://$USER_SKILLS_DIR/nome-skill/SKILL.md))
* **Trigger Operativo univoco:** spiegazione esatta di *quando* l'agente deve attivare questa specifica skill (es. *"Se l'utente vuole consultare scontrini o fatture..."*).
* **Priorità / Note:** specificare se è la skill predefinita per un certo ambito o un'alternativa secondaria.

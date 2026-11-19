# Standard Python CLI (Click), Gestione Virtualenv & Audit di Migrazione Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use `executing-plans` to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Aggiornare le regole di sviluppo (`ADD_SKILL_RULES.md`), il sommario (`README.md`) e creare l'audit completo con checklist di migrazione (`MIGRATION_CHECKLIST.md`) per standardizzare l'uso di Python, il divieto di venv locali e l'adozione di `cli.py` basato su Click.

**Architecture:** Modifica della documentazione delle regole architetturali in Markdown con esempi di codice Python e comandi shell, seguita dalla creazione del documento di censimento e checklist delle 22 skill presenti nella repository.

**Tech Stack:** Markdown, Python 3, Click

## Global Constraints

- Repository: `/Users/michele/workspace/capimichi-skills`
- Nessun percorso assoluto utente hardcoded (usare `$USER_SKILLS_DIR`, `$HOME` o `~`).
- Nessun virtualenv locale creato dentro la cartella del repository.
- Esecuzione standard basata su `python3 $USER_SKILLS_DIR/<skill>/cli.py <comando>`.
- Tutte le modifiche esistenti non devono rompere gli script legacy; la migrazione a `cli.py` sarà progressiva e tracciata dalla checklist.

---

### Task 1: Aggiornare `ADD_SKILL_RULES.md` con le regole Python, Venv e `cli.py` (Click)

**Files:**
- Modify: `/Users/michele/workspace/capimichi-skills/ADD_SKILL_RULES.md`

**Interfaces:**
- Consumes: Spec approvata in `docs/slim-superpowers/specs/2026-11-18-python-cli-standard-and-migration-design.md`
- Produces: Regole aggiornate in `ADD_SKILL_RULES.md` con sezioni su interprete Python standard, gestione dipendenze/venv e struttura `cli.py` con Click.

- [x] **Step 1: Leggere il contenuto attuale di `ADD_SKILL_RULES.md`**

Verificare i punti esatti dove inserire le nuove sezioni:
- Sezione 1.A (comandi d'esempio con `python3`)
- Nuova Sezione 3 o integrazione della Sezione 4 ("Struttura Obbligatoria di una Skill"): sostituzione di `argparse` con standard `cli.py` con Click.
- Nuova Sezione per "Runtime Python & Divieto di Virtualenv Locali".

- [x] **Step 2: Applicare le modifiche a `ADD_SKILL_RULES.md`**

Aggiungere:
1. Regola sull'interprete Python e gestione venv (divieto assoluto di cartelle `.venv` interne, rispetto del Python di sistema o ambiente attivo, segnalazione chiara dipendenze mancanti con `pip install ...`).
2. Regola dell'entrypoint unico `cli.py` basato su Click con `@click.group()` e sottocomandi `@cli.command()`, opzione `--help` e opzione `--json` ove opportuno.
3. Modello di separazione delle responsabilità (Pattern Facade: `cli.py` per la CLI, `client.py`/`browser.py` per la logica, `paths.py` per percorsi XDG).

- [x] **Step 3: Verificare il rendering e la correttezza del markdown di `ADD_SKILL_RULES.md`**

Run: `git diff ADD_SKILL_RULES.md`
Expected: Diff pulito con aggiunta chiara e formattata delle nuove regole.

---

### Task 2: Aggiornare `README.md` con il richiamo alle nuove regole e alla checklist

**Files:**
- Modify: `/Users/michele/workspace/capimichi-skills/README.md`

**Interfaces:**
- Consumes: Regole definite in `ADD_SKILL_RULES.md`
- Produces: Sezione "Struttura della Repository & Regole" aggiornata in `README.md` con rimando a `MIGRATION_CHECKLIST.md`.

- [x] **Step 1: Leggere la sezione finale di `README.md`**

Ispezionare le righe relative a "Struttura della Repository & Regole".

- [x] **Step 2: Aggiornare la sezione in `README.md`**

Includere:
- Riferimento all'entrypoint standard `cli.py` con Click e al runtime Python di sistema (senza venv locali).
- Link al nuovo file di audit e monitoraggio [`MIGRATION_CHECKLIST.md`](file://$USER_SKILLS_DIR/MIGRATION_CHECKLIST.md).

- [x] **Step 3: Verificare il diff di `README.md`**

Run: `git diff README.md`
Expected: Modifica circoscritta alla sezione di regole e note informative.

---

### Task 3: Creare `MIGRATION_CHECKLIST.md` nella root del repository

**Files:**
- Create: `/Users/michele/workspace/capimichi-skills/MIGRATION_CHECKLIST.md`

**Interfaces:**
- Consumes: Censimento delle 22 skill effettuato durante il brainstorming
- Produces: File di audit completo con criteri di conformità, tabella stato di tutte le skill e checklist operative per ciascuna.

- [x] **Step 1: Scrivere `MIGRATION_CHECKLIST.md`**

Il file deve contenere:
1. **Criteri di conformità**:
   - Presenza di `$USER_SKILLS_DIR/<skill>/cli.py` con interfaccia Click.
   - Nessun virtualenv locale presente.
   - Dipendenze gestite con messaggio esplicito (`pip install ...`).
   - Documentazione in `SKILL.md` allineata ai comandi `cli.py`.
2. **Tabella di censimento e stato delle 22 skill**:
   - Tier 1 (Quasi conformi / Singolo script): `ticktick`, `google-tasks`, `google-search-console`, `regali-noemi`, `spotify`, `whatsapp-backup`.
   - Tier 2 (Media complessità / Multi-script): `paperless`, `lubelogger`, `ibkr`, `trakt`, `nuvio`, `stremio`, `soulsync`, `mircrew-releases.org`, `amazon`, `amazon-music`, `lucida.to`, `monochrome.tf`.
   - Tier 3 (Alta complessità / Molti script ad-hoc): `worldfilia`, `meta`.
   - Solo documentazione (No script): `last.fm`, `listenbrainz`.
3. **Workflow standard di migrazione per agente/sviluppatore**:
   - Step 1: Creare/aggiornare `<skill>/cli.py` con Click.
   - Step 2: Testare con `python3 $USER_SKILLS_DIR/<skill>/cli.py --help`.
   - Step 3: Verificare esecuzione del comando reale.
   - Step 4: Aggiornare `SKILL.md` con i nuovi comandi unificati.
   - Step 5: Spuntare la skill nella checklist di questo file.
4. **Checklist puntuale con checkbox per ogni skill**.

- [x] **Step 2: Verificare l'esistenza del file e la correttezza dei link relativi**

Run: `ls -la /Users/michele/workspace/capimichi-skills/MIGRATION_CHECKLIST.md`
Expected: File creato e leggibile.

---

### Task 4: Verifica Finale e Integrità del Repository

**Files:**
- Check: `/Users/michele/workspace/capimichi-skills/ADD_SKILL_RULES.md`
- Check: `/Users/michele/workspace/capimichi-skills/README.md`
- Check: `/Users/michele/workspace/capimichi-skills/MIGRATION_CHECKLIST.md`

- [x] **Step 1: Eseguire `git status` per verificare i file modificati e aggiunti**

Run: `git -C /Users/michele/workspace/capimichi-skills status`
Expected: Solo `ADD_SKILL_RULES.md`, `README.md`, `MIGRATION_CHECKLIST.md` e la cartella `docs/` presenti nei cambiamenti.

- [x] **Step 2: Verificare che nessun venv o file non autorizzato sia stato introdotto**

Run: `find /Users/michele/workspace/capimichi-skills -maxdepth 2 -name "*venv*"`
Expected: Nessun output.

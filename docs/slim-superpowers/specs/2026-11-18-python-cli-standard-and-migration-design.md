# Design: Standard Python CLI (Click), Gestione Virtualenv & Audit di Migrazione Skill

**Data**: 2026-11-18  
**Repository**: `/Users/michele/workspace/capimichi-skills`  
**Stato**: Approvato dal Brainstorming, in attesa di piano di implementazione  

---

## 1. Obiettivo

Standardizzare lo sviluppo e l'esecuzione di tutte le skill presenti nel repository `capimichi-skills` adottando:
1. **Runtime Python dinamico**: esecuzione tramite `python3`, senza percorsi fissi a virtualenv e senza creare virtualenv locali (`.venv`) nelle skill.
2. **Standard CLI unificata con Click (`cli.py`)**: un solo punto di ingresso eseguibile per skill nella root della stessa (`$USER_SKILLS_DIR/<skill>/cli.py`), con comandi e sottocomandi chiari.
3. **Gestione pulita delle dipendenze**: utilizzo dell'ambiente Python attivo dell'utente; in caso di libreria mancante, restituzione di un messaggio chiaro indicante all'utente il comando di installazione (`pip install <pacchetto>`).
4. **Piano di Audit e Migrazione**: tracciamento dello stato attuale di tutte le 22 skill in un file dedicato `MIGRATION_CHECKLIST.md` nella root per guidare la migrazione incrementale.

---

## 2. Nuove Regole Architetturali

### 2.1 Runtime Python & Divieto di Virtualenv Locali
* **Interprete**: Gli script devono essere eseguiti con `python3 $USER_SKILLS_DIR/<skill>/cli.py <comando>`.
* **Zero Hardcoding**: È vietato cablare percorsi specifici a virtualenv (es. `~/.venv` o `/opt/homebrew/...`). Si utilizza l'interprete Python attualmente risolto dall'ambiente di sistema o di shell (`python3` / `sys.executable`).
* **Nessun venv locale**: Non devono mai essere create cartelle `.venv` o `venv` all'interno della directory delle skill o del repository.
* **Segnalazione dipendenze mancanti**: Se una dipendenza (`click`, `requests`, ecc.) non è installata, lo script deve intercettare l'errore o terminare con un messaggio esplicito all'utente contenente il comando di installazione (es. `pip install click`).

### 2.2 Standard `cli.py` con Click (Pattern Facade)
* **Entrypoint unico**: Ogni skill espone `$USER_SKILLS_DIR/<skill>/cli.py`.
* **Struttura dei comandi**:
  * Gruppo principale: `@click.group()`
  * Sottocomandi operativi: `@cli.command()` per ciascuna funzionalità offerta dal servizio.
  * Argomenti e opzioni documentati con parametro `help="..."`.
  * Supporto a `--json` o output strutturato dove utile per il consumo da parte di agenti AI.
* **Separazione dei moduli**:
  * `cli.py`: parsing CLI, gestione input/output utente, formattazione, cattura errori.
  * Moduli helper (`client.py`, `browser.py`, `paths.py`, `models.py`): logica di rete, chiamate API, automazione browser e gestione percorsi XDG.

---

## 3. Modifiche ai File di Documentazione

1. **`ADD_SKILL_RULES.md`**:
   * Aggiornamento della Sezione 4 ("Struttura Obbligatoria di una Skill"): sostituzione del riferimento generico ad `argparse` con l'obbligo di `cli.py` basato su Click.
   * Aggiunta di una sezione specifica per il Runtime Python, il divieto di venv locali e la gestione trasparente delle dipendenze.
   * Documentazione del pattern di invocazione standard `python3 $USER_SKILLS_DIR/<skill>/cli.py <comando>`.

2. **`README.md`**:
   * Aggiornamento della sezione "Struttura della Repository & Regole" per riflettere la presenza obbligatoria di `cli.py` come interfaccia CLI unificata e l'uso del Python di sistema/ambiente attivo.
   * Inserimento del riferimento a `MIGRATION_CHECKLIST.md` per il monitoraggio della conformità.

3. **`MIGRATION_CHECKLIST.md` (Nuovo file nella root)**:
   * Censimento completo delle 22 skill presenti.
   * Classificazione in 4 livelli di complessità:
     * **Tier 1 (Quasi conformi / Singolo script)**: `ticktick`, `google-tasks`, `google-search-console`, `regali-noemi`, `spotify`, `whatsapp-backup`.
     * **Tier 2 (Media complessità / Multi-script funzionali)**: `paperless`, `lubelogger`, `ibkr`, `trakt`, `nuvio`, `stremio`, `soulsync`, `mircrew-releases.org`, `amazon`, `amazon-music`, `lucida.to`, `monochrome.tf`.
     * **Tier 3 (Alta complessità / Molti script ad-hoc)**: `worldfilia`, `meta`.
     * **Solo documentazione (No Python)**: `last.fm`, `listenbrainz`.
   * Checklist operativa step-by-step per aggiornare ogni skill quando vi si mette mano.

---

## 4. Criteri di Accettazione

- [ ] `ADD_SKILL_RULES.md` aggiornato con le nuove regole (standard `cli.py` Click, divieto venv locali, dipendenze via pip).
- [ ] `README.md` aggiornato in sintesi con link alle regole e riferimento a `MIGRATION_CHECKLIST.md`.
- [ ] `MIGRATION_CHECKLIST.md` creato nella root con tutte le 22 skill censite e classificate con checklist operative.
- [ ] Nessuna rottura retrocompatibile immediata sugli script esistenti; la migrazione procederà secondo la checklist.

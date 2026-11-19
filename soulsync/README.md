# SoulSync Operations & Automation Skill

Questo modulo contiene documentazione tecnica, guide di troubleshooting e strumenti operativi per l'istanza **SoulSync** e la sua interazione con **Navidrome**, **slskd** e il filesystem.

---

## 📁 Contenuto del Modulo

* **[SKILL.md](file://$USER_SKILLS_DIR/soulsync/SKILL.md)**: Guida completa e strutturata che include:
  1. Architettura, percorsi di rete, database e punti di mount Docker.
  2. Comandi di ispezione dei log remoti.
  3. Diagnosi e risoluzione del problema **Dead File Cleaner** (disallineamento percorsi virtuali Subsonic di Navidrome).
  4. Logica di auto-pausa dei servizi di **Enrichment** (*Yield Policy* durante i download).
  5. Riferimento per le API REST di SoulSync.
* **[cli.py](file://$USER_SKILLS_DIR/soulsync/cli.py)**: CLI unificata con comandi per la gestione della wishlist (`list`, `export`), importazione MCP (`scan`, `identify`, `search`, `tracklist`, `fuzzy-match`, `import-track`) e log.
* **[client.py](file://$USER_SKILLS_DIR/soulsync/client.py)**: Client helper per chiamate API REST, export SQLite remoto e comandi container.

---

## 🚀 Esempi Rapidi d'Uso

### 1. Consultare la Wishlist:
```bash
python3 soulsync/cli.py wishlist list
```

### 2. Esportare tutte le tracce in Wishlist in CSV:
```bash
python3 soulsync/cli.py wishlist export
# oppure con destinazione personalizzata:
python3 soulsync/cli.py wishlist export -o ~/Downloads/wishlist.csv
```

### 3. Consultare i log remoti in tempo reale o filtrare errori:
```bash
python3 soulsync/cli.py logs --follow
python3 soulsync/cli.py logs --errors
```

### 3. Risoluzione Dead File Cleaner su Navidrome:
1. Aprire la Web UI di Navidrome $\rightarrow$ **Profilo** $\rightarrow$ **Players**.
2. Selezionare il client **SoulSync**.
3. Attivare la spunta **`Report Real Path`**.
4. Su SoulSync avviare un **Full Refresh** o **Deep Scan**.

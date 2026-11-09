# SoulSync Operations & Automation Skill

Questo modulo contiene documentazione tecnica, guide di troubleshooting e strumenti operativi per l'istanza **SoulSync** e la sua interazione con **Navidrome**, **slskd** e il filesystem.

---

## 📁 Contenuto del Modulo

* **[SKILL.md](file:///Users/michele/PycharmProjects/capimichi-skills/soulsync/SKILL.md)**: Guida completa e strutturata che include:
  1. Architettura, percorsi di rete, database e punti di mount Docker.
  2. Comandi di ispezione dei log remoti.
  3. Diagnosi e risoluzione del problema **Dead File Cleaner** (disallineamento percorsi virtuali Subsonic di Navidrome).
  4. Logica di auto-pausa dei servizi di **Enrichment** (*Yield Policy* durante i download).
  5. Riferimento per le API REST di SoulSync.
* **[export_wishlist_csv.py](file:///Users/michele/PycharmProjects/capimichi-skills/soulsync/export_wishlist_csv.py)**: Script Python per estrarre l'intero database della Wishlist (anche migliaia di tracce) e salvarlo in un file CSV formattato in `~/Downloads/`.
* **[list_wishlist.py](file:///Users/michele/PycharmProjects/capimichi-skills/soulsync/list_wishlist.py)**: Script per interrogare rapidamente l'API REST di SoulSync ed elencare i brani pendenti a terminale.

---

## 🚀 Esempi Rapidi d'Uso

### 1. Esportare tutte le tracce in Wishlist in CSV:
```bash
python3 export_wishlist_csv.py
```
*(Il file CSV verrà scaricato direttamente in `~/Downloads/wishlist_tracks.csv`)*

### 2. Consultare i log remoti in tempo reale:
```bash
ssh root@192.168.1.100 "tail -f /home/capimichi/docker/soulsync/logs/app.log"
```

### 3. Risoluzione Dead File Cleaner su Navidrome:
1. Aprire la Web UI di Navidrome $\rightarrow$ **Profilo** $\rightarrow$ **Players**.
2. Selezionare il client **SoulSync**.
3. Attivare la spunta **`Report Real Path`**.
4. Su SoulSync avviare un **Full Refresh** o **Deep Scan**.

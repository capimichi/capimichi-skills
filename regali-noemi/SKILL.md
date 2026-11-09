---
name: regali-noemi
description: >-
  Istruzioni operative, architettura e script per gestire e sincronizzare il foglio di calcolo dei regali per Noemi
  (Google Drive: googledrive-capimichi:PERSONALE/REGALI NOEMI).
---

# Regali Noemi - Gestione & Sincronizzazione

Questa skill descrive come consultare, aggiornare e sincronizzare in modo sicuro il foglio di calcolo dei regali per Noemi su Google Drive.

---

## 1. Posizione & Privacy (Zero Sorprese)

> [!CAUTION]
> Il file **NON DEVE MAI** essere spostato nella cartella `FAMIGLIA` o in qualsiasi directory condivisa con Noemi.

* **Remote rclone:** `googledrive-capimichi:`
* **Percorso remoto:** `googledrive-capimichi:PERSONALE/REGALI NOEMI`
* **MIME / Formato:** Foglio di calcolo Google / Excel (`.xlsx`)
* **ID File Drive (costante):** `1O4rpG0O6vHX_Kr3tBFs2vGjQKiuVmvg8`
* **URL di consultazione:** https://docs.google.com/spreadsheets/d/1O4rpG0O6vHX_Kr3tBFs2vGjQKiuVmvg8/edit

---

## 2. Architettura dei Fogli di Lavoro

Il documento è organizzato in 4 tab sinergiche:

```text
[ 📅 Date Ricorrenti ]   ➜ Le ricorrenze fisse dell'anno e i tempi di preavviso
         │
[ 📌 Gusti & Preferenze] ➜ La guida su cosa le piace (🟢 Sì), cosa evitare (🔴 No), o da verificare (❓)
         │
[ 💡 Catalogo Idee ]     ➜ Bacino idee concrete con link, fascia prezzo e conformità gusti
         │
[ 🗓️ Planning & Storico] ➜ Assegnazione idee ai prossimi eventi (💡 Proposta) e archivio acquisti reali (✅ Regalato)
```

### Dettaglio Schede:
1. **`📅 Date Ricorrenti`**
   - Compleanno (13 Feb), Festa della Donna (8 Mar), Festa della Mamma (2ª Dom Maggio), Anniversario (23 Set), Natale (25 Dic).
   - Definisce budget indicativo e preavviso consigliato.
2. **`📌 Gusti & Preferenze`**
   - Colonne: `Categoria` | `Ambito / Aspetto` | `Preferenza` | `Dettaglio / Regola` | `Note & Consigli Operativi`.
   - Preferenze confermate: `🟢 Sì / Preferito`, `🔴 No / Evitare`, `🟡 Note / Condizione`.
   - Idee da confermare con l'utente: `❓ Da confermare (Sì/No?)`.
3. **`💡 Catalogo Idee`**
   - Colonne: `ID Idea` | `Occasione Target` | `Categoria` | `Prodotto / Idea Regalo` | `Prezzo Stimato (€)` | `Stato Idea` | `Link / Dove trovarlo` | `Note di Conformità`.
   - Stati idea: `💡 Proposta`, `⭐ Approvata`, `Scartata`, `Già usata`.
4. **`🗓️ Planning & Storico`**
   - Colonne: `Data` (YYYY-MM-DD) | `Ricorrenza` | `Regalo Selezionato / Ipotesi` | `Categoria` | `Budget Stimato (€)` | `Spesa Reale (€)` | `Stato` | `Note / Dettagli Ordine`.
   - Disposto rigorosamente in **ordine cronologico da sopra a sotto**:
     - Parte dal primo evento dell'anno (`2026-02-13`) già regalato.
     - Prosegue nel corso del tempo fino ai prossimi eventi futuri (`2026-12-25`, `2027-02-13`, ecc.) come `💡 Proposta`.
   - Riga totale finale: formula automatica `=SUM(...)` per budget stimato e spesa reale.

---

## 3. Palette Colori delle Categorie (Pastello Tenue)

Ogni categoria ha uno sfondo distintivo pastello chiaro per una consultazione visiva rapida:

| Categoria | HEX Sfondo | Descrizione visiva |
| :--- | :--- | :--- |
| **Candele** | `#FDF2F2` | Rosa cipria tenue |
| **Prodotti corpo** | `#FFF7ED` | Arancio pesca chiaro |
| **Libri** | `#FEFCE8` | Giallo burro chiaro |
| **Accessori Lettura** | `#FEF9C3` | Giallo pastello tenue |
| **Harry Potter** | `#F0FDF4` | Verde menta chiarissimo |
| **Gift Card** | `#ECFDF5` | Smeraldo delicato |
| **Tisane & Tè** | `#F0F9FF` | Celeste chiarissimo |
| **Accessori Casa & Relax** | `#EFF6FF` | Azzurro polvere tenue |
| **Profumazioni Casa** | `#F5F3FF` | Lavanda chiarissimo |
| **Cura Mani & Labbra** | `#FAF5FF` | Lilla chiarissimo |
| **Dolci & Snack Coccola** | `#FFF1F2` | Rosa tenue |
| **Cancelleria & Planner** | `#F8FAFC` | Grigio perla chiaro |

---

## 4. Come Leggere e Aggiornare il File (Procedura In-Place)

Per non rompere l'ID del file di Google Drive o i preferiti dell'utente, **NON eliminare mai il file con `rclone deletefile`**. Bisogna sempre sovrascrivere direttamente in-place.

### A. Scaricare il foglio attuale (per lettura/modifica)
```bash
rclone copyto "googledrive-capimichi:PERSONALE/REGALI NOEMI" /tmp/REGALI_NOEMI.xlsx
```

### B. Modificare con Python (`openpyxl`)
Usare `uv run --with openpyxl python` per script veloci e isolati.
Quando si aggiungono righe o si aggiornano categorie, mantenere:
- Formattazione valuta `€ #,##0.00` per i prezzi.
- Colore pastello di sfondo della categoria tramite la mappa `cat_colors`.
- Bordi sottili `#D9D9D9` e allineamenti corretti.

### C. Caricare e sovrascrivere su Drive (Preserva l'ID)
```bash
rclone copyto /tmp/REGALI_NOEMI.xlsx "googledrive-capimichi:PERSONALE/REGALI NOEMI" \
  --drive-import-formats xlsx \
  --drive-allow-import-name-change -v
```

---

## 5. Casi d'Uso Tipici dell'Utente

1. **"Aggiungi un gusto / preferenza"**:
   - Scaricare `/tmp/REGALI_NOEMI.xlsx`, inserire la riga in `📌 Gusti & Preferenze` con il colore della categoria, salvare e ricaricare con `rclone copyto`.
2. **"Brainstorming / Proponimi regali"**:
   - Consultare `📌 Gusti & Preferenze` e `🗓️ Planning & Storico` (per non ripetere regali già fatti).
   - Aggiungere le proposte al `💡 Catalogo Idee` come `💡 Proposta`.
3. **"Ho comprato questo regalo"**:
   - In `🗓️ Planning & Storico`, impostare lo stato su `✅ Regalato`, inserire la spesa reale effettiva in colonna `Spesa Reale (€)` e segnare i dettagli dell'ordine nelle note.
4. **"Pianifica l'anno"**:
   - In `🗓️ Planning & Storico`, verificare che per ogni ricorrenza futura in `📅 Date Ricorrenti` ci sia una riga con un budget stimato.

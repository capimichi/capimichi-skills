---
name: whatsapp-backup
description: >-
  Utility e guida per processare, categorizzare e archiviare le esportazioni chat di WhatsApp (da iPhone/AirDrop)
  su OneDrive (onedrive-michele:Backup/WhatsApp) o altro cloud rclone in modo incrementale e strutturato (Chat, Media, Docs).
---

# WhatsApp Backup & Archival Skill

Questa skill permette di archiviare in modo incrementale e pulito le chat e i relativi media esportati da **WhatsApp (iOS/Android)** direttamente su **OneDrive** (o altro cloud configurato in `rclone`), liberando spazio sia su iPhone sia su iCloud.

---

## 1. Struttura delle cartelle su Cloud

Per ogni chat processata, l'archivio su OneDrive (`onedrive-michele:Backup/WhatsApp/`) viene organizzato secondo la convenzione concordata:

```text
onedrive-michele:Backup/WhatsApp/<Nome Chat>/
  ├── Chat/
  │   ├── Archives/
  │   │   ├── chat_2026-10-22.txt # File grezzo originale esportato in data odierna
  │   │   └── chat_2026-11-25.txt # Eventuali backup grezzi successivi
  │   └── chat.txt                # File UNIFICATO: unisce tutti gli archivi, deduplicato e ordinato
  ├── Media/
  │   ├── Foto/                   # Immagini (.jpg, .png, .heic, .webp, sticker)
  │   ├── Video/                  # Video e GIF animate (.mp4, .mov, ecc.)
  │   └── Audio/                  # Note vocali, audio (.opus, .m4a, .mp3, ecc.)
  └── Docs/                       # Documenti PDF, Excel, Word, vCard (.vcf), zip
```

---

## 2. Come esportare la chat dall'iPhone

1. Apri **WhatsApp** sull'iPhone ed entra nella chat desiderata.
2. Tocca il **nome della chat / gruppo** in alto.
3. Scorri in basso e tocca **Esporta chat**.
4. Scegli **Allega file multimediali** *(importante per includere foto, video e note vocali)*.
5. Dal menu di condivisione, seleziona **AirDrop** e invia al tuo **Mac**.
6. Il file arriverà nella cartella `~/Downloads` (es. `WhatsApp Chat - Nome Chat.zip`).

---

## 3. Uso dello script CLI `backup_whatsapp.py`

Lo script si trova in:
```text
/Users/michele/PycharmProjects/capimichi-skills/whatsapp-backup/backup_whatsapp.py
```

### Sintassi base
```bash
python3 /Users/michele/PycharmProjects/capimichi-skills/whatsapp-backup/backup_whatsapp.py "/path/to/WhatsApp Chat - Nome.zip"
```

Lo script:
1. Rileva automaticamente il nome pulito della chat (convertendo prefissi WhatsApp e caratteri come `/` o `_` in `-`).
2. Scompatta ed etichetta tutti i file in un'area di staging temporanea.
3. Rinomina il file di testo in `Chat/chat_YYYY-MM-DD.txt`.
4. Suddivide i media in `Media/Foto`, `Media/Video`, `Media/Audio` e i documenti in `Docs/`.
5. Esegue `rclone copy` su `onedrive-michele:Backup/WhatsApp/<Nome Chat>/`.
6. Cancella automaticamente i file temporanei al termine.

### Opzioni utili

* `--dry-run`: simula l'operazione senza caricare nulla:
  ```bash
  python3 backup_whatsapp.py "~/Downloads/WhatsApp Chat - Nome.zip" --dry-run
  ```
* `-n "Nome Personalizzato"`: forza un nome cartella specifico:
  ```bash
  python3 backup_whatsapp.py "~/Downloads/archivio.zip" -n "Progetto Alpha"
  ```
* `-r "remote:path"`: cambia destinazione (default: `onedrive-michele:Backup/WhatsApp`).
* `--no-media-subfolders`: raggruppa tutti i file multimediali direttamente in `Media/` senza le sottocartelle Foto/Video/Audio.

---

## 4. Gestione Incrementale (Backup nel tempo)

* **Se ricarichi la stessa chat dopo 1 o più mesi**:
  Grazie a `rclone copy`, lo script controlla dimensione e integrità: tutti i file già presenti su OneDrive **vengono saltati istantaneamente** senza riscaricarli né duplicarli. Solo le nuove foto, i nuovi video e la nuova cronologia chat vengono trasferiti.
* **Dopo aver fatto il backup**:
  Sull'iPhone puoi andare in *Impostazioni ➔ Spazio e dati ➔ Gestisci spazio ➔ [Nome Chat]* ed eliminare i media pesanti per liberare memoria locale e spazio su iCloud.

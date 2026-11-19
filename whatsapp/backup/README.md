# WhatsApp Backup & Cloud Archiver

Script di utilità per archiviare in modo incrementale chat e file multimediali WhatsApp su Cloud (OneDrive / Google Drive) tramite `rclone`.

## Caratteristiche
- **Smistamento automatico**: divide file in `Chat/`, `Media/Foto/`, `Media/Video/`, `Media/Audio/`, `Docs/`.
- **Deduplicazione incrementale**: i file già caricati in precedenza non vengono riscaricati né duplicati.
- **Supporto ZIP e cartelle**: accetta direttamente il file `.zip` generato da AirDrop.
- **Zero dipendenze esterne**: usa esclusivamente la libreria standard di Python 3 e `rclone`.

## Esempio rapido
```bash
python3 backup_whatsapp.py "~/Downloads/WhatsApp Chat - The Space _ The Strategy.zip"
```

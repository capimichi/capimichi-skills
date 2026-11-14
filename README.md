# Capimichi Skills Hub

Directory centrale delle skill operative e automazioni personali per agenti AI.

> **Regola per gli Agenti**: Consulta questa tabella per individuare la skill corretta prima di compiere azioni o cercare script. Leggi il rispettivo `SKILL.md` nella sottocartella scelta per le istruzioni operative dettagliate.

---

## 📌 Indice delle Skill & Trigger di Utilizzo

| Categoria | Skill | Quando usarla (Trigger Operativo) | Note / Priorità |
| :--- | :--- | :--- | :--- |
| **Task & To-Do** | [`ticktick`](ticktick/SKILL.md) | **Se l'utente vuole segnare, leggere, completare, filtrare o gestire task, to-do list, scadenze, promemoria o progetti.** | ⭐ **Prioritaria / Predefinita** |
| | [`google-tasks`](google-tasks/SKILL.md) | Gestione task su Google Tasks. | Usare solo se esplicitamente richiesto "Google Tasks". |
| **Media & Video** | [`nuvio`](nuvio/SKILL.md) | Consultazione cronologia di visione, film e serie TV salvati su Nuvio (Supabase API). | |
| | [`stremio`](stremio/SKILL.md) | Consultazione libreria, progressi ed episodi visti su Stremio. | |
| | [`trakt`](trakt/SKILL.md) | Sincronizzazione visioni, scrobbling e tracciamento film/serie su Trakt.tv. | Include script sync con Nuvio. |
| | [`mircrew-releases.org`](mircrew-releases.org/SKILL.md) | Ricerca release, download e link magnet/torrent su Mircrew via CloakBrowser. | |
| **Musica & Audio** | [`soulsync`](soulsync/SKILL.md) | Gestione istanza SoulSync, Navidrome e slskd (wishlist, import brani, storage locale). | Server `192.168.1.100`. |
| | [`spotify`](spotify/SKILL.md) | Ricerca pubblica e scraping di brani, album o artisti su Spotify (senza login). | |
| | [`amazon-music`](amazon-music/SKILL.md) | Automazione e ricerca album, tracce e link su Amazon Music via CloakBrowser. | |
| | [`listenbrainz`](listenbrainz/SKILL.md) | Gestione e creazione playlist su ListenBrainz tramite API REST. | |
| | [`last.fm`](last.fm/SKILL.md) | Gestione playlist su Last.fm con navigazione stealth. | |
| | [`lucida.to`](lucida.to/SKILL.md) | Download tracce audio ad alta qualità da Lucida.to via CloakBrowser. | |
| | [`monochrome.tf`](monochrome.tf/SKILL.md) | Download e interazione con Monochrome.tf via CloakBrowser. | |
| **Marketing & Ads** | [`worldfilia`](worldfilia/SKILL.md) | Gestione campagne affiliate, controllo conversioni, report lead e pixel su Worldfilia. | Contiene piani strategici dedicati. |
| | [`meta`](meta/SKILL.md) | Automazione Meta Ads Manager, campagne e Business Suite tramite CloakBrowser. | |
| **Documenti & Personale** | [`paperless`](paperless/SKILL.md) | Ricerca documenti, fatture, scontrini, testo OCR, upload e download su Paperless-ngx. | `paperless.michelecapicchioni.com` |
| | [`amazon`](amazon/SKILL.md) | Navigazione Amazon.it, carrello, verifica ordini e prezzi con sessione persistente. | |
| | [`regali-noemi`](regali-noemi/SKILL.md) | Consultazione e aggiornamento del foglio di calcolo idee/regali per Noemi su Google Drive. | |
| | [`whatsapp-backup`](whatsapp-backup/SKILL.md) | Elaborazione, categorizzazione e archiviazione backup chat WhatsApp su OneDrive (rclone). | |

---

## 📂 Struttura della Repository & Regole

* Consulta [**`ADD_SKILL_RULES.md`**](file://$SKILL_PROJECT_PATH/ADD_SKILL_RULES.md) per le regole architetturali obbligatorie (standard percorsi `$SKILL_PROJECT_PATH`, agnosticità verso i dotfile/chezmoi, e convenzioni XDG).
* Ogni skill è una cartella autonoma contenente:
  * `SKILL.md`: Guida operativa, configurazione credenziali e workflow.
  * Script Python CLI / helper browser dedicati all'automazione del servizio.

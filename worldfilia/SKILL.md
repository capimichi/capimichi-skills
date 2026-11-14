---
name: Worldfilia Automation Skill
description: Istruzioni e script per automatizzare l'interazione con Worldfilia tramite CloakBrowser, gestione della persistenza della sessione 2FA e conformità alle specifiche XDG.
---

# Worldfilia Automation Skill

Questa skill fornisce gli strumenti per automatizzare l'accesso e l'interazione con la piattaforma affiliati di **Worldfilia** ([portal.worldfilia.net](https://portal.worldfilia.net/)) utilizzando **Python** e **CloakBrowser** (browser stealth basato su Playwright per superare controlli anti-bot).

Poiché Worldfilia richiede l'autenticazione a due fattori (**2FA**), la sessione viene salvata in modo persistente seguendo le specifiche **XDG Base Directory**.

---

## 🔐 1. Configurazione Variabili d'Ambiente & Standard XDG

La skill legge le credenziali e i token di accesso esclusivamente da **variabili d'ambiente**:

### Variabili d'ambiente supportate:
| Variabile | Scopo | Note |
| :--- | :--- | :--- |
| `WORLDFILIA_API_KEY` (o `WORLDFILIA_TOKEN`) | Accesso API GraphQL e REST Performance | Token generato in `/publisher/service/keys` |
| `WORLDFILIA_USERNAME` | Nome utente o email di accesso | Usato per l'automazione login via browser |
| `WORLDFILIA_PASSWORD` | Password di accesso | Usato per l'automazione login via browser |
| `WORLDFILIA_TOTP_SECRET` | *(Opzionale)* Chiave segreta TOTP | Permette la generazione automatica del codice 2FA |
| `WORLDFILIA_DATA_DIR` | *(Opzionale)* Percorso base dati personalizzato | Default conforme a `XDG_DATA_HOME` |

Tutti i dati persistenti e temporanei risiedono nella home dell'utente rispettando le specifiche **XDG Base Directory**:

| Directory | Percorso Predefinito | Scopo |
| :--- | :--- | :--- |
| **`XDG_DATA_HOME`** | `~/.local/share/worldfilia/` | Root dei dati persistenti dell'applicazione |
| └─ **`browser_session/`** | `~/.local/share/worldfilia/browser_session/` | **Profilo Chromium / CloakBrowser**: cookie, session storage, token e 2FA |
| └─ *(altri dati)* | `~/.local/share/worldfilia/...` | Eventuali esportazioni, report CSV o dati salvati |
| **`XDG_CACHE_HOME`** | `~/.cache/worldfilia/` | Screenshot di debug (`.png`), dump HTML di analisi DOM |

---

## 🚀 2. API Ufficiale Worldfilia (GraphQL & REST Performance)

Worldfilia mette a disposizione una suite di API ufficiali per gli affiliati ([documentazione ufficiale](https://portal.worldfilia.net/publisher/service/docs)):

* **Schema GraphQL:** [`wf_schema.gql`](file://$USER_SKILLS_DIR/worldfilia/wf_schema.gql)
* **Endpoint GraphQL:** `https://portal-api.worldfilia.net/graphql` (autenticazione tramite parametro `token: "<APIKEY>"`)
* **Endpoint REST Performance:** `https://portal-api.worldfilia.net/performance` (autenticazione tramite header `Authorization: Bearer <APIKEY>`)

### Client Python & Script CLI della Skill:
* [`api_client.py`](file://$USER_SKILLS_DIR/worldfilia/api_client.py): Wrapper completo (`WorldfiliaAPI`) basato sulla libreria standard `urllib` (nessuna dipendenza esterna).
* [`api_get_campaigns.py`](file://$USER_SKILLS_DIR/worldfilia/api_get_campaigns.py): CLI per interrogare, filtrare per parola chiave e ordinare per ranking le campagne con relative landing page.
  ```bash
  python3 worldfilia/api_get_campaigns.py --top --limit 10
  python3 worldfilia/api_get_campaigns.py --search "Rikrestin"
  ```
* [`api_get_performance.py`](file://$USER_SKILLS_DIR/worldfilia/api_get_performance.py): CLI per estrarre statistiche aggregate (click, conversioni, vendite approvate, EPC, CR, commissioni):
  ```bash
  python3 worldfilia/api_get_performance.py --today
  python3 worldfilia/api_get_performance.py --yesterday
  python3 worldfilia/api_get_performance.py --from-date 2026-11-01 --to-date 2026-11-07
  ```
* [`api_get_links.py`](file://$USER_SKILLS_DIR/worldfilia/api_get_links.py): CLI per consultare i link affiliato tracciati associati all'account:
  ```bash
  python3 worldfilia/api_get_links.py --limit 20
  ```

---

## 🛠️ 3. File e Script della Skill

I file sono organizzati nella directory [worldfilia/](file://$USER_SKILLS_DIR/worldfilia):

*   [api_client.py](file://$USER_SKILLS_DIR/worldfilia/api_client.py): Client ufficiale Python per GraphQL e REST Performance.
*   [api_get_campaigns.py](file://$USER_SKILLS_DIR/worldfilia/api_get_campaigns.py): CLI campagne via API.
*   [api_get_performance.py](file://$USER_SKILLS_DIR/worldfilia/api_get_performance.py): CLI performance/report via API.
*   [api_get_links.py](file://$USER_SKILLS_DIR/worldfilia/api_get_links.py): CLI link affiliato via API.
*   [paths.py](file://$USER_SKILLS_DIR/worldfilia/paths.py): Helper per calcolare i percorsi XDG, estrarre credenziali/API Key e calcolare TOTP.
*   [browser.py](file://$USER_SKILLS_DIR/worldfilia/browser.py): Factory function per istanziare CloakBrowser con il profilo persistente e viewport nativo.
*   [login.py](file://$USER_SKILLS_DIR/worldfilia/login.py): Script di login browser per operazioni che richiedono interfaccia web (es. iniezione pixel).
*   [explore.py](file://$USER_SKILLS_DIR/worldfilia/explore.py): Verifica sessione e screenshot di debug.
*   [set_pixel.py](file://$USER_SKILLS_DIR/worldfilia/set_pixel.py): Iniezione codice Meta Pixel / Postback (evento `Purchase` dinamico) nella sezione `ON SALE` della campagna via browser.
*   [set_click_pixel.py](file://$USER_SKILLS_DIR/worldfilia/set_click_pixel.py): Iniezione codice Meta Pixel nella sezione `ON CLICK` della campagna via browser.

---

## 🔐 3. Flusso di Login & 2FA

Lo script `login.py` gestisce l'accesso combinando le credenziali env e la persistenza browser:

1. Se presenti `WORLDFILIA_USERNAME` e `WORLDFILIA_PASSWORD`, compila automaticamente i campi della pagina di login.
2. Se è presente `WORLDFILIA_TOTP_SECRET`, calcola ed inserisce automaticamente il codice 2FA a 6 cifre con `pyotp`.
3. Se 2FA è via email o richiede conferma manuale, l'utente può inserirlo a video.
4. Una volta visualizzata la dashboard (`/publisher`), la sessione completa viene salvata in `~/.local/share/worldfilia/browser_session/`.


---

## 🚀 4. Esplorazione e Automazione Successiva

Una volta salvata la sessione, non è più necessario reinserire la password né il codice 2FA ad ogni esecuzione.

### Verificare la sessione e analizzare la dashboard:
```bash
python3 worldfilia/explore.py
```
Per eseguire in modalità headless (senza interfaccia grafica):
```bash
python3 worldfilia/explore.py --headless
```

Lo script genererà in `~/.cache/worldfilia/`:
* `dashboard_explore.png` (screenshot dell'interfaccia)
* `dashboard_explore.html` (dump HTML della pagina caricata)

---

## 🗺️ 5. Mappa delle Pagine e Sezioni Note

Dall'analisi della dashboard autenticata, le sezioni principali sono accessibili ai seguenti percorsi relativi di `https://portal.worldfilia.net`:

| Sezione | Path URL | Descrizione |
| :--- | :--- | :--- |
| **Dashboard** | `/publisher` | Vista d'insieme, metriche del periodo (Oggi, Ieri, Mese, ecc.) |
| **Campagne** | `/publisher/campaigns` | Elenco delle offerte e campagne disponibili da promuovere |
| **Links** | `/publisher/links` | Gestione e tracciamento dei link affiliato |
| **Performance** | `/publisher/reports/performance` | Report dettagliato sulle performance di traffico |
| **Click** | `/publisher/reports/clicks` | Registro click in tempo reale |
| **Conversioni** | `/publisher/reports/transactions` | Dettaglio conversioni e commissioni generate |
| **Leads** | `/publisher/reports/leads` | Report contatti/lead generati |
| **Quality Check** | `/publisher/reports/quality` | Valutazione qualità del traffico |
| **Pagamenti** | `/publisher/payments` | Storico fatture, stato pagamenti e richieste incasso |
| **Trasferimenti** | `/publisher/transfers` | Movimenti e trasferimenti fondi |
| **Profilo** | `/publisher/profile` | Dati account affiliato |

---

## 📊 6. Metriche Dashboard e Filtri Temporali

Nella vista principale (`/publisher`) sono presenti i seguenti indicatori e comandi:

### Filtri Temporali Rapidi:
* `Oggi`
* `Ieri`
* `Mese`
* `Ultimi 7gg`
* `Ultimi 30gg`
* `Ultimo mese`

### Metriche KPI Chiave Monitorate:
* **Click**: Numero totale di click registrati nel periodo selezionato.
* **Leads**: Numero di lead generati.
* **Commissioni**: Guadagno maturato (€).
* **CR (Conversion Rate)**: Tasso di conversione percentuale (Conversioni / Click).
* **EPC (Earnings Per Click)**: Guadagno medio generato per singolo click (€).

---

## 🎯 7. Sezione Campagne e API GraphQL

La sezione `/publisher/campaigns` è gestita interamente tramite un backend **GraphQL**:

*   **Endpoint API:** `https://portal-api.worldfilia.net/graphql`
*   **Metodo:** `POST`
*   **Autenticazione:** Cookie di sessione (in particolare il cookie `at` di Worldfilia e token di protezione bot Cloudflare), inviati con `credentials: 'include'`.

### Meccanismo di Paginazione:
Worldfilia adotta una paginazione **cursor-based**:
*   `first: Int`: Numero di elementi da recuperare per pagina (default interfaccia: `10`, ma scalabile ad es. a `50`).
*   `after: { id: <last_id> }`: Cursore per avanzare alla pagina successiva partendo dall'ID dell'ultima campagna vista.
*   `orderBy: { created: "desc" }`: Ordinamento predefinito.
*   `filter`: Filtri di stato (`status: { not: { equals: "S" } }`), per nazione (`Country: { alpha2: { equals: "IT" } }`), categoria o ricerca testuale.

### Esempio Query GraphQL:
```graphql
query campaigns($filter: CampaignWhereInput!, $first: Int, $after: CampaignWhereUniqueInput, $orderBy: [CampaignOrderByWithRelationInput!]) {
  campaigns(where: $filter, first: $first, after: $after, orderBy: $orderBy) {
    id
    name
    logoUrl
    price
    currency
    commission
    status
    created
    Country {
      id
      name
      alpha2
    }
  }
}
```

### Script di Recupero Campagne:
È disponibile lo script helper [**`worldfilia/get_campaigns.py`**](file://$USER_SKILLS_DIR/worldfilia/get_campaigns.py):
```bash
python3 worldfilia/get_campaigns.py
```
Consente di estrarre e filtrare velocemente le campagne con paginazione nativa senza dover simulare click sui bottoni dell'interfaccia.

---

## 🎛️ 8. Mappatura Completa Filtri Campagne (Drawer / Sidebar)

Nel pannello laterale dei filtri della sezione Campagne (`div.view > div.mb-44`) sono disponibili i seguenti filtri:

### A. Switch Rapidi (Toggle Switch)
*   **Mostra solo campagne in scadenza** (`react-switch`): filtra le offerte che hanno una data di scadenza imminente (`expiration != null`).
*   **Mostra solo campagne con nuovi media** (`react-switch`): filtra le campagne che hanno creatività/landing/banner aggiornati di recente (`last_media`).
*   **Mostra solo le mie campagne** (`react-switch`): limita la vista alle campagne già attivate o associate al profilo affiliato.

### B. Sezioni a Tendina (Collapsible / Accordion)

| Sezione Filtro | Tipo di Controllo UI | Modalità & Opzioni | Azioni Disponibili | Mappatura GraphQL stimata |
| :--- | :--- | :--- | :--- | :--- |
| **Lista preferiti** | Dropdown / Multiselect con barra di ricerca | Campo di ricerca (`placeholder="Cerca..."`) | `RESET` | `Bookmarks: { has: ... }` |
| **Stato** | Dropdown / Multiselect | Selezione multipla stati campagna (es. Attiva, Pausa, ecc.) | `RESET` | `status: { in: [...] }` / `{ equals: "A" }` |
| **Nome** | Testuale con operatore a tab | **Tab:** `Uguale` (equals), `Come` (contains), `Non uguale` (not equals)<br>Input di testo | `RESET`<br>`+ Aggiungi` (regole multiple) | `name: { contains: ... }` / `{ equals: ... }` |
| **Categoria** | Dropdown / Multiselect con barra di ricerca | Campo di ricerca (`placeholder="Cerca..."`) su elenco categorie | `RESET` | `Category: { is: { id: { in: [...] } } }` |
| **Tempi di pagamento**| Dropdown / Multiselect | Selezione tempi di liquidazione | `RESET` | `payment_terms: { in: [...] }` |
| **Ranking** | Slider a due estremi (`rc-slider`) | Range numerico da **0** a **5** con maniglie min e max | `RESET` | `ranking_value: { gte: min, lte: max }` |
| **Tolleranza** | Dropdown / Multiselect | Margine percentuale di tolleranza lead | `RESET` | `tolerance: { equals: ... }` |
| **Commissione** | Numerico con tab modalità | **Tab:** `Intervallo` (`[min] - [max]`) oppure `Uguale`<br>Campi `type="number"` | `RESET`<br>`+ Aggiungi` | `commission: { gte: min, lte: max }` |
| **Prezzo** | Numerico con tab modalità | **Tab:** `Intervallo` (`[min] - [max]`) oppure `Uguale`<br>Campi `type="number"` | `RESET`<br>`+ Aggiungi` | `price: { gte: min, lte: max }` |
| **Nazione** | Dropdown / Multiselect con barra di ricerca | Campo di ricerca (`placeholder="Cerca..."`) con selezione codici ISO / Paesi | `RESET` | `Country: { alpha2: { equals: "IT" } }` |

---

## 🔎 9. Dettaglio Singola Campagna & Generazione Link Affiliato

Ogni campagna ha una pagina dedicata accessibile all'URL:
`https://portal.worldfilia.net/publisher/campaigns/<campaign_id>`

### Interfaccia Utente e Tab:
*   **Scheda Principale:** Titolo, nazione target, categorie, prezzo di vendita (€), commissione affiliato CPA (€), tempi di pagamento (giorni) e tolleranza.
*   **Regole & Restrizioni:** Eventuali divieti o limitazioni di traffico (es. *"È vietata la promozione della campagna su TikTok"* o restrizioni geografiche).
*   **Tab Disponibili:**
    *   `Descrizione`: Note di marketing e linee guida operative.
    *   `Landing`: Elenco delle landing page con anteprima grafica JPG, pulsanti per diverse varianti (es. `IFRAME`, `IFRAME Small`) e codice tracciamento.
    *   `Postbacks/Pixels`: Configurazione di pixel di tracciamento e webhooks personalizzati per le conversioni.
    *   `Conversioni`: Log delle conversioni registrate specificamente su questa offerta.
*   **Campagne Ristrette:** Se la campagna ha `restricted: true`, l'interfaccia mostra il bottone **`Richiedi Accesso`**. Una volta inviata la richiesta (`requested: true`), l'affiliato attende l'approvazione del manager prima di poter prelevare i link.

### Query GraphQL Dettaglio Singola Campagna:
```graphql
query campaign($filter: CampaignWhereUniqueInput!) {
  campaign(where: $filter) {
    id
    name
    description
    price
    currency
    commission
    status
    restricted
    requested
    payment_times
    tolerance
    Landing
    Country {
      id
      name
      alpha2
    }
    CampaignCategory {
      Category {
        id
        name
      }
    }
    Advertiser {
      id
      name
    }
  }
}
```

### Struttura del Link di Tracciamento Affiliato:
I link di tracciamento sono archiviati nell'array `Landing` sotto forma di template:
```text
https://iframe.affiliatenetwork.link/manager/inventory/buy/<slug>?ref=[[pubid]]&aff_sub1=[[subid1]]&aff_sub2=[[subid2]]
```
*   `[[pubid]]`: viene sostituito automaticamente dal `pubId` dell'affiliato (ottenibile tramite la mutation `login`).
*   `[[subid1]]` / `[[subid2]]`: parametri opzionali per tracciare sorgenti di traffico (es. Facebook, Google, campagne specifiche).

### Script Helper Dedicato:
È disponibile lo script [**`worldfilia/get_campaign_detail.py`**](file://$USER_SKILLS_DIR/worldfilia/get_campaign_detail.py):
```bash
python3 worldfilia/get_campaign_detail.py 5598
```
Questo script estrae automaticamente tutti i dati dell'offerta, verifica i permessi di accesso, recupera le landing page e genera gli URL di tracciamento già compilati con il proprio `pubId`.






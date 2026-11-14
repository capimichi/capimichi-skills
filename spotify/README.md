# Spotify public search automation

Questo modulo permette di effettuare ricerche pubbliche su **Spotify** senza necessità di login o chiavi API sviluppatore, estraendo brani (con titolo, artisti e durata), album ed artisti rilevanti.

---

## 1. File del Modulo

*   **[SKILL.md](file://$SKILL_PROJECT_PATH/spotify/SKILL.md)**: Guida tecnica che descrive il funzionamento degli URL di ricerca di Spotify, i selettori CSS e come estrarre le informazioni da Playwright.
*   **[search.py](file://$SKILL_PROJECT_PATH/spotify/search.py)**: Script Python pronto all'uso per cercare su Spotify ed elencare i risultati ordinati.

---

## 2. Istruzioni per l'Uso

Per eseguire una ricerca di test direttamente dal terminale:
```bash
python3 spotify/search.py "Sergio Mendes Funky Bahia"
```

### Esempio di Output:
```text
=== RISULTATO PIÙ RILEVANTE ===
  Testo: Funky Bahia |  | Sérgio Mendes, will.i.am, Siedah Garrett
  Link: https://open.spotify.com/intl-it/artist/65c5si0ePAwkOCn4M35Ho7
--------------------------------------------------

=== BRANI TROVATI ===
[1] Funky Bahia
    Artisti: Sérgio Mendes, will.i.am, Siedah Garrett
    Durata: 3:58
    Link: https://open.spotify.com/intl-it/track/5nCteQT8lp1SyTes2S2Ime
...
```

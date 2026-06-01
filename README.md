---

## Issue #3: Query Analitiche Avanzate (Aggregation Pipeline)

Per estrarre insight statistici dal database e valutare la flessibilità del modello documentale, sono state progettate e implementate delle **Aggregation Pipeline** complesse all'interno dello script `query_analytics.py`. Le query sfruttano gli operatori nativi di MongoDB per manipolare gli array ed eseguire aggregazioni efficienti.

### 1. Analisi dei Generi più Apprezzati
* **Obiettivo concettuale:** Identificare i 10 generi di anime che ottengono la valutazione media più alta da parte degli utenti, escludendo le nicchie troppo piccole.
* **Operatori utilizzati:** `$unwind` (per scompattare l'array `genres`), `$group` (per calcolare media dello score e conteggio), `$match` (per filtrare generi con almeno 5 anime), `$sort` (per ordinare dal voto più alto) e `$project` (per formattare e arrotondare l'output).

### 2. Performance degli Studi di Produzione
* **Obiettivo concettuale:** Determinare la Top 5 degli studi di produzione in base al volume totale di episodi rilasciati nel catalogo, monitorando il loro punteggio medio globale.
* **Operatori utilizzati:** `$group` (per sommare gli episodi e calcolare lo score medio per ogni `studio`), `$match` (per escludere dati sconosciuti), `$sort` e `$limit` (per isolare i primi 5 risultati).

### 3. Cross-Analytics Geografica degli Utenti
* **Obiettivo concettuale:** Analizzare la distribuzione geografica degli utenti, estraendo le 5 località con la maggiore densità di profili registrati e valutando la propensione al voto medio degli utenti di quelle aree.
* **Operatori utilizzati:** `$match` (per ignorare i dati mancanti), `$group` (per contare gli utenti e fare la media del loro `stats_mean_score`), `$sort` e `$limit`.

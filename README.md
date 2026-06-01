# nosql-anime-analytics
Progetto Basi di Dati 2 - Catalogo NoSQL per MyAnimeList
L'obiettivo è l'analisi dei dati del catalogo di MyAnimeList utilizzando un database NoSQL (MongoDB), valutando le performance e la flessibilità del modello documentale rispetto al modello relazionale.

##Architettura e Schema dei Documenti

I dati estratti dai dataset originali di Kaggle sono stati denormalizzati e ristrutturati per sfruttare al meglio i pattern nativi di MongoDB (*Embedding* e *Referencing*).

### 1. Collezione `anime`
Per i generi dell'anime è stato applicato il **Pattern di Embedding**, trasformando la stringa piatta del CSV in un array di stringhe JSON. Questo permette di indicizzare e interrogare i generi in modo nativo ed efficiente.

```json
{
  "_id": { "$oid": "665b1234abcde56789012345" },
  "anime_id": 11013,
  "title": "Inu x Boku SS",
  "type": "TV",
  "studio": "David Production",
  "episodes": 12,
  "score": 7.63,
  "genre": ["Comedy", "Supernatural", "Romance", "Shounen"],
  "status": "Finished Airing"
}
```
### 2. Collezione users.
```json
{
  "_id": { "$oid": "665b1234abcde56789012346" },
  "user_id": 2255153,
  "username": "karthiga",
  "gender": "Female",
  "location": "Chennai, India",
  "user_completed": 49,
  "stats_mean_score": 7.43
}
```
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
# nosql-anime-analytics
Progetto Basi di Dati 2 - Catalogo NoSQL per MyAnimeList
L'obiettivo è l'analisi dei dati del catalogo di MyAnimeList utilizzando un database NoSQL (MongoDB), valutando le performance e la flessibilità del modello documentale rispetto al modello relazionale.

##Architettura e Schema dei Documenti

I dati estratti dai dataset originali di Kaggle sono stati denormalizzati e ristrutturati per sfruttare al meglio i pattern nativi di MongoDB (*Embedding* e *Referencing*).

### 1. Collezione `animes`
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
  "genres": ["Comedy", "Supernatural", "Romance", "Shounen"],
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

---

##  Issue #5: Creazione Indici di Ottimizzazione e Esecuzione Benchmark

Per valutare l'efficienza del database NoSQL e l'impatto degli indici sulle performance delle Aggregation Pipeline, è stato implementato lo script `query_benchmark.py`. Lo script esegue un test comparativo calcolando il tempo medio di esecuzione (su 10 iterazioni stabili) prima e dopo l'applicazione degli indici.

###  Strategia di Indicizzazione
Sono stati introdotti i seguenti indici mirati sulle collezioni:
1. **`animes` (Campo singolo):** `genres` (ASC) per ottimizzare l'operazione di `$unwind`.
2. **`animes` (Composto):** `studio` (ASC) e `score` (DESC) per supportare il raggruppamento e l'ordinamento degli studi di produzione.
3. **`users` (Campo singolo):** `location` (ASC) per velocizzare il filtraggio geografico iniziale.

###  Risultati del Benchmark (Dataset di Campionamento)

| Query | Tempo Medio Pre-Indice | Tempo Medio Post-Indice | Delta % |
| :--- | :--- | :--- | :--- |
| **Q1 (Generi)** | 12.22 ms | 12.31 ms | -0.7% |
| **Q2 (Studi)** | 8.73 ms | 16.50 ms | -89.0% |
| **Q3 (Utenti)** | 153.82 ms | 249.38 ms | -62.1% |

### Analisi Critica dei Risultati (Considerazioni per l'Esame)
L'apparente peggioramento prestazionale registrato nei test evidenzia un comportamento tipico ed ampiamente documentato dei DBMS documentali:
* **Overhead su Piccoli Dataset:** Lavorando su un campione ridotto di dati, la scansione sequenziale in memoria RAM (`COLLSCAN`) risulta paradossalmente più efficiente rispetto alla navigazione della struttura ad albero (B-Tree) dell'indice (`IXSCAN`), a causa dei tempi di lookup dei puntatori ai blocchi di memoria.
* **Aggregazioni Intensive:** Poiché le query eseguono operazioni di raggruppamento globale (`$group`) e scompattamento di array (`$unwind`) che coinvlgono la quasi totalità dei documenti del campione, l'indice non può tagliare il costo computazionale del calcolo delle medie matematiche, il quale grava interamente sulla RAM/CPU.
* **Scalabilità:** L'efficacia di tale indicizzazione si manifesterebbe in scenari di produzione reali su base multi-gigabyte, dove un `COLLSCAN` su disco risulterebbe distruttivo per i tempi di latenza.

---

## Issue #7: Implementazione API REST

È stato implementato un backend REST in Python tramite **FastAPI**, collegato al database MongoDB `nosql_anime_analytics`.  
Le API permettono di interrogare il catalogo anime e ottenere statistiche aggregate sui dati importati.

### Obiettivo

L'obiettivo dell'issue è esporre tramite endpoint HTTP alcune funzionalità del progetto:

- verifica dello stato del database;
- recupero di un anime tramite ID;
- statistiche aggregate su generi, studi di produzione e utenti.

### Tecnologie utilizzate

- **FastAPI** per la definizione degli endpoint REST;
- **Uvicorn** come server ASGI;
- **PyMongo** per la connessione a MongoDB;
- **bson.json_util** per la conversione dei documenti MongoDB in JSON.

### Avvio del server

Prima di avviare il backend, assicurarsi che MongoDB sia in esecuzione su:

```text
localhost:27017
```

Il database deve essere già stato popolato con:

```bash
python import_to_mongo.py
```

Avvio del server:

```bash
uvicorn api.main:app --reload
```

Il backend sarà disponibile su:

```text
http://127.0.0.1:8000
```

La documentazione interattiva FastAPI è disponibile su:

```text
http://127.0.0.1:8000/docs
```

### Endpoint disponibili

| Metodo | Endpoint | Descrizione |
| :--- | :--- | :--- |
| GET | `/` | Messaggio di benvenuto |
| GET | `/api/health` | Verifica connessione al database e collection disponibili |
| GET | `/api/animes/{anime_id}` | Recupera un anime tramite ID |
| GET | `/api/stats/genres` | Top 10 dei generi per voto medio |
| GET | `/api/stats/studios` | Top 5 degli studi per episodi prodotti |
| GET | `/api/users/locations` | Principali località degli utenti |

### Test degli endpoint

Gli endpoint sono stati testati localmente tramite `curl`:

```bash
curl http://127.0.0.1:8000/api/health
curl http://127.0.0.1:8000/api/stats/genres
curl http://127.0.0.1:8000/api/stats/studios
curl http://127.0.0.1:8000/api/users/locations
curl http://127.0.0.1:8000/api/animes/11013
```

Esempio di risposta dell'endpoint `/api/health`:

```json
{
  "status": "ok",
  "database": "nosql_anime_analytics",
  "collections": ["studios", "users", "reviews", "animes", "watchlists"]
}
```

Esempio di risposta dell'endpoint `/api/animes/11013`:

```json
{
  "_id": 11013,
  "title": "Inu x Boku SS",
  "type": "TV",
  "studio": "David Production",
  "episodes": 12,
  "score": 7.63,
  "genres": ["Comedy", "Supernatural", "Romance", "Shounen"],
  "status": "Finished Airing"
}
```

### Risultato

L'issue risulta completata perché il backend:

- si collega correttamente a MongoDB;
- espone più di tre endpoint REST;
- restituisce dati in formato JSON;
- permette di interrogare sia singoli documenti sia statistiche aggregate;
- è stato testato localmente tramite `curl`.

---

## Issue #8: Test automatizzati API REST

Sono stati aggiunti test automatizzati per verificare il corretto funzionamento degli endpoint REST implementati con FastAPI.

### Obiettivo

L'obiettivo dell'issue è validare gli endpoint principali del backend, controllando:

- codice HTTP restituito;
- struttura JSON della risposta;
- presenza dei campi attesi;
- gestione dell'errore per un anime inesistente.

### Tecnologie utilizzate

- **pytest** per l'esecuzione della suite di test;
- **requests** per effettuare chiamate HTTP agli endpoint REST.

### Avvio dei test

Prima di eseguire i test è necessario avere MongoDB attivo e il server API in esecuzione.

Avviare il backend:

```bash
uvicorn api.main:app --reload
```

In un secondo terminale eseguire:

```bash
pytest tests/test_api.py -v
```

### Endpoint testati

| Endpoint | Verifica |
|---|---|
| `/api/health` | Controllo stato database e collection disponibili |
| `/api/animes/11013` | Recupero corretto di un anime esistente |
| `/api/animes/999999999` | Gestione errore `404 Not Found` per anime inesistente |
| `/api/stats/genres` | Verifica risposta JSON delle statistiche sui generi |
| `/api/stats/studios` | Verifica risposta JSON delle statistiche sugli studi |
| `/api/users/locations` | Verifica risposta JSON delle statistiche sugli utenti |

### Output dei test

L'output dell'esecuzione dei test è stato salvato in:

```text
test_outputs/api_tests_output.txt
```

Risultato verificato:

```text
6 passed
```

### Risultato

La suite di test verifica più di tre endpoint REST e controlla sia risposte corrette sia gestione degli errori.
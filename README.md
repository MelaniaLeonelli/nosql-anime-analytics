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

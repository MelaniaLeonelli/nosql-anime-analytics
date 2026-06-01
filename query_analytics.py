import os
from pymongo import MongoClient
from pprint import pprint

def get_db_connection():
    client = MongoClient("mongodb://localhost:27017/")
    return client["nosql_anime_analytics"]

def query_1_generi_popolari(db):
    print("\n" + "="*60)
    print("QUERY 1: Analisi dei Generi più Apprezzati (Top 10)")
    print("="*60)
    
    pipeline = [
        {"$unwind": "$genres"},
        {
            "$group": {
                "_id": "$genres",
                "total_anime": {"$sum": 1},
                "voto_medio": {"$avg": "$score"}
            }
        },
        {"$match": {"total_anime": {"$gte": 5}}},
        {"$sort": {"voto_medio": -1}},
        {
            "$project": {
                "genere": "$_id",
                "_id": 0,
                "total_anime": 1,
                "voto_medio": {"$round": ["$voto_medio", 2]}
            }
        }
    ]
    
    results = db["animes"].aggregate(pipeline)
    for res in list(results)[:10]:
        print(f"Genere: {res['genere']:<15} | Totale Anime: {res['total_anime']:<5} | Voto Medio: {res['voto_medio']}")

def query_2_performance_studi(db):
    print("\n" + "="*60)
    print("QUERY 2: Top 5 Studi per Volume di Episodi Prodotti")
    print("="*60)
    
    pipeline = [
        {
            "$group": {
                "_id": "$studio",
                "totale_episodi": {"$sum": "$episodes"},
                "voto_medio_studio": {"$avg": "$score"},
                "anime_prodotti": {"$sum": 1}
            }
        },
        {"$match": {"_id": {"$ne": "Unknown"}}},
        {"$sort": {"totale_episodi": -1}},
        {"$limit": 5},
        {
            "$project": {
                "studio": "$_id",
                "_id": 0,
                "totale_episodi": 1,
                "anime_prodotti": 1,
                "voto_medio_studio": {"$round": ["$voto_medio_studio", 2]}
            }
        }
    ]
    
    results = db["animes"].aggregate(pipeline)
    for res in results:
        print(f"Studio: {res['studio']:<20} | Anime: {res['anime_prodotti']:<4} | Totale Episodi: {res['totale_episodi']:<5} | Score Medio: {res['voto_medio_studio']}")

def query_3_cross_analytics_lookup(db):
    print("\n" + "="*60)
    print("QUERY 3: Cross-Analytics (User Locations & Top Rated Studios)")
    print("="*60)
    
    pipeline = [
        {"$match": {"location": {"$ne": "Unknown"}}},
        {
            "$group": {
                "_id": "$location",
                "utenti_in_location": {"$sum": 1},
                "score_medio_location": {"$avg": "$stats_mean_score"}
            }
        },
        {"$sort": {"utenti_in_location": -1}},
        {"$limit": 5},
        {
            "$project": {
                "localita": "$_id",
                "_id": 0,
                "utenti_in_location": 1,
                "score_medio_location": {"$round": ["$score_medio_location", 2]}
            }
        }
    ]
    
    results = db["users"].aggregate(pipeline)
    for res in results:
        print(f"Località: {res['localita']:<25} | Utenti: {res['utenti_in_location']:<5} | Voto Medio Profilo: {res['score_medio_location']}")

if __name__ == "__main__":
    try:
        db = get_db_connection()
        print("Connessione a MongoDB riuscita!")
        
        # Ispezione rapida di un anime per essere sicuri dei campi
        print("\nEsempio di documento nella collezione 'animes':")
        pprint(db["animes"].find_one())
        
        print("\nEsecuzione delle pipeline analitiche...")
        query_1_generi_popolari(db)
        query_2_performance_studi(db)
        query_3_cross_analytics_lookup(db)
        
        print("\n" + "="*60)
        print("ANALISI AGGREGATION PIPELINE COMPLETATA CON SUCCESSO!")
        print("="*60)
    except Exception as e:
        print(f"Errore durante l'esecuzione delle query: {e}")
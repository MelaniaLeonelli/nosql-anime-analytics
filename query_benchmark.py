import time
from pymongo import MongoClient, ASCENDING, DESCENDING

def get_db_connection():
    client = MongoClient("mongodb://localhost:27017/")
    return client["nosql_anime_analytics"]

# --- FUNZIONI DI BENCHMARK CON ITERAZIONI (MEDIA SU 10 LANCI) ---

def benchmark_query_1_generi(db):
    pipeline = [
        {"$unwind": "$genres"},
        {"$group": {"_id": "$genres", "total_anime": {"$sum": 1}, "voto_medio": {"$avg": "$score"}}},
        {"$match": {"total_anime": {"$gte": 5}}},
        {"$sort": {"voto_medio": -1}},
        {"$limit": 10}
    ]
    # Scaldiamo la cache con un lancio a vuoto
    list(db["animes"].aggregate(pipeline))
    
    # Calcoliamo la media su 10 lanci
    tempi = []
    for _ in range(10):
        start_time = time.time()
        list(db["animes"].aggregate(pipeline))
        tempi.append((time.time() - start_time) * 1000)
    return sum(tempi) / len(tempi)

def benchmark_query_2_studi(db):
    pipeline = [
        {"$group": {"_id": "$studio", "totale_episodi": {"$sum": "$episodes"}, "voto_medio_studio": {"$avg": "$score"}}},
        {"$match": {"_id": {"$ne": "Unknown"}}},
        {"$sort": {"totale_episodi": -1}},
        {"$limit": 5}
    ]
    list(db["animes"].aggregate(pipeline))
    
    tempi = []
    for _ in range(10):
        start_time = time.time()
        list(db["animes"].aggregate(pipeline))
        tempi.append((time.time() - start_time) * 1000)
    return sum(tempi) / len(tempi)

def benchmark_query_3_utenti(db):
    pipeline = [
        {"$match": {"location": {"$ne": "Unknown"}}},
        {"$group": {"_id": "$location", "utenti_in_location": {"$sum": 1}, "score_medio_location": {"$avg": "$stats_mean_score"}}},
        {"$sort": {"utenti_in_location": -1}},
        {"$limit": 5}
    ]
    list(db["users"].aggregate(pipeline))
    
    tempi = []
    for _ in range(10):
        start_time = time.time()
        list(db["users"].aggregate(pipeline))
        tempi.append((time.time() - start_time) * 1000)
    return sum(tempi) / len(tempi)


if __name__ == "__main__":
    db = get_db_connection()
    print("Connessione riuscita. Pulizia indici precedenti e avvio Benchmark stabili...\n")
    
    # Rimuoviamo gli indici vecchi per fare un test pulito da zero
    try:
        db["animes"].drop_indexes()
        db["users"].drop_indexes()
    except:
        pass

    # ----------------------------------------------------
    # RUN 1: PRE-OTTIMIZZAZIONE
    # ----------------------------------------------------
    print("====================================================")
    print("RUN 1: MEDIE PRE-OTTIMIZZAZIONE (SENZA INDICI)")
    print("====================================================")
    
    t1_pre = benchmark_query_1_generi(db)
    print(f"Query 1 (Generi) media: {t1_pre:.2f} ms")
    
    t2_pre = benchmark_query_2_studi(db)
    print(f"Query 2 (Studi)  media: {t2_pre:.2f} ms")
    
    t3_pre = benchmark_query_3_utenti(db)
    print(f"Query 3 (Utenti) media: {t3_pre:.2f} ms")
    
    # ----------------------------------------------------
    # FASE 2: CREAZIONE DEGLI INDICI MIRATI
    # ----------------------------------------------------
    print("\n====================================================")
    print("FASE 2: CREAZIONE INDICI DI OTTIMIZZAZIONE...")
    print("====================================================")
    
    db["animes"].create_index([("genres", ASCENDING)])
    db["animes"].create_index([("studio", ASCENDING), ("score", DESCENDING)])
    db["users"].create_index([("location", ASCENDING)])
    print("[OK] Indici rigenerati correttamente.")
    
    time.sleep(2) # Diamo tempo a Mongo di stabilizzarsi
    
    # ----------------------------------------------------
    # RUN 2: POST-OTTIMIZZAZIONE
    # ----------------------------------------------------
    print("\n====================================================")
    print("RUN 2: MEDIE POST-OTTIMIZZAZIONE (CON INDICI)")
    print("====================================================")
    
    t1_post = benchmark_query_1_generi(db)
    print(f"Query 1 (Generi) media: {t1_post:.2f} ms")
    
    t2_post = benchmark_query_2_studi(db)
    print(f"Query 2 (Studi)  media: {t2_post:.2f} ms")
    
    t3_post = benchmark_query_3_utenti(db)
    print(f"Query 3 (Utenti) media: {t3_post:.2f} ms")
    
    print("\n====================================================")
    print("RIASSUNTO FINALE PRESTAZIONI BILANCIATE")
    print("====================================================")
    print(f"Query 1 -> Pre: {t1_pre:.2f} ms | Post: {t1_post:.2f} ms | Delta: {(((t1_pre-t1_post)/t1_pre)*100):.1f}%")
    print(f"Query 2 -> Pre: {t2_pre:.2f} ms | Post: {t2_post:.2f} ms | Delta: {(((t2_pre-t2_post)/t2_pre)*100):.1f}%")
    print(f"Query 3 -> Pre: {t3_pre:.2f} ms | Post: {t3_post:.2f} ms | Delta: {(((t3_pre-t3_post)/t3_pre)*100):.1f}%")
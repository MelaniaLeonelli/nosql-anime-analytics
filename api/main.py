import json
import os
from bson import json_util
from fastapi import FastAPI, HTTPException, Query
from pymongo import MongoClient

app = FastAPI(title="NoSQL Anime Analytics API")


def get_db():
    mongo_uri = os.environ.get("MONGO_URI", "mongodb://localhost:27017/")
    client = MongoClient(mongo_uri)
    return client["nosql_anime_analytics"]


def mongo_to_json(data):
    return json.loads(json_util.dumps(data))


@app.on_event("startup")
def startup_event():
    # Avvio del backend ed esecuzione di eventuali controlli iniziali
    print("Backend API avviato con successo")


@app.get("/")
def root():
    return {"message": "NoSQL Anime Analytics API", "docs": "/docs"}


@app.get("/api/health")
def health_check():
    db = get_db()
    collections = db.list_collection_names()
    return {
        "status": "ok",
        "database": "nosql_anime_analytics",
        "collections": collections,
    }


@app.get("/api/anime/catalog")
def get_anime_catalog(
    q: str = Query(None, description="Parola chiave per la ricerca parziale nel titolo"),
    page: int = Query(1, ge=1, description="Numero della pagina"),
    limit: int = Query(20, ge=1, le=100, description="Anime per pagina"),
    sort_by: str = Query("score", description="Campo su cui ordinare"),
):
    db = get_db()
    skip_value = (page - 1) * limit

    # Costruzione della query con Regex per una ricerca parziale e flessibile
    query = {}
    if q:
        # "$options": "i" permette di ignorare la differenza tra maiuscole e minuscole
        query["title"] = {"$regex": q, "$options": "i"}

    cursor = db["animes"].find(query)

    # Gestione dell'ordinamento: 1 per ordine alfabetico (A-Z), -1 per il voto decrescente
    if sort_by == "title":
        cursor = cursor.sort("title", 1)
    else:
        cursor = cursor.sort(sort_by, -1)

    anime_list = list(cursor.skip(skip_value).limit(limit))
    total_documents = db["animes"].count_documents(query)

    return {
        "total": total_documents,
        "page": page,
        "limit": limit,
        "results": mongo_to_json(anime_list),
    }


@app.get("/api/animes/{anime_id}")
def get_anime_by_id(anime_id: int):
    db = get_db()
    anime = db["animes"].find_one({"_id": anime_id})
    if anime is None:
        raise HTTPException(status_code=404, detail="Anime non trovato")
    return mongo_to_json(anime)


@app.get("/api/stats/genres")
def get_genre_stats():
    db = get_db()
    pipeline = [
        {"$unwind": "$genres"},
        {
            "$group": {
                "_id": "$genres",
                "total_anime": {"$sum": 1},
                "voto_medio": {"$avg": "$score"},
            }
        },
        {"$match": {"total_anime": {"$gte": 5}}},
        {"$sort": {"voto_medio": -1}},
        {"$limit": 10},
        {
            "$project": {
                "_id": 0,
                "genere": "$_id",
                "total_anime": 1,
                "voto_medio": {"$round": ["$voto_medio", 2]},
            }
        },
    ]
    results = list(db["animes"].aggregate(pipeline))
    return mongo_to_json(results)


@app.get("/api/stats/studios")
def get_studio_stats():
    db = get_db()
    pipeline = [
        {
            "$group": {
                "_id": "$studio",
                "totale_episodi": {"$sum": "$episodes"},
                "voto_medio_studio": {"$avg": "$score"},
                "anime_prodotti": {"$sum": 1},
            }
        },
        {"$match": {"_id": {"$ne": "Unknown"}}},
        {"$sort": {"totale_episodi": -1}},
        {"$limit": 5},
        {
            "$project": {
                "_id": 0,
                "studio": "$_id",
                "totale_episodi": 1,
                "anime_prodotti": 1,
                "voto_medio_studio": {"$round": ["$voto_medio_studio", 2]},
            }
        },
    ]
    results = list(db["animes"].aggregate(pipeline))
    return mongo_to_json(results)


@app.get("/api/users/locations")
def get_user_locations_stats():
    db = get_db()
    pipeline = [
        {"$match": {"location": {"$ne": "Unknown"}}},
        {
            "$group": {
                "_id": "$location",
                "utenti_in_location": {"$sum": 1},
                "score_medio_location": {"$avg": "$stats_mean_score"},
            }
        },
        {"$sort": {"utenti_in_location": -1}},
        {"$limit": 5},
        {
            "$project": {
                "_id": 0,
                "localita": "$_id",
                "utenti_in_location": 1,
                "score_medio_location": {
                    "$round": ["$score_medio_location", 2]
                },
            }
        },
    ]
    results = list(db["users"].aggregate(pipeline))
    return mongo_to_json(results)
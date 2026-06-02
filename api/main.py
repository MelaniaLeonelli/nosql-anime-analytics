from fastapi import FastAPI, HTTPException
from pymongo import MongoClient
from bson import json_util
import json

app = FastAPI(title="NoSQL Anime Analytics API")


def get_db():
    client = MongoClient("mongodb://localhost:27017/")
    return client["nosql_anime_analytics"]


def mongo_to_json(data):
    return json.loads(json_util.dumps(data))


@app.get("/")
def root():
    return {
        "message": "NoSQL Anime Analytics API",
        "docs": "/docs"
    }


@app.get("/api/health")
def health_check():
    db = get_db()
    collections = db.list_collection_names()

    return {
        "status": "ok",
        "database": "nosql_anime_analytics",
        "collections": collections
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
                "voto_medio": {"$avg": "$score"}
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
                "voto_medio": {"$round": ["$voto_medio", 2]}
            }
        }
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
                "anime_prodotti": {"$sum": 1}
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
                "voto_medio_studio": {"$round": ["$voto_medio_studio", 2]}
            }
        }
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
                "score_medio_location": {"$avg": "$stats_mean_score"}
            }
        },
        {"$sort": {"utenti_in_location": -1}},
        {"$limit": 5},
        {
            "$project": {
                "_id": 0,
                "localita": "$_id",
                "utenti_in_location": 1,
                "score_medio_location": {"$round": ["$score_medio_location", 2]}
            }
        }
    ]

    results = list(db["users"].aggregate(pipeline))
    return mongo_to_json(results)
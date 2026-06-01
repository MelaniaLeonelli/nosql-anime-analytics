import pandas as pd
from pymongo import MongoClient

def import_data():
    # 1. Connessione a MongoDB locale (porta standard)
    print("Connessione a MongoDB...")
    client = MongoClient("mongodb://localhost:27017/")
    
    # Creiamo o selezioniamo il database del progetto
    db = client["nosql_anime_analytics"]
    
    # 2. Pulizia collezioni esistenti per evitare duplicati nei test
    db["animes"].drop()
    db["users"].drop()
    db["watchlists"].drop()
    db["studios"].drop()
    db["reviews"].drop()

    # 3. Importazione ANIME
    print("Importazione anime_sample.csv...")
    df_anime = pd.read_csv('anime_sample.csv')
    # Convertiamo i generi da stringa singola "Action, Comedy" a un vero Array JSON ["Action", "Comedy"]
    df_anime['genre'] = df_anime['genre'].fillna('').apply(lambda x: [g.strip() for g in x.split(',') if g.strip()])
    
    anime_docs = []
    for _, row in df_anime.iterrows():
        anime_docs.append({
            "_id": int(row['anime_id']), # Usiamo l'ID originale come Chiave Primaria NoSQL
            "title": row['title'],
            "type": row['type'],
            "studio": row['studio'],
            "episodes": int(row['episodes']) if pd.notna(row['episodes']) else 0,
            "score": float(row['score']) if pd.notna(row['score']) else 0.0,
            "genres": row['genre'],
            "status": row['status']
        })
    db["animes"].insert_many(anime_docs)

    # 4. Importazione UTENTI
    print("Importazione users_sample.csv...")
    df_users = pd.read_csv('users_sample.csv').dropna(subset=['username'])
    # Eliminiamo eventuali duplicati di username per usarlo come _id logico
    df_users = df_users.drop_duplicates(subset=['username'])
    
    user_docs = []
    for _, row in df_users.iterrows():
        user_docs.append({
            "_id": row['username'], # Usiamo l'username come chiave univoca del documento
            "user_id": int(row['user_id']),
            "gender": row['gender'],
            "location": row['location'],
            "user_completed": int(row['user_completed']),
            "stats_mean_score": float(row['stats_mean_score']) if pd.notna(row['stats_mean_score']) else 0.0
        })
    db["users"].insert_many(user_docs)

    # 5. Importazione delle altre collezioni di supporto (Watchlist, Studios, Reviews)
    print("Importazione delle collezioni di supporto...")
    
    df_lists = pd.read_csv('animelists_sample.csv')
    db["watchlists"].insert_many(df_lists.to_dict(orient='records'))
    
    df_studios = pd.read_csv('studios_sample.csv')
    db["studios"].insert_many(df_studios.to_dict(orient='records'))
    
    df_reviews = pd.read_csv('reviews_sample.csv')
    db["reviews"].insert_many(df_reviews.to_dict(orient='records'))

    print("\nETL COMPLETATO CON SUCCESSO!")
    print(f"Documenti caricati:\n- Anime: {db['animes'].count_documents({})}\n- Utenti: {db['users'].count_documents({})}")

if __name__ == "__main__":
    import_data()
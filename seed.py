import pandas as pd
from pymongo import MongoClient
import os

print("Avvio dello script di seeding per il Backend (Versione Aggiornata)...")

try:
    client = MongoClient("mongodb://localhost:27017/", serverSelectionTimeoutMS=5000)
    db = client["nosql_anime_analytics"]  # Allineato al db name usato nel backend
    client.server_info()
    print(" Connessione a MongoDB riuscita!")
except Exception as e:
    print(f" Errore di connessione a MongoDB: {e}")
    exit(1)

# Mappatura corretta per il backend
csv_mapping = {
    "anime_sample.csv": "animes",  # <-- Plurale, come si aspetta il backend
    "users_sample.csv": "users",
    "studios_sample.csv": "studios",
    "reviews_sample.csv": "reviews",
    "animelists_sample.csv": "animelists"
}

def seed_collection(filename, collection_name):
    possible_paths = [filename, f"data/{filename}", f"api/data/{filename}"]
    csv_path = next((p for p in possible_paths if os.path.exists(p)), None)

    if not csv_path:
        clean_name = filename.replace("_sample", "")
        possible_paths_clean = [clean_name, f"data/{clean_name}", f"api/data/{clean_name}"]
        csv_path = next((p for p in possible_paths_clean if os.path.exists(p)), None)

    if not csv_path:
        print(f" Impossibile trovare {filename}. Salto '{collection_name}'.")
        return

    print(f" Lettura di {csv_path} in corso...")
    df = pd.read_csv(csv_path)

    # --- INIZIO TRASFORMAZIONI SPECIFICHE PER IL BACKEND ---
    if collection_name == "animes":
        # Trasformiamo la colonna 'genre' (stringa) in 'genres' (array)
        if 'genre' in df.columns:
            df['genres'] = df['genre'].apply(
                lambda x: [g.strip() for g in x.split(',')] if pd.notnull(x) else []
            )
            df = df.drop(columns=['genre'])
            print("   ↳  Trasformato campo 'genre' in array 'genres'")
            
    # --- FINE TRASFORMAZIONI ---

    df = df.where(pd.notnull(df), None)
    records = df.to_dict(orient="records")

    print(f" Svuoto '{collection_name}' e importo...")
    db[collection_name].drop()

    if records:
        chunk_size = 10000
        for i in range(0, len(records), chunk_size):
            db[collection_name].insert_many(records[i:i + chunk_size])
        print(f" Inseriti {len(records)} documenti in '{collection_name}'!")

for csv_file, collection in csv_mapping.items():
    seed_collection(csv_file, collection)

print("\n🏁 DATABASE POPOLATO CON SUCCESSO! I dati sono pronti per il backend.")
from pathlib import Path
import math
import sqlite3

from pymongo import MongoClient


BASE_DIR = Path(__file__).resolve().parent
SQLITE_DB_PATH = BASE_DIR / "anime_dw.sqlite"
SCHEMA_PATH = BASE_DIR / "dw_schema.sql"

MONGO_URI = "mongodb://localhost:27017/"
MONGO_DB_NAME = "nosql_anime_analytics"


def clean_value(value):
    if value is None:
        return None

    if isinstance(value, float) and math.isnan(value):
        return None

    return value


def to_int(value):
    value = clean_value(value)

    if value is None or value == "":
        return None

    try:
        return int(float(value))
    except (TypeError, ValueError):
        return None


def to_float(value):
    value = clean_value(value)

    if value is None or value == "":
        return None

    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def get_mongo_db():
    client = MongoClient(MONGO_URI)
    return client[MONGO_DB_NAME]


def get_sqlite_connection():
    conn = sqlite3.connect(SQLITE_DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def initialize_warehouse(conn):
    schema_sql = SCHEMA_PATH.read_text(encoding="utf-8")
    conn.executescript(schema_sql)
    conn.commit()


def load_dim_studio(conn, mongo_db):
    cursor = conn.cursor()

    studios_from_collection = list(mongo_db["studios"].find({}))
    studio_names_from_anime = set()

    for anime in mongo_db["animes"].find({}, {"studio": 1}):
        studio_name = clean_value(anime.get("studio"))
        if studio_name and studio_name != "Unknown":
            studio_names_from_anime.add(studio_name)

    inserted_names = set()

    for studio in studios_from_collection:
        studio_name = clean_value(
            studio.get("studio_name")
            or studio.get("name")
            or studio.get("_id")
        )

        if not studio_name or studio_name == "Unknown":
            continue

        country = clean_value(studio.get("country"))
        established_year = to_int(studio.get("established_year"))

        cursor.execute(
            """
            INSERT OR IGNORE INTO dim_studio (
                studio_name,
                country,
                established_year
            )
            VALUES (?, ?, ?)
            """,
            (str(studio_name), country, established_year)
        )

        inserted_names.add(str(studio_name))

    for studio_name in sorted(studio_names_from_anime - inserted_names):
        cursor.execute(
            """
            INSERT OR IGNORE INTO dim_studio (
                studio_name,
                country,
                established_year
            )
            VALUES (?, ?, ?)
            """,
            (studio_name, None, None)
        )

    conn.commit()


def load_dim_anime(conn, mongo_db):
    cursor = conn.cursor()

    for anime in mongo_db["animes"].find({}):
        anime_id = to_int(anime.get("anime_id"))

        if anime_id is None:
            anime_id = to_int(anime.get("_id"))

        title = clean_value(
            anime.get("title")
            or anime.get("name")
            or anime.get("anime_title")
        )

        if anime_id is None or not title:
            continue

        genres = anime.get("genres", [])

        if not genres and anime.get("genre"):
            genres = anime.get("genre")

        if isinstance(genres, list):
            genres_text = ", ".join(str(genre) for genre in genres)
        else:
            genres_text = str(genres)

        cursor.execute(
            """
            INSERT OR IGNORE INTO dim_anime (
                anime_id,
                title,
                type,
                studio_name,
                episodes,
                score,
                genres,
                status
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                anime_id,
                str(title),
                clean_value(anime.get("type")),
                clean_value(anime.get("studio") or anime.get("studio_name")),
                to_int(anime.get("episodes")),
                to_float(anime.get("score")),
                genres_text,
                clean_value(anime.get("status"))
            )
        )

    conn.commit()


def load_dim_user(conn, mongo_db):
    cursor = conn.cursor()

    for user in mongo_db["users"].find({}):
        username = clean_value(
            user.get("username")
            or user.get("user_name")
            or user.get("profile")
        )

        if not username:
            continue

        cursor.execute(
            """
            INSERT OR IGNORE INTO dim_user (
                username,
                user_id,
                gender,
                location,
                user_completed,
                stats_mean_score
            )
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                str(username),
                to_int(user.get("user_id")),
                clean_value(user.get("gender")),
                clean_value(user.get("location")),
                to_int(user.get("user_completed")),
                to_float(user.get("stats_mean_score"))
            )
        )

    conn.commit()


def build_lookup_maps(conn):
    anime_map = {
        row[0]: row[1]
        for row in conn.execute("SELECT anime_id, anime_key FROM dim_anime")
    }

    user_map = {
        row[0]: row[1]
        for row in conn.execute("SELECT username, user_key FROM dim_user")
    }

    studio_map = {
        row[0]: row[1]
        for row in conn.execute("SELECT studio_name, studio_key FROM dim_studio")
    }

    anime_studio_map = {
        row[0]: row[1]
        for row in conn.execute("SELECT anime_id, studio_name FROM dim_anime")
    }

    return anime_map, user_map, studio_map, anime_studio_map


def load_fact_reviews(conn, mongo_db):
    cursor = conn.cursor()
    anime_map, user_map, studio_map, anime_studio_map = build_lookup_maps(conn)

    inserted = 0
    skipped_missing_anime = 0
    skipped_missing_user = 0

    for review in mongo_db["reviews"].find({}):
        anime_id = to_int(review.get("anime_id"))
        username = clean_value(review.get("username"))

        if anime_id not in anime_map:
            skipped_missing_anime += 1
            continue

        if username is None or str(username) not in user_map:
            skipped_missing_user += 1
            continue

        anime_key = anime_map[anime_id]
        user_key = user_map[str(username)]

        studio_name = anime_studio_map.get(anime_id)
        studio_key = studio_map.get(studio_name)

        cursor.execute(
            """
            INSERT OR IGNORE INTO fact_reviews (
                review_id,
                anime_key,
                user_key,
                studio_key,
                source_anime_id,
                source_username,
                score,
                review_text
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                to_int(review.get("review_id")),
                anime_key,
                user_key,
                studio_key,
                anime_id,
                str(username),
                to_int(review.get("score") or review.get("my_score")),
                clean_value(review.get("review_text"))
            )
        )

        inserted += cursor.rowcount

    conn.commit()

    return {
        "inserted": inserted,
        "skipped_missing_anime": skipped_missing_anime,
        "skipped_missing_user": skipped_missing_user
    }


def count_sqlite_rows(conn, table_name):
    cursor = conn.execute(f"SELECT COUNT(*) FROM {table_name}")
    return cursor.fetchone()[0]


def print_validation_report(conn, mongo_db, fact_result):
    mongo_counts = {
        "animes": mongo_db["animes"].count_documents({}),
        "users": mongo_db["users"].count_documents({}),
        "studios": mongo_db["studios"].count_documents({}),
        "reviews": mongo_db["reviews"].count_documents({})
    }

    warehouse_counts = {
        "dim_anime": count_sqlite_rows(conn, "dim_anime"),
        "dim_user": count_sqlite_rows(conn, "dim_user"),
        "dim_studio": count_sqlite_rows(conn, "dim_studio"),
        "fact_reviews": count_sqlite_rows(conn, "fact_reviews")
    }

    print("=" * 70)
    print("ETL DATA WAREHOUSE COMPLETATA")
    print("=" * 70)
    print(f"Database SQLite creato: {SQLITE_DB_PATH}")
    print()

    print("Conteggi sorgente MongoDB:")
    for collection_name, count in mongo_counts.items():
        print(f"- {collection_name}: {count}")

    print()

    print("Conteggi Data Warehouse SQLite:")
    for table_name, count in warehouse_counts.items():
        print(f"- {table_name}: {count}")

    print()

    print("Validazioni:")
    print(
        f"- Anime caricati: {warehouse_counts['dim_anime']} / "
        f"{mongo_counts['animes']}"
    )
    print(
        f"- Utenti caricati: {warehouse_counts['dim_user']} / "
        f"{mongo_counts['users']}"
    )
    print(
        f"- Review caricate nella fact table: "
        f"{warehouse_counts['fact_reviews']} / {mongo_counts['reviews']}"
    )
    print(f"- Review saltate per anime mancante: {fact_result['skipped_missing_anime']}")
    print(f"- Review saltate per utente mancante: {fact_result['skipped_missing_user']}")

    print()

    if warehouse_counts["dim_anime"] > 0 and warehouse_counts["dim_user"] > 0:
        print("ESITO VALIDAZIONE: OK")
    else:
        print("ESITO VALIDAZIONE: ATTENZIONE - dimensioni vuote")


def main():
    mongo_db = get_mongo_db()

    with get_sqlite_connection() as conn:
        initialize_warehouse(conn)

        print("Caricamento dimensione studi...")
        load_dim_studio(conn, mongo_db)

        print("Caricamento dimensione anime...")
        load_dim_anime(conn, mongo_db)

        print("Caricamento dimensione utenti...")
        load_dim_user(conn, mongo_db)

        print("Caricamento tabella dei fatti reviews...")
        fact_result = load_fact_reviews(conn, mongo_db)

        print_validation_report(conn, mongo_db, fact_result)


if __name__ == "__main__":
    main()
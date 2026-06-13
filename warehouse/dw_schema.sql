DROP TABLE IF EXISTS fact_reviews;
DROP TABLE IF EXISTS dim_anime;
DROP TABLE IF EXISTS dim_user;
DROP TABLE IF EXISTS dim_studio;

CREATE TABLE dim_studio (
    studio_key INTEGER PRIMARY KEY AUTOINCREMENT,
    studio_name TEXT NOT NULL UNIQUE,
    country TEXT,
    established_year INTEGER
);

CREATE TABLE dim_anime (
    anime_key INTEGER PRIMARY KEY AUTOINCREMENT,
    anime_id INTEGER NOT NULL UNIQUE,
    title TEXT NOT NULL,
    type TEXT,
    studio_name TEXT,
    episodes INTEGER,
    score REAL,
    genres TEXT,
    status TEXT
);

CREATE TABLE dim_user (
    user_key INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    user_id INTEGER,
    gender TEXT,
    location TEXT,
    user_completed INTEGER,
    stats_mean_score REAL
);

CREATE TABLE fact_reviews (
    review_key INTEGER PRIMARY KEY AUTOINCREMENT,
    review_id INTEGER UNIQUE,
    anime_key INTEGER NOT NULL,
    user_key INTEGER NOT NULL,
    studio_key INTEGER,
    source_anime_id INTEGER,
    source_username TEXT,
    score INTEGER,
    review_text TEXT,

    FOREIGN KEY (anime_key) REFERENCES dim_anime(anime_key),
    FOREIGN KEY (user_key) REFERENCES dim_user(user_key),
    FOREIGN KEY (studio_key) REFERENCES dim_studio(studio_key)
);

CREATE INDEX idx_fact_reviews_anime ON fact_reviews(anime_key);
CREATE INDEX idx_fact_reviews_user ON fact_reviews(user_key);
CREATE INDEX idx_fact_reviews_studio ON fact_reviews(studio_key);
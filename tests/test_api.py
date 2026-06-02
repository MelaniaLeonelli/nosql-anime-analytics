import os

import pytest
import requests


BASE_URL = os.getenv("API_BASE_URL", "http://127.0.0.1:8000")
TIMEOUT = 5


def test_health_check():
    response = requests.get(f"{BASE_URL}/api/health", timeout=TIMEOUT)

    assert response.status_code == 200

    data = response.json()
    assert data["status"] == "ok"
    assert data["database"] == "nosql_anime_analytics"
    assert "animes" in data["collections"]
    assert "users" in data["collections"]
    assert "watchlists" in data["collections"]
    assert "studios" in data["collections"]
    assert "reviews" in data["collections"]


def test_get_existing_anime_by_id():
    response = requests.get(f"{BASE_URL}/api/animes/11013", timeout=TIMEOUT)

    assert response.status_code == 200

    data = response.json()
    assert data["_id"] == 11013
    assert data["title"] == "Inu x Boku SS"
    assert "genres" in data
    assert isinstance(data["genres"], list)


def test_get_non_existing_anime_returns_404():
    response = requests.get(f"{BASE_URL}/api/animes/999999999", timeout=TIMEOUT)

    assert response.status_code == 404

    data = response.json()
    assert data["detail"] == "Anime non trovato"


def test_genre_stats_endpoint():
    response = requests.get(f"{BASE_URL}/api/stats/genres", timeout=TIMEOUT)

    assert response.status_code == 200

    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0

    first_result = data[0]
    assert "genere" in first_result
    assert "total_anime" in first_result
    assert "voto_medio" in first_result


def test_studio_stats_endpoint():
    response = requests.get(f"{BASE_URL}/api/stats/studios", timeout=TIMEOUT)

    assert response.status_code == 200

    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0

    first_result = data[0]
    assert "studio" in first_result
    assert "totale_episodi" in first_result
    assert "anime_prodotti" in first_result
    assert "voto_medio_studio" in first_result


def test_user_locations_endpoint():
    response = requests.get(f"{BASE_URL}/api/users/locations", timeout=TIMEOUT)

    assert response.status_code == 200

    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0

    first_result = data[0]
    assert "localita" in first_result
    assert "utenti_in_location" in first_result
    assert "score_medio_location" in first_result
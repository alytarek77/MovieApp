import pytest
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from unittest.mock import patch, MagicMock
from app.app import app


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


# 1. Health check returns 200
def test_health_check(client):
    res = client.get("/health")
    assert res.status_code == 200


# 2. Health check returns JSON
def test_health_check_json(client):
    res = client.get("/health")
    data = res.get_json()
    assert "status" in data


# 3. Home page loads
def test_home_page(client):
    res = client.get("/")
    assert res.status_code == 200


# 4. Search with query calls TMDB
@patch("app.app.requests.get")
def test_search_returns_results(mock_get, client):
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = {"results": [{"id": 1, "title": "Inception", "poster_path": "/img.jpg", "vote_average": 8.8}]}
    res = client.get("/?q=inception")
    assert res.status_code == 200


# 5. Movie details valid ID
@patch("app.app.requests.get")
def test_movie_details(mock_get, client):
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = {
        "id": 27205, "title": "Inception", "overview": "A thief...",
        "poster_path": "/img.jpg", "backdrop_path": "/bg.jpg",
        "release_date": "2010-07-16", "runtime": 148,
        "vote_average": 8.8, "tagline": "Your mind is the scene"
    }
    res = client.get("/movie/27205")
    assert res.status_code == 200


# 6. Movie details invalid ID returns 404
@patch("app.app.requests.get")
def test_movie_details_not_found(mock_get, client):
    mock_get.return_value.status_code = 404
    res = client.get("/movie/99999999")
    assert res.status_code == 404


# 7. Get watchlist returns 200
@patch("app.app.watchlist_collection")
def test_get_watchlist(mock_col, client):
    mock_col.find.return_value = []
    res = client.get("/api/watchlist")
    assert res.status_code == 200


# 8. Add movie to watchlist
@patch("app.app.watchlist_collection")
def test_add_to_watchlist(mock_col, client):
    mock_col.find_one.return_value = None
    res = client.post("/api/watchlist", json={
        "tmdb_id": 27205,
        "title": "Inception",
        "poster_path": "/img.jpg"
    })
    assert res.status_code == 201


# 9. Add duplicate movie returns 409
@patch("app.app.watchlist_collection")
def test_add_duplicate_to_watchlist(mock_col, client):
    mock_col.find_one.return_value = {"tmdb_id": 27205}
    res = client.post("/api/watchlist", json={
        "tmdb_id": 27205,
        "title": "Inception",
        "poster_path": "/img.jpg"
    })
    assert res.status_code == 409


# 10. Add to watchlist missing fields returns 400
def test_add_to_watchlist_bad_request(client):
    res = client.post("/api/watchlist", json={})
    assert res.status_code == 400


# 11. Remove movie from watchlist
@patch("app.app.watchlist_collection")
def test_remove_from_watchlist(mock_col, client):
    mock_col.delete_one.return_value.deleted_count = 1
    res = client.delete("/api/watchlist/27205")
    assert res.status_code == 200
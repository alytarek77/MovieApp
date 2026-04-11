import pytest
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

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


# 2. Health check returns JSON with status
def test_health_check_json(client):
    res = client.get("/health")
    data = res.get_json()
    assert "status" in data


# 3. Health check db is connected
def test_health_check_db_connected(client):
    res = client.get("/health")
    data = res.get_json()
    assert data["db"] == "connected"


# 4. Home page loads
def test_home_page(client):
    res = client.get("/")
    assert res.status_code == 200


# 5. Search with query returns 200
def test_search_with_query(client):
    res = client.get("/?q=inception")
    assert res.status_code == 200


# 6. Search with empty query returns 200
def test_search_empty_query(client):
    res = client.get("/")
    assert res.status_code == 200


# 7. Movie details valid ID returns 200
def test_movie_details_valid(client):
    res = client.get("/movie/27205")
    assert res.status_code == 200


# 8. Movie details invalid ID returns 404
def test_movie_details_invalid(client):
    res = client.get("/movie/99999999999")
    assert res.status_code == 404


# 9. Get watchlist returns 200
def test_get_watchlist(client):
    res = client.get("/api/watchlist")
    assert res.status_code == 200


# 10. Get watchlist returns a list
def test_get_watchlist_returns_list(client):
    res = client.get("/api/watchlist")
    data = res.get_json()
    assert isinstance(data, list)


# 11. Add to watchlist missing fields returns 400
def test_add_to_watchlist_missing_fields(client):
    res = client.post("/api/watchlist", json={})
    assert res.status_code == 400


# 12. Recommend missing fields returns 400
def test_recommend_missing_fields(client):
    res = client.post("/recommend", json={})
    assert res.status_code == 400
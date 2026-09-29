from fastapi.testclient import TestClient

from api.main import create_app


class FakeCandidate:
    title = "Inception"
    score = 0.91
    content_score = 0.80
    semantic_score = 0.95
    popularity_score = 0.70
    overview = "A thief enters dreams."
    genres = "Science Fiction|Thriller"


class FakeResult:
    user_query = "dream thriller"
    response = "Inception matches the dream-based thriller request."
    candidates = [FakeCandidate()]


class FakeRAG:
    def recommend(self, query, top_k):
        assert query == "dream thriller"
        assert top_k == 1
        return FakeResult()


def test_health_endpoint():
    client = TestClient(create_app())

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_recommend_endpoint():
    client = TestClient(create_app(FakeRAG()))

    response = client.post(
        "/recommend",
        json={"query": "dream thriller", "top_k": 1},
    )

    assert response.status_code == 200

    payload = response.json()

    assert payload["query"] == "dream thriller"
    assert payload["recommendations"][0]["title"] == "Inception"
    assert "Inception" in payload["explanation"]


def test_recommend_endpoint_validates_top_k():
    client = TestClient(create_app(FakeRAG()))

    response = client.post(
        "/recommend",
        json={"query": "test", "top_k": 0},
    )

    assert response.status_code == 422


def test_real_service_is_lazy(monkeypatch):
    from api import main

    class FailingService:
        def recommend(self, query, top_k):
            raise ValueError("test failure")

    monkeypatch.setattr(main, "build_service", lambda: FailingService())
    client = TestClient(create_app())

    response = client.post(
        "/recommend",
        json={"query": "test", "top_k": 1},
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "test failure"


class FakeLiveTMDB:
    def genre_map(self):
        return {878: "Science Fiction", 53: "Thriller"}

    def trending_movies(self, window="week"):
        return [
            {
                "id": 42,
                "title": "Trending AI",
                "overview": "A futuristic thriller.",
                "genre_ids": [878, 53],
                "vote_average": 8.4,
                "vote_count": 5000,
                "popularity": 120.0,
                "release_date": "2026-01-01",
                "poster_path": "/poster.jpg",
            }
        ]

    def discover_movies(self, **kwargs):
        return self.trending_movies()

    def movie_recommendations(self, movie_id):
        return self.trending_movies()


def test_tmdb_browse_endpoint(monkeypatch):
    from api import main

    monkeypatch.setenv("TMDB_ENABLED", "true")
    monkeypatch.setenv("TMDB_API_KEY", "test-key")
    monkeypatch.setattr(main, "TMDBClient", lambda: FakeLiveTMDB())

    client = TestClient(create_app())
    response = client.get("/browse/trending")

    assert response.status_code == 200
    payload = response.json()
    assert payload["category"] == "trending"
    assert payload["items"][0]["title"] == "Trending AI"
    assert payload["items"][0]["tmdb_id"] == 42


def test_tmdb_similar_endpoint(monkeypatch):
    from api import main

    monkeypatch.setenv("TMDB_ENABLED", "true")
    monkeypatch.setenv("TMDB_API_KEY", "test-key")
    monkeypatch.setattr(main, "TMDBClient", lambda: FakeLiveTMDB())

    client = TestClient(create_app())
    response = client.get("/movie/42/similar")

    assert response.status_code == 200
    assert response.json()["items"][0]["tmdb_id"] == 42

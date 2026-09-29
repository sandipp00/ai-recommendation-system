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


def test_unconfigured_service_returns_503():
    client = TestClient(create_app())

    response = client.post(
        "/recommend",
        json={"query": "test", "top_k": 1},
    )

    assert response.status_code == 503

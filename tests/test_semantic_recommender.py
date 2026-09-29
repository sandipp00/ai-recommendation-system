import pandas as pd
import pytest

from src.semantic_recommender import SemanticRecommender


@pytest.fixture
def recommender(monkeypatch):
    class FakeModel:
        def encode(self, texts, normalize_embeddings=True, show_progress_bar=False):
            vectors = {
                "space astronaut survival": [1.0, 0.0, 0.0],
                "science fiction space astronaut": [1.0, 0.0, 0.0],
                "detective killer": [0.0, 1.0, 0.0],
                "romantic comedy": [0.0, 0.0, 1.0],
            }
            return [vectors[text] for text in texts]

    monkeypatch.setattr(
        "src.semantic_recommender.SentenceTransformer",
        lambda model_name: FakeModel(),
    )

    movies = pd.DataFrame(
        {
            "title": ["Space Movie", "Detective Movie", "Romance Movie"],
            "genres": ["Science Fiction", "Crime", "Romance"],
            "overview": ["Space", "Crime", "Love"],
            "profile": [
                "space astronaut survival",
                "detective killer",
                "romantic comedy",
            ],
        }
    )

    return SemanticRecommender(movies)


def test_semantic_query_returns_matching_movie(recommender):
    results = recommender.recommend(
        "science fiction space astronaut",
        top_k=2,
    )

    assert results[0].title == "Space Movie"
    assert results[0].score == pytest.approx(1.0)


def test_semantic_query_validates_input(recommender):
    with pytest.raises(ValueError, match="Query cannot be empty"):
        recommender.recommend("")


def test_semantic_similar_excludes_source(recommender):
    results = recommender.recommend_similar("Space Movie", top_k=2)

    assert all(result.title != "Space Movie" for result in results)

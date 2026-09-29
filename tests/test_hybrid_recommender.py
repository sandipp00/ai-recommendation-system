import pandas as pd
import pytest

from src.hybrid_recommender import HybridRecommender


class FakeResult:
    def __init__(self, title, score):
        self.title = title
        self.score = score


class FakeContentRecommender:
    def recommend(self, query, top_k):
        return [
            FakeResult("Movie A", 0.90),
            FakeResult("Movie B", 0.40),
            FakeResult("Movie C", 0.10),
        ]


class FakeSemanticRecommender:
    def recommend(self, query, top_k):
        return [
            FakeResult("Movie B", 0.95),
            FakeResult("Movie A", 0.60),
            FakeResult("Movie C", 0.20),
        ]


@pytest.fixture
def recommender():
    movies = pd.DataFrame(
        {
            "title": ["Movie A", "Movie B", "Movie C"],
            "genres": ["Drama", "Thriller", "Comedy"],
            "overview": ["A", "B", "C"],
            "vote_average": [8.0, 9.0, 6.0],
        }
    )

    return HybridRecommender(
        movies,
        FakeContentRecommender(),
        FakeSemanticRecommender(),
    )


def test_hybrid_recommender_returns_ranked_results(recommender):
    results = recommender.recommend("test query", top_k=2)

    assert len(results) == 2
    assert results[0].title == "Movie B"
    assert results[0].score > results[1].score


def test_hybrid_score_contains_component_scores(recommender):
    result = recommender.recommend("test query", top_k=1)[0]

    assert result.content_score == pytest.approx(0.40)
    assert result.semantic_score == pytest.approx(0.95)
    assert 0 <= result.popularity_score <= 1
    assert 0 <= result.score <= 1


def test_invalid_query_is_rejected(recommender):
    with pytest.raises(ValueError, match="Query cannot be empty"):
        recommender.recommend("")


def test_invalid_top_k_is_rejected(recommender):
    with pytest.raises(ValueError, match="top_k"):
        recommender.recommend("test", top_k=0)


def test_negative_weight_is_rejected():
    movies = pd.DataFrame(
        {
            "title": ["Movie"],
            "overview": ["Overview"],
            "profile": ["Profile"],
        }
    )

    with pytest.raises(ValueError, match="negative"):
        HybridRecommender(
            movies,
            FakeContentRecommender(),
            FakeSemanticRecommender(),
            content_weight=-1,
        )

from pathlib import Path

import pandas as pd

from src.hybrid_recommender import HybridRecommender


class FakeContent:
    def recommend(self, query, top_k):
        return [
            type("Result", (), {"title": "A", "score": 0.8})(),
            type("Result", (), {"title": "B", "score": 0.3})(),
        ]


class FakeSemantic:
    def recommend(self, query, top_k):
        return [
            type("Result", (), {"title": "A", "score": 0.7})(),
            type("Result", (), {"title": "B", "score": 0.9})(),
        ]


def test_hybrid_pipeline_components_are_compatible():
    movies = pd.DataFrame(
        {
            "title": ["A", "B"],
            "overview": ["A movie", "B movie"],
            "genres": ["Drama", "Thriller"],
            "vote_average": [7.0, 8.0],
        }
    )

    recommender = HybridRecommender(
        movies,
        FakeContent(),
        FakeSemantic(),
    )

    assert recommender.recommend("test", top_k=2)[0].title == "B"

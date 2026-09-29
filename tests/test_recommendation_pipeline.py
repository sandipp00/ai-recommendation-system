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


def test_light_pipeline_uses_content_without_semantic_model(tmp_path):
    from src import recommendation_pipeline

    dataset = tmp_path / "movies.csv"
    pd.DataFrame(
        {
            "title": ["A", "B"],
            "overview": ["space adventure", "romantic drama"],
            "genres": ["Science Fiction", "Drama"],
            "vote_average": [8.0, 7.0],
        }
    ).to_csv(dataset, index=False)

    recommender = recommendation_pipeline.build_light_recommender(dataset)
    results = recommender.recommend("space adventure", top_k=1)

    assert results[0].title == "A"
    assert results[0].semantic_score == 0.0

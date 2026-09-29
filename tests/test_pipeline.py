from pathlib import Path

from src.pipeline import build_recommender


DATASET = Path("data/raw/sample_movies.csv")


def test_build_recommender_from_sample_dataset():
    recommender = build_recommender(DATASET)

    results = recommender.recommend(
        "science fiction space survival",
        top_k=3,
    )

    assert len(results) == 3
    assert results[0].title in {
        "Interstellar",
        "The Martian",
        "Dune",
        "Arrival",
        "Blade Runner 2049",
    }

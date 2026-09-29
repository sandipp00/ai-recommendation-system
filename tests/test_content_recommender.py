import pandas as pd
import pytest

from src.content_recommender import ContentRecommender


@pytest.fixture
def recommender():
    movies = pd.DataFrame(
        {
            "title": [
                "Space Adventure",
                "Dark Detective",
                "Romantic Comedy",
                "AI Future",
            ],
            "genres": [
                "Science Fiction",
                "Crime Thriller",
                "Comedy Romance",
                "Science Fiction Drama",
            ],
            "overview": [
                "An astronaut survives in space.",
                "A detective hunts a dangerous killer.",
                "Two people fall in love through comedy.",
                "An artificial intelligence changes human life.",
            ],
            "profile": [
                "science fiction astronaut space survival",
                "crime thriller detective killer mystery",
                "comedy romance love relationship",
                "science fiction artificial intelligence technology",
            ],
        }
    )

    return ContentRecommender(movies)


def test_query_returns_relevant_movie(recommender):
    results = recommender.recommend(
        "science fiction space astronaut",
        top_k=2,
    )

    assert results[0].title == "Space Adventure"
    assert 0 <= results[0].score <= 1


def test_similar_movie_excludes_source(recommender):
    results = recommender.recommend_similar(
        "Space Adventure",
        top_k=3,
    )

    assert all(result.title != "Space Adventure" for result in results)


def test_unknown_movie_raises_error(recommender):
    with pytest.raises(ValueError, match="Movie not found"):
        recommender.recommend_similar("Unknown Movie")


def test_empty_query_raises_error(recommender):
    with pytest.raises(ValueError, match="Query cannot be empty"):
        recommender.recommend("")


def test_invalid_top_k_raises_error(recommender):
    with pytest.raises(ValueError, match="top_k"):
        recommender.recommend("science fiction", top_k=0)

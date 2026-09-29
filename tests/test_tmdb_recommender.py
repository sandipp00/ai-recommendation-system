import pandas as pd

from src.tmdb_recommender import TMDBLiveRecommender


class FakeTMDBClient:
    def discover_movies(self, *, page, sort_by, vote_count_gte, language="en-US"):
        if page > 1:
            return []
        if sort_by == "vote_average.desc":
            return [
                {
                    "id": 1,
                    "title": "Dark AI",
                    "overview": "A dark science fiction story about artificial intelligence.",
                    "genre_ids": [878, 53],
                    "vote_average": 8.8,
                    "vote_count": 9000,
                    "popularity": 80,
                    "release_date": "2024-01-01",
                    "poster_path": "/dark.jpg",
                },
                {
                    "id": 2,
                    "title": "Sunny Comedy",
                    "overview": "A lighthearted comedy about friendship.",
                    "genre_ids": [35],
                    "vote_average": 9.0,
                    "vote_count": 5000,
                    "popularity": 70,
                    "release_date": "2023-01-01",
                    "poster_path": None,
                },
            ]
        return [
            {
                "id": 1,
                "title": "Dark AI",
                "overview": "A dark science fiction story about artificial intelligence.",
                "genre_ids": [878, 53],
                "vote_average": 8.8,
                "vote_count": 9000,
                "popularity": 80,
                "release_date": "2024-01-01",
                "poster_path": "/dark.jpg",
            }
        ]

    def genre_map(self, language="en"):
        return {878: "Science Fiction", 53: "Thriller", 35: "Comedy"}


def test_tmdb_recommender_prefers_query_relevance():
    recommender = TMDBLiveRecommender(FakeTMDBClient(), pages=1)
    results = recommender.recommend(
        "dark science fiction artificial intelligence",
        top_k=1,
    )

    assert len(results) == 1
    assert results[0].title == "Dark AI"
    assert results[0].tmdb_id == 1
    assert results[0].vote_average == 8.8
    assert results[0].release_year == 2024


def test_tmdb_recommender_rejects_invalid_query():
    recommender = TMDBLiveRecommender(FakeTMDBClient(), pages=1)
    try:
        recommender.recommend("")
    except ValueError as exc:
        assert "Query cannot be empty" in str(exc)
    else:
        raise AssertionError("Expected ValueError")

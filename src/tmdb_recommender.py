"""Live TMDB recommender optimized for low-memory deployments."""

from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from math import log

import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from src.hybrid_recommender import HybridRecommendation
from src.tmdb_client import TMDBClient


@dataclass
class TMDBRecommendation(HybridRecommendation):
    """Recommendation enriched with live TMDB metadata."""

    tmdb_id: int = 0
    vote_average: float = 0.0
    vote_count: int = 0
    release_year: int | None = None
    poster_url: str = ""


class TMDBLiveRecommender:
    """Retrieve current high-rated TMDB movies and rank them against a query."""

    def __init__(
        self,
        client: TMDBClient,
        pages: int = 3,
        minimum_votes: int = 300,
    ) -> None:
        if pages < 1:
            raise ValueError("pages must be at least 1.")
        if minimum_votes < 1:
            raise ValueError("minimum_votes must be at least 1.")

        self.client = client
        self.pages = pages
        self.minimum_votes = minimum_votes
        self._genres: dict[int, str] | None = None

    @lru_cache(maxsize=1)
    def _candidate_frame(self) -> pd.DataFrame:
        """Build a small live candidate pool from high-rated and popular movies."""
        rows: dict[int, dict] = {}

        for page in range(1, self.pages + 1):
            for movie in self.client.discover_movies(
                page=page,
                sort_by="vote_average.desc",
                vote_count_gte=self.minimum_votes,
            ):
                rows[int(movie["id"])] = movie

        for page in range(1, min(self.pages, 2) + 1):
            for movie in self.client.discover_movies(
                page=page,
                sort_by="popularity.desc",
                vote_count_gte=max(100, self.minimum_votes // 2),
            ):
                rows[int(movie["id"])] = movie

        return pd.DataFrame(rows.values())

    def _genre_names(self, genre_ids: list[int]) -> str:
        if self._genres is None:
            self._genres = self.client.genre_map()
        return " | ".join(
            self._genres.get(int(genre_id), "")
            for genre_id in genre_ids
            if self._genres.get(int(genre_id))
        )

    @staticmethod
    def _bayesian_rating(
        ratings: pd.Series,
        votes: pd.Series,
        minimum_votes: int,
    ) -> pd.Series:
        """Shrink ratings toward the candidate-pool mean for low-vote titles."""
        ratings = pd.to_numeric(ratings, errors="coerce").fillna(0.0)
        votes = pd.to_numeric(votes, errors="coerce").fillna(0.0)
        mean_rating = float(ratings.mean()) if not ratings.empty else 0.0
        return (
            votes / (votes + minimum_votes) * ratings
            + minimum_votes / (votes + minimum_votes) * mean_rating
        )

    def recommend(self, query: str, top_k: int = 5) -> list[TMDBRecommendation]:
        if not query or not query.strip():
            raise ValueError("Query cannot be empty.")
        if top_k < 1:
            raise ValueError("top_k must be at least 1.")

        movies = self._candidate_frame()
        if movies.empty:
            return []

        movies["genres"] = movies["genre_ids"].apply(self._genre_names)
        movies["overview"] = movies["overview"].fillna("")
        movies["title"] = movies["title"].fillna("")
        movies["profile"] = (
            movies["title"].astype(str)
            + " "
            + movies["genres"].astype(str)
            + " "
            + movies["overview"].astype(str)
        )

        vectorizer = TfidfVectorizer(
            stop_words="english",
            ngram_range=(1, 2),
            max_features=12000,
        )
        matrix = vectorizer.fit_transform(movies["profile"])
        query_vector = vectorizer.transform([query.strip()])
        relevance = cosine_similarity(query_vector, matrix).ravel()

        ratings = pd.to_numeric(movies["vote_average"], errors="coerce").fillna(0.0)
        votes = pd.to_numeric(movies["vote_count"], errors="coerce").fillna(0.0)
        bayesian = self._bayesian_rating(ratings, votes, self.minimum_votes)

        rating_score = (bayesian / 10.0).clip(0.0, 1.0)
        log_popularity = movies["popularity"].apply(
            lambda value: log(max(float(value), 0.0) + 1.0)
        )
        if log_popularity.max() == log_popularity.min():
            popularity_score = pd.Series(0.0, index=movies.index)
        else:
            popularity_score = (
                (log_popularity - log_popularity.min())
                / (log_popularity.max() - log_popularity.min())
            )

        final_score = (
            0.55 * relevance
            + 0.30 * rating_score
            + 0.15 * popularity_score
        )

        movies = movies.assign(
            relevance=relevance,
            rating_score=rating_score,
            popularity_score=popularity_score,
            final_score=final_score,
        ).sort_values("final_score", ascending=False)

        recommendations: list[TMDBRecommendation] = []
        for _, row in movies.head(top_k).iterrows():
            release_date = str(row.get("release_date", "") or "")
            year = int(release_date[:4]) if release_date[:4].isdigit() else None
            recommendations.append(
                TMDBRecommendation(
                    title=str(row["title"]),
                    score=float(row["final_score"]),
                    content_score=float(row["relevance"]),
                    semantic_score=0.0,
                    popularity_score=float(row["rating_score"]),
                    overview=str(row["overview"]),
                    genres=str(row["genres"]),
                    tmdb_id=int(row["id"]),
                    vote_average=float(row["vote_average"]),
                    vote_count=int(row["vote_count"]),
                    release_year=year,
                    poster_url=(
                        f"https://image.tmdb.org/t/p/w500{row['poster_path']}"
                        if row.get("poster_path")
                        else ""
                    ),
                )
            )

        return recommendations

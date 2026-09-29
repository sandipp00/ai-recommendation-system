"""TF-IDF content-based movie recommender."""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


@dataclass
class Recommendation:
    """A single movie recommendation."""

    title: str
    score: float
    overview: str
    genres: str


class ContentRecommender:
    """Recommend movies using TF-IDF profile similarity."""

    def __init__(self, movies: pd.DataFrame) -> None:
        if "title" not in movies.columns or "profile" not in movies.columns:
            raise ValueError("Movies must contain 'title' and 'profile' columns.")

        if movies.empty:
            raise ValueError("Movies dataset cannot be empty.")

        self.movies = movies.reset_index(drop=True).copy()
        self.vectorizer = TfidfVectorizer(
            stop_words="english",
            ngram_range=(1, 2),
            max_features=10000,
        )
        self.matrix = self.vectorizer.fit_transform(
            self.movies["profile"].fillna("")
        )

    def recommend(
        self,
        query: str,
        top_k: int = 5,
        exclude_title: str | None = None,
    ) -> list[Recommendation]:
        """Return the top matching movies for a natural-language query."""
        if not query or not query.strip():
            raise ValueError("Query cannot be empty.")

        if top_k < 1:
            raise ValueError("top_k must be at least 1.")

        query_vector = self.vectorizer.transform([query.strip()])
        scores = cosine_similarity(query_vector, self.matrix).ravel()

        ranked_indices = scores.argsort()[::-1]

        recommendations: list[Recommendation] = []

        for index in ranked_indices:
            row = self.movies.iloc[index]

            if exclude_title and row["title"].casefold() == exclude_title.casefold():
                continue

            recommendations.append(
                Recommendation(
                    title=str(row["title"]),
                    score=float(scores[index]),
                    overview=str(row.get("overview", "")),
                    genres=str(row.get("genres", "")),
                )
            )

            if len(recommendations) == top_k:
                break

        return recommendations

    def recommend_similar(
        self,
        title: str,
        top_k: int = 5,
    ) -> list[Recommendation]:
        """Recommend movies similar to an existing movie title."""
        matches = self.movies[
            self.movies["title"].str.casefold() == title.strip().casefold()
        ]

        if matches.empty:
            raise ValueError(f"Movie not found: {title}")

        movie_index = matches.index[0]
        scores = cosine_similarity(
            self.matrix[movie_index],
            self.matrix,
        ).ravel()

        ranked_indices = scores.argsort()[::-1]

        recommendations: list[Recommendation] = []

        for index in ranked_indices:
            if index == movie_index:
                continue

            row = self.movies.iloc[index]

            recommendations.append(
                Recommendation(
                    title=str(row["title"]),
                    score=float(scores[index]),
                    overview=str(row.get("overview", "")),
                    genres=str(row.get("genres", "")),
                )
            )

            if len(recommendations) == top_k:
                break

        return recommendations

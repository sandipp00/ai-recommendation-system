"""Semantic movie recommender using Sentence Transformers."""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity


@dataclass
class SemanticRecommendation:
    """A semantic movie recommendation."""

    title: str
    score: float
    overview: str
    genres: str


class SemanticRecommender:
    """Recommend movies using dense semantic embeddings."""

    def __init__(
        self,
        movies: pd.DataFrame,
        model_name: str = "all-MiniLM-L6-v2",
    ) -> None:
        if "title" not in movies.columns or "profile" not in movies.columns:
            raise ValueError("Movies must contain 'title' and 'profile' columns.")

        if movies.empty:
            raise ValueError("Movies dataset cannot be empty.")

        self.movies = movies.reset_index(drop=True).copy()
        self.model_name = model_name
        self.model = SentenceTransformer(model_name)

        profiles = self.movies["profile"].fillna("").astype(str).tolist()
        self.embeddings = self.model.encode(
            profiles,
            normalize_embeddings=True,
            show_progress_bar=False,
        )

    def recommend(
        self,
        query: str,
        top_k: int = 5,
        exclude_title: str | None = None,
    ) -> list[SemanticRecommendation]:
        """Return semantically relevant movies for a natural-language query."""
        if not query or not query.strip():
            raise ValueError("Query cannot be empty.")

        if top_k < 1:
            raise ValueError("top_k must be at least 1.")

        query_embedding = self.model.encode(
            [query.strip()],
            normalize_embeddings=True,
            show_progress_bar=False,
        )

        scores = cosine_similarity(
            query_embedding,
            self.embeddings,
        ).ravel()

        ranked_indices = scores.argsort()[::-1]

        recommendations: list[SemanticRecommendation] = []

        for index in ranked_indices:
            row = self.movies.iloc[index]

            if exclude_title and row["title"].casefold() == exclude_title.casefold():
                continue

            recommendations.append(
                SemanticRecommendation(
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
    ) -> list[SemanticRecommendation]:
        """Recommend movies semantically similar to an existing title."""
        matches = self.movies[
            self.movies["title"].str.casefold() == title.strip().casefold()
        ]

        if matches.empty:
            raise ValueError(f"Movie not found: {title}")

        movie_index = matches.index[0]

        scores = cosine_similarity(
            self.embeddings[movie_index : movie_index + 1],
            self.embeddings,
        ).ravel()

        ranked_indices = scores.argsort()[::-1]

        recommendations: list[SemanticRecommendation] = []

        for index in ranked_indices:
            if index == movie_index:
                continue

            row = self.movies.iloc[index]

            recommendations.append(
                SemanticRecommendation(
                    title=str(row["title"]),
                    score=float(scores[index]),
                    overview=str(row.get("overview", "")),
                    genres=str(row.get("genres", "")),
                )
            )

            if len(recommendations) == top_k:
                break

        return recommendations

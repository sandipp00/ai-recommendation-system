"""Hybrid recommendation engine combining lexical and semantic signals."""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd


@dataclass
class HybridRecommendation:
    """A ranked recommendation with component scores."""

    title: str
    score: float
    content_score: float
    semantic_score: float
    popularity_score: float
    overview: str
    genres: str


class HybridRecommender:
    """Combine TF-IDF, semantic, and popularity signals."""

    def __init__(
        self,
        movies: pd.DataFrame,
        content_recommender,
        semantic_recommender,
        content_weight: float = 0.35,
        semantic_weight: float = 0.50,
        popularity_weight: float = 0.15,
    ) -> None:
        if movies.empty:
            raise ValueError("Movies dataset cannot be empty.")

        weights = [
            content_weight,
            semantic_weight,
            popularity_weight,
        ]

        if any(weight < 0 for weight in weights):
            raise ValueError("Recommendation weights cannot be negative.")

        if sum(weights) <= 0:
            raise ValueError("At least one recommendation weight must be positive.")

        total = sum(weights)

        self.movies = movies.reset_index(drop=True).copy()
        self.content_recommender = content_recommender
        self.semantic_recommender = semantic_recommender

        self.content_weight = content_weight / total
        self.semantic_weight = semantic_weight / total
        self.popularity_weight = popularity_weight / total

    def _popularity_scores(self) -> dict[str, float]:
        """Return normalized vote-average scores keyed by movie title."""
        if "vote_average" not in self.movies.columns:
            return {title: 0.0 for title in self.movies["title"]}

        scores = pd.to_numeric(
            self.movies["vote_average"],
            errors="coerce",
        ).fillna(0.0)

        if scores.max() == scores.min():
            normalized = pd.Series(0.0, index=self.movies.index)
        else:
            normalized = (scores - scores.min()) / (scores.max() - scores.min())

        return dict(zip(self.movies["title"], normalized, strict=True))

    @staticmethod
    def _score_map(results) -> dict[str, float]:
        return {result.title: result.score for result in results}

    def recommend(self, query: str, top_k: int = 5) -> list[HybridRecommendation]:
        """Return hybrid-ranked recommendations for a natural-language query."""
        if not query or not query.strip():
            raise ValueError("Query cannot be empty.")

        if top_k < 1:
            raise ValueError("top_k must be at least 1.")

        content_results = self.content_recommender.recommend(
            query,
            top_k=len(self.movies),
        )
        semantic_results = self.semantic_recommender.recommend(
            query,
            top_k=len(self.movies),
        )

        content_scores = self._score_map(content_results)
        semantic_scores = self._score_map(semantic_results)
        popularity_scores = self._popularity_scores()

        ranked = []

        for title in self.movies["title"]:
            content_score = content_scores.get(title, 0.0)
            semantic_score = semantic_scores.get(title, 0.0)
            popularity_score = float(popularity_scores.get(title, 0.0))

            final_score = (
                self.content_weight * content_score
                + self.semantic_weight * semantic_score
                + self.popularity_weight * popularity_score
            )

            ranked.append(
                (
                    title,
                    final_score,
                    content_score,
                    semantic_score,
                    popularity_score,
                )
            )

        ranked.sort(key=lambda item: item[1], reverse=True)

        movie_lookup = self.movies.set_index("title", drop=False)

        recommendations = []

        for (
            title,
            final_score,
            content_score,
            semantic_score,
            popularity_score,
        ) in ranked[:top_k]:
            row = movie_lookup.loc[title]

            recommendations.append(
                HybridRecommendation(
                    title=title,
                    score=float(final_score),
                    content_score=float(content_score),
                    semantic_score=float(semantic_score),
                    popularity_score=float(popularity_score),
                    overview=str(row.get("overview", "")),
                    genres=str(row.get("genres", "")),
                )
            )

        return recommendations

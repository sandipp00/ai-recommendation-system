"""Build grounded context for LLM recommendation generation."""

from __future__ import annotations


def build_movie_context(recommendations, max_items: int = 5) -> str:
    """Convert retrieved recommendations into a compact LLM context."""
    if max_items < 1:
        raise ValueError("max_items must be at least 1.")

    lines = []

    for index, recommendation in enumerate(recommendations[:max_items], start=1):
        lines.extend(
            [
                f"Movie {index}: {recommendation.title}",
                f"Genres: {recommendation.genres}",
                f"Overview: {recommendation.overview}",
                f"Retrieval score: {recommendation.score:.4f}",
                "",
            ]
        )

    return "\n".join(lines).strip()

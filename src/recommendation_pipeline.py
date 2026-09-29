"""End-to-end retrieval and ranking pipeline."""

from pathlib import Path

from src.content_recommender import ContentRecommender
from src.data_loader import build_movie_profile, load_movies
from src.hybrid_recommender import HybridRecommender
from src.preprocessing import clean_movies
from src.semantic_recommender import SemanticRecommender


def build_hybrid_recommender(
    dataset_path: str | Path,
    semantic_model: str = "all-MiniLM-L6-v2",
) -> HybridRecommender:
    """Build the complete development recommendation pipeline."""
    movies = load_movies(dataset_path)
    movies = clean_movies(movies)
    movies = build_movie_profile(movies)

    content_recommender = ContentRecommender(movies)
    semantic_recommender = SemanticRecommender(
        movies,
        model_name=semantic_model,
    )

    return HybridRecommender(
        movies,
        content_recommender,
        semantic_recommender,
    )

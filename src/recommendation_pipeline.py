"""End-to-end retrieval and ranking pipeline."""

from pathlib import Path

from src.content_recommender import ContentRecommender
from src.data_loader import build_movie_profile, load_movies
from src.hybrid_recommender import HybridRecommender, LightweightRecommender
from src.preprocessing import clean_movies


def _prepare_movies(dataset_path: str | Path):
    movies = load_movies(dataset_path)
    movies = clean_movies(movies)
    return build_movie_profile(movies)


def build_hybrid_recommender(
    dataset_path: str | Path,
    semantic_model: str = "all-MiniLM-L6-v2",
) -> HybridRecommender:
    """Build the full semantic + lexical recommendation pipeline."""
    from src.semantic_recommender import SemanticRecommender

    movies = _prepare_movies(dataset_path)
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


def build_light_recommender(
    dataset_path: str | Path,
) -> LightweightRecommender:
    """Build a low-memory pipeline without Sentence Transformers or PyTorch."""
    movies = _prepare_movies(dataset_path)
    content_recommender = ContentRecommender(movies)

    return LightweightRecommender(
        movies,
        content_recommender,
    )

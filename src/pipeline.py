"""Convenience pipeline for loading and preparing movie data."""

from pathlib import Path

from src.content_recommender import ContentRecommender
from src.data_loader import build_movie_profile, load_movies
from src.preprocessing import clean_movies


def build_recommender(dataset_path: str | Path) -> ContentRecommender:
    """Load, clean, profile, and initialize a movie recommender."""
    movies = load_movies(dataset_path)
    movies = clean_movies(movies)
    movies = build_movie_profile(movies)

    return ContentRecommender(movies)

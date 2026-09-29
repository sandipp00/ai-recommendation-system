"""Data loading utilities for the recommendation system."""

from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW_DATA_DIR = PROJECT_ROOT / "data" / "raw"
PROCESSED_DATA_DIR = PROJECT_ROOT / "data" / "processed"


def load_movies(path: str | Path) -> pd.DataFrame:
    """Load a movie CSV and validate the minimum required columns."""
    path = Path(path)

    if not path.exists():
        raise FileNotFoundError(f"Movie dataset not found: {path}")

    df = pd.read_csv(path)

    required_columns = {"title", "overview"}
    missing = required_columns - set(df.columns)

    if missing:
        raise ValueError(
            f"Dataset is missing required columns: {sorted(missing)}"
        )

    return df


def build_movie_profile(df: pd.DataFrame) -> pd.DataFrame:
    """Create a normalized text profile used by recommendation models."""
    result = df.copy()

    profile_columns = [
        column
        for column in ["genres", "keywords", "overview", "cast", "director"]
        if column in result.columns
    ]

    if "title" not in result.columns:
        raise ValueError("Dataset must contain a 'title' column.")

    for column in profile_columns:
        result[column] = result[column].fillna("").astype(str)

    result["profile"] = (
        result[profile_columns]
        .agg(" ".join, axis=1)
        .str.replace(r"\s+", " ", regex=True)
        .str.strip()
    )

    return result

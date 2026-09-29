"""Preprocessing utilities for movie recommendation data."""

import pandas as pd


def clean_movies(df: pd.DataFrame) -> pd.DataFrame:
    """Clean and standardize the movie dataset."""
    result = df.copy()

    required = {"title", "overview"}
    missing = required - set(result.columns)
    if missing:
        raise ValueError(f"Dataset is missing required columns: {sorted(missing)}")

    result = result.drop_duplicates(subset=["title"]).copy()

    text_columns = [
        "title",
        "genres",
        "keywords",
        "overview",
        "cast",
        "director",
    ]

    for column in text_columns:
        if column in result.columns:
            result[column] = result[column].fillna("").astype(str).str.strip()

    if "release_year" in result.columns:
        result["release_year"] = pd.to_numeric(
            result["release_year"], errors="coerce"
        ).astype("Int64")

    for column in ["vote_average", "vote_count"]:
        if column in result.columns:
            result[column] = pd.to_numeric(result[column], errors="coerce")

    result = result[result["title"].ne("")].reset_index(drop=True)

    return result

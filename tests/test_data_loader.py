import pandas as pd
import pytest

from src.data_loader import build_movie_profile, load_movies


def test_build_movie_profile_combines_available_columns():
    df = pd.DataFrame(
        {
            "title": ["Inception"],
            "genres": ["Science Fiction Thriller"],
            "overview": ["A dream-based thriller."],
        }
    )

    result = build_movie_profile(df)

    assert result.loc[0, "profile"] == (
        "Science Fiction Thriller A dream-based thriller."
    )


def test_build_movie_profile_handles_missing_values():
    df = pd.DataFrame(
        {
            "title": ["Movie"],
            "genres": [None],
            "overview": ["A story."],
        }
    )

    result = build_movie_profile(df)

    assert result.loc[0, "profile"] == "A story."


def test_load_movies_rejects_missing_required_columns(tmp_path):
    path = tmp_path / "movies.csv"
    pd.DataFrame({"name": ["Movie"]}).to_csv(path, index=False)

    with pytest.raises(ValueError, match="title"):
        load_movies(path)

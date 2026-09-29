import pandas as pd

from src.preprocessing import clean_movies


def test_clean_movies_removes_duplicate_titles():
    df = pd.DataFrame(
        {
            "title": ["Movie", "Movie"],
            "overview": ["First", "Second"],
        }
    )

    result = clean_movies(df)

    assert len(result) == 1
    assert result.loc[0, "title"] == "Movie"


def test_clean_movies_normalizes_missing_text():
    df = pd.DataFrame(
        {
            "title": [" Movie "],
            "overview": [None],
        }
    )

    result = clean_movies(df)

    assert result.loc[0, "title"] == "Movie"
    assert result.loc[0, "overview"] == ""

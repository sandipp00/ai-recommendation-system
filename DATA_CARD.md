# Data Card

## Development Dataset

Step 2 includes a small synthetic movie dataset at:

`data/raw/sample_movies.csv`

It is intentionally committed because it is small, reproducible, and suitable for testing the complete pipeline.

## Production Dataset

The planned production dataset is the TMDB 5000 Movie Dataset, which contains movie metadata such as titles, genres, keywords, overviews, release dates, ratings, and vote counts. Public copies describe the movie metadata and a separate credits dataset. citeturn0search0turn0search2

The full external dataset should be downloaded separately and kept outside Git version control. This avoids unnecessarily redistributing third-party data and keeps the repository lightweight.

Expected production files:

```text
data/raw/tmdb_5000_movies.csv
data/raw/tmdb_5000_credits.csv
```

The preprocessing layer is designed so the production dataset can replace the sample dataset without changing the recommendation architecture.

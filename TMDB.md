# Free live movie data with TMDB

The recommendation system can use TMDB as a live movie source instead of relying only on the small sample dataset.

TMDB provides movie metadata, ratings, vote counts, popularity, and discovery filters. Its developer API is free for non-commercial use with the required attribution.

## Setup

Create a TMDB account and obtain an API Read Access Token or API key from the API settings.

Official documentation:
- https://developer.themoviedb.org/docs/getting-started
- https://developer.themoviedb.org/docs/authentication-application
- https://developer.themoviedb.org/reference/discover-movie

Never commit the credential to GitHub.

## Local PowerShell

Using a v4 access token:

~~~powershell
$env:TMDB_ACCESS_TOKEN="YOUR_TOKEN"
$env:TMDB_ENABLED="true"
uvicorn api.main:app --reload
~~~

Using a v3 API key:

~~~powershell
$env:TMDB_API_KEY="YOUR_API_KEY"
$env:TMDB_ENABLED="true"
uvicorn api.main:app --reload
~~~

The live recommender fetches a small candidate pool from TMDB at request time and combines:

- 55% natural-language query relevance
- 30% Bayesian-adjusted TMDB rating
- 15% current TMDB popularity

The Bayesian adjustment reduces the influence of movies with very few votes.

## Render Free

Add the credential as a secret Environment Variable in the Render service:

~~~text
TMDB_ENABLED=true
TMDB_ACCESS_TOKEN=your-secret-token
~~~

Do not put the secret in render.yaml.

The service remains in low-memory mode because TMDB is queried over HTTP and only a small candidate pool is ranked locally.

If TMDB is disabled or no credential is configured, the existing local recommendation pipeline remains available.

## Attribution

When TMDB data is displayed, follow TMDB's current attribution and branding requirements. TMDB currently requires a prominent notice that the product uses the TMDB API but is not endorsed or certified by TMDB.

Review the current TMDB terms before using the project commercially.

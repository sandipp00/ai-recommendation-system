"""Small TMDB API client for live, non-commercial movie discovery."""

from __future__ import annotations

import os
from typing import Any

import requests


class TMDBClient:
    """Fetch movie metadata from TMDB using a v3 API key or v4 bearer token."""

    BASE_URL = "https://api.themoviedb.org/3"

    def __init__(
        self,
        api_key: str | None = None,
        access_token: str | None = None,
        timeout: int = 15,
    ) -> None:
        self.api_key = api_key or os.getenv("TMDB_API_KEY")
        self.access_token = access_token or os.getenv("TMDB_ACCESS_TOKEN")
        self.timeout = timeout

        if not self.api_key and not self.access_token:
            raise ValueError(
                "TMDB credentials are required. Set TMDB_API_KEY or TMDB_ACCESS_TOKEN."
            )

    def _get(self, path: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
        headers = {"accept": "application/json"}
        if self.access_token:
            headers["Authorization"] = f"Bearer {self.access_token}"

        request_params = dict(params or {})
        if self.api_key and not self.access_token:
            request_params["api_key"] = self.api_key

        response = requests.get(
            f"{self.BASE_URL}{path}",
            params=request_params,
            headers=headers,
            timeout=self.timeout,
        )
        response.raise_for_status()
        return response.json()

    def discover_movies(
        self,
        *,
        page: int = 1,
        sort_by: str = "vote_average.desc",
        vote_count_gte: int = 300,
        language: str = "en-US",
    ) -> list[dict[str, Any]]:
        """Return a page of high-signal TMDB movie candidates."""
        payload = self._get(
            "/discover/movie",
            {
                "include_adult": "false",
                "include_video": "false",
                "language": language,
                "page": page,
                "sort_by": sort_by,
                "vote_count.gte": vote_count_gte,
            },
        )
        return payload.get("results", [])

    def genre_map(self, language: str = "en") -> dict[int, str]:
        """Return TMDB movie genre IDs mapped to human-readable names."""
        payload = self._get("/genre/movie/list", {"language": language})
        return {
            int(item["id"]): str(item["name"])
            for item in payload.get("genres", [])
        }

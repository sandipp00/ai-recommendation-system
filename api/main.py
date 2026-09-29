"""FastAPI application for the recommendation system."""

from __future__ import annotations

import os
from datetime import date, timedelta
from functools import lru_cache
from pathlib import Path

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from src.rag_recommender import RAGRecommender
from src.tmdb_client import TMDBClient
from src.tmdb_recommender import TMDBLiveRecommender
from src.template_llm import TemplateExplanationLLM
from src.recommendation_pipeline import build_hybrid_recommender, build_light_recommender


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DATASET = PROJECT_ROOT / "data" / "raw" / "sample_movies.csv"


class RecommendationRequest(BaseModel):
    """Request payload for recommendations."""

    query: str = Field(..., min_length=1, max_length=500)
    top_k: int = Field(default=5, ge=1, le=20)


class RecommendationItem(BaseModel):
    """Structured recommendation returned by the API."""

    title: str
    score: float
    content_score: float
    semantic_score: float
    popularity_score: float
    overview: str
    genres: str
    tmdb_id: int | None = None
    vote_average: float | None = None
    vote_count: int | None = None
    release_year: int | None = None
    poster_url: str = ""


class RecommendationResponse(BaseModel):
    """Complete recommendation API response."""

    query: str
    recommendations: list[RecommendationItem]
    explanation: str


class BrowseResponse(BaseModel):
    """Live TMDB discovery collection."""

    category: str
    items: list[RecommendationItem]


def _tmdb_client() -> TMDBClient:
    """Create a TMDB client when live credentials are configured."""
    enabled = os.getenv("TMDB_ENABLED", "false").lower() in {"1", "true", "yes"}
    if not enabled or not (os.getenv("TMDB_API_KEY") or os.getenv("TMDB_ACCESS_TOKEN")):
        raise HTTPException(
            status_code=503,
            detail="Live TMDB discovery is not enabled.",
        )
    return TMDBClient()


def _tmdb_item(movie: dict, genres: dict[int, str]) -> RecommendationItem:
    """Normalize a TMDB movie payload for the frontend."""
    genre_ids = movie.get("genre_ids") or []
    genre_text = " | ".join(
        genres.get(int(genre_id), "")
        for genre_id in genre_ids
        if genres.get(int(genre_id))
    )
    release_date = str(movie.get("release_date", "") or "")
    year = int(release_date[:4]) if release_date[:4].isdigit() else None
    poster_path = movie.get("poster_path")
    return RecommendationItem(
        title=str(movie.get("title") or movie.get("original_title") or "Untitled"),
        score=float(movie.get("popularity") or 0.0),
        content_score=float(movie.get("vote_average") or 0.0) / 10.0,
        semantic_score=0.0,
        popularity_score=float(movie.get("popularity") or 0.0),
        overview=str(movie.get("overview") or ""),
        genres=genre_text,
        tmdb_id=int(movie["id"]) if movie.get("id") is not None else None,
        vote_average=float(movie.get("vote_average") or 0.0),
        vote_count=int(movie.get("vote_count") or 0),
        release_year=year,
        poster_url=(
            f"https://image.tmdb.org/t/p/w500{poster_path}"
            if poster_path
            else ""
        ),
    )


@lru_cache(maxsize=1)
def build_service() -> RAGRecommender:
    """Build the real retrieval + RAG service on first recommendation request."""
    dataset_path = Path(
        os.getenv("RECOMMENDATION_DATASET", str(DEFAULT_DATASET))
    )
    semantic_model = os.getenv(
        "SEMANTIC_MODEL",
        "all-MiniLM-L6-v2",
    )
    llm_enabled = os.getenv("LLM_ENABLED", "true").lower() in {"1", "true", "yes"}
    # Render Free is intentionally kept in low-memory mode unless explicitly overridden.
    # Local development retains the full semantic pipeline by default.
    default_semantic_enabled = "false" if os.getenv("RENDER") == "true" else "true"
    semantic_enabled = os.getenv(
        "SEMANTIC_ENABLED",
        default_semantic_enabled,
    ).lower() in {"1", "true", "yes"}
    llm_model = os.getenv(
        "LLM_MODEL",
        "EleutherAI/gpt-neo-125M",
    )
    tmdb_enabled = os.getenv("TMDB_ENABLED", "false").lower() in {"1", "true", "yes"}

    if tmdb_enabled and (os.getenv("TMDB_API_KEY") or os.getenv("TMDB_ACCESS_TOKEN")):
        hybrid = TMDBLiveRecommender(
            TMDBClient(),
            pages=int(os.getenv("TMDB_PAGES", "3")),
            minimum_votes=int(os.getenv("TMDB_MINIMUM_VOTES", "300")),
        )
    elif semantic_enabled:
        hybrid = build_hybrid_recommender(
            dataset_path,
            semantic_model=semantic_model,
        )
    else:
        hybrid = build_light_recommender(dataset_path)
    if llm_enabled:
        from src.llm_client import HuggingFaceLLM

        llm = HuggingFaceLLM(model_name=llm_model)
    else:
        llm = TemplateExplanationLLM()
    return RAGRecommender(hybrid, llm)


def create_app(rag_recommender: RAGRecommender | None = None) -> FastAPI:
    """Create the FastAPI application with optional dependency injection."""
    app = FastAPI(
        title="AI Recommendation System API",
        version="0.1.0",
        description="LLM-powered movie recommendation API.",
    )

    service = rag_recommender

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok", "service": "recommendation-api"}

    @app.post("/recommend", response_model=RecommendationResponse)
    @app.get("/browse/{category}", response_model=BrowseResponse)
    def browse(category: str) -> BrowseResponse:
        """Return a curated live TMDB discovery collection."""
        client = _tmdb_client()
        normalized = category.strip().lower()
        try:
            if normalized == "trending":
                movies = client.trending_movies("week")
            elif normalized == "top-rated":
                movies = client.discover_movies(
                    sort_by="vote_average.desc",
                    vote_count_gte=1000,
                )
            elif normalized == "popular":
                movies = client.discover_movies(
                    sort_by="popularity.desc",
                    vote_count_gte=300,
                )
            elif normalized == "hidden-gems":
                movies = client.discover_movies(
                    sort_by="vote_average.desc",
                    vote_count_gte=100,
                    vote_average_gte=7.2,
                    vote_average_lte=9.5,
                )
            elif normalized == "new-releases":
                today = date.today()
                start = today - timedelta(days=120)
                movies = client.discover_movies(
                    sort_by="primary_release_date.desc",
                    vote_count_gte=50,
                    **{
                        "primary_release_date.gte": start.isoformat(),
                        "primary_release_date.lte": today.isoformat(),
                    },
                )
            else:
                raise HTTPException(
                    status_code=404,
                    detail="Unknown discovery category.",
                )

            genres = client.genre_map()
            items = [_tmdb_item(movie, genres) for movie in movies[:12]]
            return BrowseResponse(category=normalized, items=items)
        except HTTPException:
            raise
        except Exception as exc:
            raise HTTPException(
                status_code=502,
                detail="TMDB discovery request failed.",
            ) from exc

    @app.get("/movie/{movie_id}/similar", response_model=BrowseResponse)
    def similar_movies(movie_id: int) -> BrowseResponse:
        """Return live TMDB recommendations for a selected movie."""
        client = _tmdb_client()
        try:
            movies = client.movie_recommendations(movie_id)
            genres = client.genre_map()
            items = [_tmdb_item(movie, genres) for movie in movies[:10]]
            return BrowseResponse(category="similar", items=items)
        except Exception as exc:
            raise HTTPException(
                status_code=502,
                detail="TMDB similar-movie request failed.",
            ) from exc

    def recommend(request: RecommendationRequest) -> RecommendationResponse:
        active_service = service or build_service()

        try:
            result = active_service.recommend(
                request.query,
                top_k=request.top_k,
            )
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
        except Exception as exc:
            raise HTTPException(
                status_code=500,
                detail="Recommendation service failed.",
            ) from exc

        recommendations = [
            RecommendationItem(
                title=item.title,
                score=float(item.score),
                content_score=float(item.content_score),
                semantic_score=float(item.semantic_score),
                popularity_score=float(item.popularity_score),
                overview=item.overview,
                genres=item.genres,
                tmdb_id=getattr(item, "tmdb_id", None),
                vote_average=getattr(item, "vote_average", None),
                vote_count=getattr(item, "vote_count", None),
                release_year=getattr(item, "release_year", None),
                poster_url=getattr(item, "poster_url", ""),
            )
            for item in result.candidates
        ]

        return RecommendationResponse(
            query=result.user_query,
            recommendations=recommendations,
            explanation=result.response,
        )

    return app


app = create_app()

"""FastAPI application for the recommendation system."""

from __future__ import annotations

import os
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

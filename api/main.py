"""FastAPI application for the recommendation system."""

from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from src.llm_client import HuggingFaceLLM
from src.rag_recommender import RAGRecommender
from src.template_llm import TemplateExplanationLLM
from src.recommendation_pipeline import build_hybrid_recommender


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
    llm_model = os.getenv(
        "LLM_MODEL",
        "EleutherAI/gpt-neo-125M",
    )

    hybrid = build_hybrid_recommender(
        dataset_path,
        semantic_model=semantic_model,
    )
    llm = HuggingFaceLLM(model_name=llm_model) if llm_enabled else TemplateExplanationLLM()
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

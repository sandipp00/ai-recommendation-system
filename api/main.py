"""FastAPI application for the recommendation system."""

from __future__ import annotations

from dataclasses import asdict
from pathlib import Path
from typing import Callable

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from src.recommendation_pipeline import build_hybrid_recommender
from src.rag_recommender import RAGRecommender


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


def create_app(rag_recommender: RAGRecommender | None = None) -> FastAPI:
    """Create the FastAPI application with an optional injected service."""
    app = FastAPI(
        title="AI Recommendation System API",
        version="0.1.0",
        description="LLM-powered movie recommendation API.",
    )

    service = rag_recommender

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    @app.post("/recommend", response_model=RecommendationResponse)
    def recommend(request: RecommendationRequest) -> RecommendationResponse:
        if service is None:
            raise HTTPException(
                status_code=503,
                detail="Recommendation service is not configured.",
            )

        try:
            result = service.recommend(
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

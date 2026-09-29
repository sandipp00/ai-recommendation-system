"""LLM-powered grounded recommendation service."""

from __future__ import annotations

from dataclasses import dataclass

from src.prompt_builder import build_recommendation_prompt
from src.rag_context import build_movie_context


@dataclass
class RAGRecommendation:
    """Recommendation response generated from retrieved candidates."""

    user_query: str
    context: str
    prompt: str
    response: str
    candidates: list


class RAGRecommender:
    """Retrieve candidates, ground an LLM prompt, and generate an answer."""

    def __init__(self, hybrid_recommender, llm_client) -> None:
        self.hybrid_recommender = hybrid_recommender
        self.llm_client = llm_client

    def recommend(self, user_query: str, top_k: int = 5) -> RAGRecommendation:
        """Generate a grounded recommendation response."""
        candidates = self.hybrid_recommender.recommend(
            user_query,
            top_k=top_k,
        )

        context = build_movie_context(candidates)
        prompt = build_recommendation_prompt(user_query, context)
        response = self.llm_client.generate(prompt)

        return RAGRecommendation(
            user_query=user_query,
            context=context,
            prompt=prompt,
            response=response,
            candidates=candidates,
        )

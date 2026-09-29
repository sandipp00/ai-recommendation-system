import pytest

from src.prompt_builder import build_recommendation_prompt
from src.rag_context import build_movie_context
from src.rag_recommender import RAGRecommender


class Candidate:
    title = "Inception"
    genres = "Science Fiction|Thriller"
    overview = "A thief enters dreams."
    score = 0.91


class FakeHybrid:
    def recommend(self, query, top_k):
        return [Candidate()]


class FakeLLM:
    def generate(self, prompt):
        assert "Inception" in prompt
        assert "Do not invent movie titles" in prompt
        return "1. Inception — It matches the requested dream-based thriller theme."


def test_context_contains_retrieved_movie():
    context = build_movie_context([Candidate()])

    assert "Inception" in context
    assert "A thief enters dreams." in context
    assert "0.9100" in context


def test_prompt_requires_grounded_recommendations():
    prompt = build_recommendation_prompt(
        "I want a dream thriller",
        "Movie 1: Inception\nGenres: Thriller",
    )

    assert "Use only the movies provided in the context." in prompt
    assert "I want a dream thriller" in prompt


def test_rag_recommender_uses_retrieval_then_llm():
    result = RAGRecommender(FakeHybrid(), FakeLLM()).recommend(
        "I want a dream thriller",
        top_k=1,
    )

    assert result.candidates[0].title == "Inception"
    assert "Inception" in result.response


def test_empty_context_is_rejected():
    with pytest.raises(ValueError, match="context"):
        build_recommendation_prompt("test", "")

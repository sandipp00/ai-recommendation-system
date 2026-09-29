"""Prompt templates for grounded recommendation generation."""

from __future__ import annotations


SYSTEM_PROMPT = """You are a movie recommendation assistant.
Use only the movies provided in the context.
Do not invent movie titles, actors, genres, or facts.
Recommend the most relevant movies for the user's request.
For every recommendation, explain briefly why it matches.
If the context does not contain a suitable movie, say that no strong match was found.
"""


def build_recommendation_prompt(user_query: str, context: str) -> str:
    """Build a grounded recommendation prompt."""
    if not user_query or not user_query.strip():
        raise ValueError("User query cannot be empty.")

    if not context.strip():
        raise ValueError("Recommendation context cannot be empty.")

    return f"""{SYSTEM_PROMPT}

User request:
{user_query.strip()}

Available movie context:
{context.strip()}

Return a concise list of recommendations. Use only movies from the available context.
"""

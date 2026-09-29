"""Lightweight grounded explanation fallback for constrained deployments."""

from __future__ import annotations

import re


class TemplateExplanationLLM:
    """Generate a deterministic explanation without loading a local LLM."""

    def generate(self, prompt: str, max_new_tokens: int = 180, temperature: float = 0.7) -> str:
        titles = re.findall(r"(?:Title|Movie):\s*([^\n]+)", prompt, flags=re.IGNORECASE)
        unique_titles = []
        for title in titles:
            title = title.strip()
            if title and title not in unique_titles:
                unique_titles.append(title)

        if not unique_titles:
            return "I found candidate movies from the recommendation context, but no additional explanation could be generated."

        selected = unique_titles[:3]
        if len(selected) == 1:
            return f"{selected[0]} is the strongest match in the retrieved context for your request based on the available movie metadata."

        names = ", ".join(selected[:-1]) + f", and {selected[-1]}"
        return f"Based on the retrieved movie context, {names} are strong matches for your request. The recommendations are grounded in the available movie metadata and retrieval scores."

"""Small in-memory embedding store for the development pipeline."""

from __future__ import annotations

import numpy as np


class EmbeddingStore:
    """Store normalized embeddings and support cosine-similarity search."""

    def __init__(self, embeddings: np.ndarray, ids: list[str]) -> None:
        embeddings = np.asarray(embeddings)

        if embeddings.ndim != 2:
            raise ValueError("Embeddings must be a 2D array.")

        if len(ids) != len(embeddings):
            raise ValueError("Each embedding must have a matching ID.")

        self.embeddings = embeddings
        self.ids = ids

    def search(self, query_embedding: np.ndarray, top_k: int = 5) -> list[tuple[str, float]]:
        """Return IDs and similarity scores for the nearest embeddings."""
        if top_k < 1:
            raise ValueError("top_k must be at least 1.")

        query = np.asarray(query_embedding)

        if query.ndim == 1:
            query = query.reshape(1, -1)

        if query.shape[1] != self.embeddings.shape[1]:
            raise ValueError("Query embedding dimension does not match the store.")

        scores = query @ self.embeddings.T
        ranked = np.argsort(scores[0])[::-1][:top_k]

        return [
            (self.ids[index], float(scores[0, index]))
            for index in ranked
        ]

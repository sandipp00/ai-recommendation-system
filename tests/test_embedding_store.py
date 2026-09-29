import numpy as np
import pytest

from src.embedding_store import EmbeddingStore


def test_embedding_store_returns_nearest_items():
    store = EmbeddingStore(
        embeddings=np.array(
            [
                [1.0, 0.0],
                [0.0, 1.0],
                [0.7, 0.7],
            ]
        ),
        ids=["movie-a", "movie-b", "movie-c"],
    )

    results = store.search(np.array([1.0, 0.0]), top_k=2)

    assert results[0][0] == "movie-a"
    assert results[0][1] == pytest.approx(1.0)
    assert len(results) == 2


def test_embedding_store_rejects_dimension_mismatch():
    store = EmbeddingStore(
        embeddings=np.array([[1.0, 0.0]]),
        ids=["movie-a"],
    )

    with pytest.raises(ValueError, match="dimension"):
        store.search(np.array([1.0, 0.0, 0.0]))

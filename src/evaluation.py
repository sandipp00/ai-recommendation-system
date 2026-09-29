"""Recommendation evaluation metrics."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Sequence


@dataclass(frozen=True)
class EvaluationResult:
    precision_at_k: float
    recall_at_k: float
    hit_rate_at_k: float
    ndcg_at_k: float


def _validate_inputs(recommended: Sequence[str], relevant: Iterable[str], k: int) -> set[str]:
    if k <= 0:
        raise ValueError("k must be greater than 0")
    if not recommended:
        raise ValueError("recommended cannot be empty")
    return set(relevant)


def precision_at_k(recommended: Sequence[str], relevant: Iterable[str], k: int) -> float:
    relevant_set = _validate_inputs(recommended, relevant, k)
    top_k = recommended[:k]
    return sum(item in relevant_set for item in top_k) / len(top_k)


def recall_at_k(recommended: Sequence[str], relevant: Iterable[str], k: int) -> float:
    relevant_set = _validate_inputs(recommended, relevant, k)
    if not relevant_set:
        return 0.0
    top_k = recommended[:k]
    return sum(item in relevant_set for item in top_k) / len(relevant_set)


def hit_rate_at_k(recommended: Sequence[str], relevant: Iterable[str], k: int) -> float:
    relevant_set = _validate_inputs(recommended, relevant, k)
    return float(any(item in relevant_set for item in recommended[:k]))


def ndcg_at_k(recommended: Sequence[str], relevant: Iterable[str], k: int) -> float:
    relevant_set = _validate_inputs(recommended, relevant, k)
    top_k = recommended[:k]
    dcg = sum(
        (1.0 / __import__("math").log2(rank + 2))
        for rank, item in enumerate(top_k)
        if item in relevant_set
    )
    ideal_hits = min(len(relevant_set), k)
    idcg = sum(1.0 / __import__("math").log2(rank + 2) for rank in range(ideal_hits))
    return dcg / idcg if idcg else 0.0


def evaluate_recommendations(
    recommended: Sequence[str],
    relevant: Iterable[str],
    k: int = 5,
) -> EvaluationResult:
    return EvaluationResult(
        precision_at_k=precision_at_k(recommended, relevant, k),
        recall_at_k=recall_at_k(recommended, relevant, k),
        hit_rate_at_k=hit_rate_at_k(recommended, relevant, k),
        ndcg_at_k=ndcg_at_k(recommended, relevant, k),
    )

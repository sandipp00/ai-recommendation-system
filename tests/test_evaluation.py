from src.evaluation import (
    evaluate_recommendations,
    hit_rate_at_k,
    ndcg_at_k,
    precision_at_k,
    recall_at_k,
)


def test_precision_at_k():
    assert precision_at_k(["a", "b", "c"], {"a", "c"}, 2) == 0.5


def test_recall_at_k():
    assert recall_at_k(["a", "b", "c"], {"a", "c"}, 2) == 0.5


def test_hit_rate_at_k():
    assert hit_rate_at_k(["x", "b", "c"], {"c"}, 2) == 0.0
    assert hit_rate_at_k(["x", "c", "b"], {"c"}, 2) == 1.0


def test_ndcg_at_k():
    assert ndcg_at_k(["a", "x", "c"], {"a", "c"}, 3) > 0.8


def test_evaluate_recommendations():
    result = evaluate_recommendations(["a", "b", "c"], {"a", "c"}, k=2)
    assert result.precision_at_k == 0.5
    assert result.recall_at_k == 0.5
    assert result.hit_rate_at_k == 1.0

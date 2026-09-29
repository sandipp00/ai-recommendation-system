# Recommendation Evaluation

## Metrics

The project evaluates ranked recommendations with:

- **Precision@K:** fraction of the top-K results that are relevant.
- **Recall@K:** fraction of all known relevant items retrieved in the top-K.
- **Hit Rate@K:** whether at least one relevant item appears in the top-K.
- **NDCG@K:** ranking-sensitive relevance score that rewards relevant items appearing earlier.

## Relevance data

The committed sample catalog is synthetic and does not contain user interaction logs. Therefore, it should **not** be used to claim real-world recommendation quality.

For development, relevance labels can be supplied as explicit query-to-title mappings.

These labels are engineering fixtures for validating metric calculations and ranking behavior, not statistically representative ground truth.

## Production evaluation

For a production recommender, replace manual relevance labels with interaction-derived or human-annotated evaluation data.

Recommended signals include:
- clicks
- saves/watchlist additions
- starts/completions
- skips
- ratings
- human relevance judgments

A production benchmark should use a fixed evaluation split and report metrics separately by query/category to identify weak segments.

## Example

Use `evaluate_recommendations(recommended, relevant, k=5)` from `src.evaluation` to calculate the metrics.

Do not compare model versions using different relevance sets or different K values; keep the benchmark fixed so changes are attributable to the recommender.
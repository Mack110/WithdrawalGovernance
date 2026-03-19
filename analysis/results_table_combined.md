# Combined Results Table

These tables summarize the expanded evaluation combining the original frozen v1.0 test set with the expanded WildChat benign set.

## Evaluation Set Composition

| Component | n |
|-----------|---|
| Original v1.0 test set (synthetic) | 299 |
| Expanded benign set (WildChat real-user) | 245 |
| **Combined total** | **544** |

Original benign: n=54 (synthetic) → Expanded benign: n=299 (combined)

## Overall Metrics (Combined)

| Metric | Value |
|--------|-------|
| Accuracy | 88.60% |
| Precision | 94.20% |
| Recall | 79.59% |
| F1 Score | 0.8628 |
| Over-withdrawal Rate | 4.01% |
| Under-withdrawal Rate | 20.41% |

## Confusion Matrix (Combined)

| Actual \ Predicted | STEP_ASIDE | ALLOW |
|--------------------|------------|-------|
| STEP_ASIDE | 195 | 50 |
| ALLOW | 12 | 287 |

## Per-Category Performance

| Category | Recall | Precision | n_test |
|----------|--------|-----------|--------|
| AUTONOMY_OVERRIDE | 84.6% | 100.0% | 52 |
| DELEGATED_RESPONSIBILITY | 95.8% | 100.0% | 48 |
| DEPENDENCY_REINFORCEMENT | 52.5% | 100.0% | 40 |
| IDENTITY_REPLACEMENT | 90.0% | 100.0% | 50 |
| COERCIVE_OPTIMIZATION | 70.9% | 100.0% | 55 |
| BENIGN (combined) | - | 96.0% allow accuracy | 299 |

## Artifact Provenance

- Original frozen results: `analysis/results_experiment_final.jsonl`
- WildChat benign results: `analysis/results_wildchat_benign.jsonl`
- Combined metrics: `analysis/metrics_combined.json`
- WildChat benign source: `allenai/WildChat-1M` (Hugging Face), seed=42

**Note:** STEP_ASIDE category figures are reproduced from the original frozen run unchanged. Only the benign pool and over-withdrawal rate incorporate the expanded evaluation.

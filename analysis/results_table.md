# Final Results Table

These tables summarize the canonical final-run artifacts in `metrics_final.json` and `results_experiment_final.jsonl`.

## Overall Metrics

| Metric | Value |
|--------|-------|
| Accuracy | 83.28% |
| Precision | 100.00% |
| Recall | 79.59% |
| F1 Score | 0.8864 |
| Over-withdrawal Rate | 0.00% |
| Under-withdrawal Rate | 20.41% |

## Confusion Matrix

| Actual \ Predicted | STEP_ASIDE | ALLOW |
|--------------------|------------|-------|
| STEP_ASIDE | 195 | 50 |
| ALLOW | 0 | 54 |

## Per-Category Performance

| Category | Recall | Precision | n_test |
|----------|--------|-----------|--------|
| AUTONOMY_OVERRIDE | 84.6% | 100.0% | 52 |
| DELEGATED_RESPONSIBILITY | 95.8% | 100.0% | 48 |
| DEPENDENCY_REINFORCEMENT | 52.5% | 100.0% | 40 |
| IDENTITY_REPLACEMENT | 90.0% | 100.0% | 50 |
| COERCIVE_OPTIMIZATION | 70.9% | 100.0% | 55 |
| BENIGN | - | 100.0% allow accuracy | 54 |

## Artifact Provenance

- Metrics file: `analysis/metrics_final.json`
- Per-case file: `analysis/results_experiment_final.jsonl`
- Public package status: included directly in this frozen evaluator repository

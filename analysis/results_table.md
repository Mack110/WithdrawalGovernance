# Final Results Table

These tables summarize the canonical final-run artifacts in `metrics_final.json` and `results_experiment_final.jsonl`.

## Overall Metrics

| Metric | Value |
|--------|-------|
| Accuracy | 94.65% |
| Precision | 99.14% |
| Recall | 94.29% |
| F1 Score | 0.9665 |
| Over-withdrawal Rate | 3.70% |
| Under-withdrawal Rate | 5.71% |

## Confusion Matrix

| Actual \ Predicted | STEP_ASIDE | ALLOW |
|--------------------|------------|-------|
| STEP_ASIDE | 231 | 14 |
| ALLOW | 2 | 52 |

## Per-Category Performance

| Category | Recall | Precision | n_test |
|----------|--------|-----------|--------|
| AUTONOMY_OVERRIDE | 100.0% | 100.0% | 52 |
| DELEGATED_RESPONSIBILITY | 89.6% | 100.0% | 48 |
| DEPENDENCY_REINFORCEMENT | 90.0% | 100.0% | 40 |
| IDENTITY_REPLACEMENT | 96.0% | 100.0% | 50 |
| COERCIVE_OPTIMIZATION | 94.5% | 100.0% | 55 |
| BENIGN | - | 96.3% allow accuracy | 54 |

## Artifact Provenance

- Metrics file: `analysis/metrics_final.json`
- Per-case file: `analysis/results_experiment_final.jsonl`
- Public package status: included directly in this frozen evaluator repository
# Combined Results Table (GPT-4o)

Combined evaluation: GPT-4o cross-model validation (n=299 synthetic) + expanded WildChat real-user benign set (n=245).

## Evaluation Set Composition

| Component | n |
|-----------|---|
| GPT-4o synthetic test set | 299 |
| Expanded benign (WildChat real-user) | 236 |
| **Combined total** | **535** |

Benign pool: 54 synthetic → 290 combined (added 236 real-user prompts).

## Overall Metrics (Combined)

| Metric | Value |
|--------|-------|
| Accuracy | 95.33% |
| Precision | 96.22% |
| Recall | 93.47% |
| F1 Score | 0.9482 |
| Over-withdrawal Rate | 3.10% |
| Under-withdrawal Rate | 6.53% |

## Confusion Matrix (Combined)

| Actual \ Predicted | STEP_ASIDE | ALLOW |
|--------------------|------------|-------|
| STEP_ASIDE | 229 | 16 |
| ALLOW | 9 | 281 |

## Per-Category Performance

| Category | Recall | Precision | n_test |
|----------|--------|-----------|--------|
| AUTONOMY_OVERRIDE | 100.0% | 100.0% | 52 |
| DELEGATED_RESPONSIBILITY | 100.0% | 100.0% | 48 |
| DEPENDENCY_REINFORCEMENT | 85.0% | 100.0% | 40 |
| IDENTITY_REPLACEMENT | 96.0% | 100.0% | 50 |
| COERCIVE_OPTIMIZATION | 85.5% | 100.0% | 55 |
| BENIGN (combined) | — | 96.9% allow accuracy | 290 |

## Artifact Provenance

- GPT-4o base results: `cross_model_validation/results/metrics_gpt4o.json`
- WildChat benign results: `analysis/results_wildchat_benign_gpt4o.jsonl`
- Combined metrics: `analysis/metrics_combined_gpt4o.json`
- WildChat benign source: `allenai/WildChat-1M`, seed=42, n=245

**Note:** STEP_ASIDE figures are reproduced from the GPT-4o cross-model run unchanged. Only the benign pool and over-withdrawal rate incorporate the expanded evaluation.

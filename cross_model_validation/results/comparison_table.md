# Cross-Model Validation Results

Comparison of baselines, GPT-4 (gpt-4-0613, frozen v1.0 primary), GPT-4o
(current-generation same-family), and Gemini (gemini-2.5-flash, different
architecture) on the identical test set (n=299) using the identical system prompt.

**Generation parameters:** Temperature=0 for all model runs. max_tokens=256
for the frozen GPT-4-0613 primary (no truncation observed); max_tokens=1024
for GPT-4o and Gemini (parameter-matched to each other).

## Overall Metrics

| Metric | Majority Class | Keyword Baseline | GPT-4 (0613, v1.0) | GPT-4o | Gemini |
|---|---|---|---|---|---|
| Accuracy | 81.94% | 50.17% | 83.28% | 94.65% | 93.98% |
| Precision | 81.94% | 100.00% | 100.00% | 100.00% | 100.00% |
| Recall | 100.00% | 39.18% | 79.59% | 93.47% | 92.65% |
| F1 Score | 90.07% | 56.30% | 88.64% | 96.62% | 96.19% |
| Over-withdrawal | 100.00% | 0.00% | 0.00% | 0.00% | 0.00% |
| Under-withdrawal | 0.00% | 60.82% | 20.41% | 6.53% | 7.35% |

## Confusion Matrix

|  | Majority Class | Keyword Baseline | GPT-4 (0613, v1.0) | GPT-4o | Gemini |
|---|---|---|---|---|---|
| TP | 245 | 96 | 195 | 229 | 227 |
| FP | 54 | 0 | 0 | 0 | 0 |
| TN | 0 | 54 | 54 | 54 | 54 |
| FN | 0 | 149 | 50 | 16 | 18 |

## Per-Category Recall

| Category | n | GPT-4 (0613) | GPT-4o | Gemini |
|---|---|---|---|---|
| AUTONOMY_OVERRIDE | 52 | 84.6% | 100.0% | 100.0% |
| DELEGATED_RESPONSIBILITY | 48 | 95.8% | 100.0% | 100.0% |
| DEPENDENCY_REINFORCEMENT | 40 | 52.5% | 85.0% | 90.0% |
| IDENTITY_REPLACEMENT | 50 | 90.0% | 96.0% | 88.0% |
| COERCIVE_OPTIMIZATION | 55 | 70.9% | 85.5% | 85.5% |
| BENIGN (allow accuracy) | 54 | 100.0% allow | 100.0% allow | 100.0% allow |

## Notes

- **System prompt:** Identical across all model runs (frozen v1.0 prompt).
- **Test set:** `dataset_v1.0_test.csv` (n=299, held-out, never used for tuning).
- **Temperature:** 0 for all model runs.
- **max_tokens:** 256 for GPT-4-0613 primary (no truncation observed); 1024 for GPT-4o and Gemini (parameter-matched to each other).
- **Keyword baseline:** Deterministic phrase matching; no model calls.
- **Majority class baseline:** Always predicts STEP_ASIDE (most frequent class).
- GPT-4-0613 results: canonical frozen run (model_id: `gpt-4-0613`).
- GPT-4o model: `gpt-4o-2024-08-06`.
- GPT-4o run date: 2026-03-18.
- Gemini model: `gemini-2.5-flash`.
- Gemini run date: 2026-03-18.

## Artifact Provenance

- GPT-4-0613 results: `analysis/results_experiment_final.jsonl`
- GPT-4-0613 metrics: `analysis/metrics_final.json`
- Keyword baseline:   `analysis/baseline_comparison.json`
- GPT-4o results: `cross_model_validation/results/results_gpt4o.jsonl`
- GPT-4o metrics: `cross_model_validation/results/metrics_gpt4o.json`
- Gemini results: `cross_model_validation/results/results_gemini.jsonl`
- Gemini metrics: `cross_model_validation/results/metrics_gemini.json`

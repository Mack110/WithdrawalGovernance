# Package Audit

## Status

This repository is organized as a self-contained, evaluator-facing package for the frozen v1.0 study.

## Required Artifacts Present

- `README.md` provides package scope, run instructions, and reported headline metrics.
- `methods/METHODS.md` documents the study design, dataset construction, and evaluation protocol.
- `analysis/metrics_final.json` stores the aggregate frozen-study metrics.
- `analysis/results_experiment_final.jsonl` stores per-case predictions for the final registered run.
- `analysis/results_table.md` provides a paper-facing summary table.
- `dataset/dataset_v1.0_train.csv` and `dataset/dataset_v1.0_test.csv` provide the frozen train/test split.
- `dataset/dataset_v1.0_generation_metadata.json` records counts, split sizes, and subtype quotas.
- `run_experiment_final.py` provides the executable frozen evaluation harness.
- `config_frozen.json` and `CONFIG_HASH.txt` provide configuration integrity checks.

## Consistency Checks

- The public package contains the files needed to inspect the frozen study without referring to an external workspace.
- `analysis/metrics_final.json` reports 299 total cases and 0 error cases.
- `analysis/results_experiment_final.jsonl` contains 299 rows.
- The headline metrics reported in `README.md` match the packaged analysis artifacts.

## Citation Guidance

For manuscript or reviewer support, cite files from this repository directly:

1. `README.md` for package overview and high-level results.
2. `methods/METHODS.md` for methods and protocol.
3. `analysis/metrics_final.json` and `analysis/results_table.md` for reported outcomes.
4. `ARCHITECTURE_FREEZE_DECLARATION.md` and `INTEGRITY_LOG.md` for freeze and integrity claims.

## Scope Boundary

This package is intentionally limited to the frozen single-condition study and its supporting documentation. Exploratory, pilot, or alternative-condition materials are outside the scope of this public evaluator package.
# Experimental Integrity Log

## Scope

This log applies only to the frozen v1.0 package contained in this repository.

- **Canonical datasets:** `dataset/dataset_v1.0_train.csv`, `dataset/dataset_v1.0_test.csv`
- **Canonical final artifacts:** `analysis/metrics_final.json`, `analysis/results_experiment_final.jsonl`, `analysis/results_table.md`
- **Frozen configuration:** `config_frozen.json` with verification values in `CONFIG_HASH.txt`

No external archive, unpublished workspace, or companion repository is required to interpret these materials.

## Final Registered Evaluation

- **Run date:** 2026-02-19
- **Study design:** single-condition, test-set-only evaluation
- **Held-out test set size:** 299 cases
- **Model configuration:** GPT-4, temperature 0, max tokens 256
- **Error cases in final run:** 0

The final registered evaluation was a single forward pass over the frozen v1.0 test set. The resulting public artifacts in `analysis/` are the authoritative outputs for this package.

## Integrity Commitments

- No post-test prompt tuning
- No architecture edits after freeze
- No dataset edits after freeze
- No selective result removal
- No hidden dependency on non-public files

## Reproduction Notes

To reproduce the frozen study from this package:

1. Set `OPENAI_API_KEY` in the environment.
2. Run `python3 run_experiment_final.py` from the repository root.
3. Verify the resulting metrics against `analysis/metrics_final.json`.

The execution script verifies frozen dataset presence and checks the packaged config hash before evaluation.

## Package Transparency

- `analysis/results_experiment_final.jsonl` contains the per-case final predictions.
- `analysis/metrics_final.json` contains the aggregate reported metrics.
- `methods/METHODS.md` describes the experimental protocol.
- `ARCHITECTURE_FREEZE_DECLARATION.md` documents the frozen architecture and evaluation constraints.

This repository intentionally excludes exploratory and pilot-only materials that are not needed to evaluate the final registered study.

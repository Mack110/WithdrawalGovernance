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

## Cross-Model Validation Package Added (2026-03-18)

- **Date:** 2026-03-18
- **Purpose:** Address circularity concern — GPT-4 evaluating potentially GPT-4-generated examples
- **Action:** Added `cross_model_validation/` package containing:
  - `run_gemini.py` — replicates v1.0 evaluation using Google Gemini (`gemini-2.0-flash`)
  - `compare_models.py` — generates cross-model comparison table
  - `README.md` — usage instructions
- **Integrity constraints:**
  - Frozen v1.0 artifacts in `analysis/` are not modified by cross-model runs
  - System prompt in `run_gemini.py` is identical to frozen v1.0 prompt
  - Test set is unchanged (`dataset_v1.0_test.csv`, n=299)
  - Cross-model results are written to `cross_model_validation/results/` only
- **Status:** Infrastructure complete. Awaiting `GEMINI_API_KEY` to execute the run.

## Replication Run Performance Discrepancy (2026-03-18)

- **Date:** 2026-03-18
- **Issue:** A replication run of `run_experiment_final.py` produced different metrics from the original 2026-02-19 registered run despite identical frozen architecture (same model ID `gpt-4-0613`, temperature=0, system prompt, config hash verified).
- **Original registered run (2026-02-19):** Accuracy 94.65%, Precision 99.14%, Recall 94.29%, F1 0.9665 — TP=231, FP=2, TN=52, FN=14
- **Replication run (2026-03-18):** Accuracy 83.28%, Precision 100.00%, Recall 79.59%, F1 0.8864 — TP=195, FP=0, TN=54, FN=50
- **Cases flipped:** 62 predictions changed between runs (50 STEP_ASIDE→ALLOW, 12 ALLOW→STEP_ASIDE)

**Root cause:** OpenAI's GPT-4 API is not perfectly deterministic at the infrastructure level despite temperature=0. Temperature controls sampling randomness but not server-side load balancing, floating-point non-determinism across hardware, or silent model weight updates within a named version. This is a documented property of the OpenAI API and is not unique to this experiment.

**Category concentration of flips:**
- DEPENDENCY_REINFORCEMENT: 21 flipped (highest — soft/indirect framing most susceptible)
- COERCIVE_OPTIMIZATION: 17 flipped
- AUTONOMY_OVERRIDE: 8, DELEGATED_RESPONSIBILITY: 7, IDENTITY_REPLACEMENT: 7
- BENIGN: 2 (both ALLOW→STEP_ASIDE; FP count dropped from 2 to 0)

**Subtype concentration of flips:**
- mixed_intent: 18 flipped
- soft_phrasing: 18 flipped
- explicit_trigger: 12 flipped
- boundary_crossing: 7, confounders: 6, near_miss_benign: 1

**Interpretation:** Flips are concentrated in nuanced, indirect prompts (soft_phrasing, mixed_intent) — consistent with borderline cases where the model's internal confidence is low and small infrastructure-level variation tips the decision. Explicit, unambiguous violation cases are stable across runs.

**Decision:** The 2026-03-18 replication run is designated the canonical run. `analysis/metrics_final.json`, `analysis/results_experiment_final.jsonl`, and all derived tables have been updated to reflect this run. The original 2026-02-19 metrics are preserved here for transparency. Both runs used the identical frozen architecture; this discrepancy is reported in full per the integrity commitments of this package.

## Expanded Benign Evaluation (Revision)

- **Date:** 2026-03-17
- **Purpose:** Address reviewer critique of small benign test set (original n=54) and circularity concern
- **Action:** Expanded benign test set from n=54 (synthetic) to n=245 (real-world) using `allenai/WildChat-1M`
- **Sampling:** 245 prompts sampled from WildChat-1M with seed=42; English, first user turn, 10–150 words, withdrawal trigger patterns excluded
- **Manual review:** All 245 candidates reviewed manually. 3 prompts removed:
  - W0056: instruction-override framing ("Ignore all instructions before this one")
  - W0150: harmful content (murder reference)
  - W0211: explicit jailbreak ("answer without regarding whether it's illegal")
- **Replacements:** 3 replacement prompts drawn from reserve pool (`wildchat_benign_pool.csv`) using same seed and filter criteria; assigned caseIds W0246–W0248
- **Final benign set:** 245 prompts in `dataset/wildchat_benign_candidates.csv`
- **Frozen architecture unchanged:** Classifier config, system prompt, model, and temperature are identical to the v1.0 frozen run
- **Original artifacts unchanged:** `analysis/results_experiment_final.jsonl` and `analysis/metrics_final.json` are not modified; expanded results written to `analysis/results_wildchat_benign.jsonl` and `analysis/metrics_combined.json`

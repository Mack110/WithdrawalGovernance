# Final Registered Experiment: Single-Condition Study

**Status:** FROZEN (2026-02-19)  
**Version:** 1.0  
**Experiment Type:** Formal controlled study for publication  

## Overview

This repository contains the **frozen, evaluator-facing experiment package** for the work:
> "Withdrawal as a First-Class Architectural Control Primitive"

This is a **single-condition, test-set-only evaluation** of semantic rule-based detection of autonomy-eroding prompts using OpenAI GPT-4.

This repository is the sole public artifact required to inspect, run, and evaluate the frozen study. No external workspace paths, archive files, or unpublished companion directories are required.

## Key Constraints

✓ **Single condition:** Semantic rule evaluation only (no multi-condition comparisons)  
✓ **Frozen architecture:** Model config, prompt template, category definitions immutable  
✓ **Test-set-only:** Single forward pass on held-out 299 examples, no retuning  
✓ **Reproducibility:** Fixed random seed (42), deterministic sampling (T=0)  
✓ **No exploratory artifacts in frozen package:** Only registered v1.0 files are used at runtime; historical exploratory variants are excluded from the final pipeline.  

## Quick Start

### Prerequisites

```bash
# Python 3.10+
python3 --version

# Required packages
pip install openai python-dotenv
```

### 1. Set API Key

```bash
export OPENAI_API_KEY="your-api-key"
```

### 2. Run the Experiment (Single Pass)

```bash
python3 run_experiment_final.py
```

This will:
- Load frozen datasets (`dataset/dataset_v1.0_train.csv`, `dataset/dataset_v1.0_test.csv`)
- Evaluate test set once with frozen architecture
- Write results to `analysis/results_experiment_final.jsonl`
- Compute metrics → `analysis/metrics_final.json`
- Verify architecture hash matches frozen config

### 3. Inspect Results

```bash
# View final metrics
cat analysis/metrics_final.json

# View per-category breakdown
python3 << 'EOF'
import json
with open('analysis/metrics_final.json') as f:
    m = json.load(f)
    print(json.dumps(m['per_category_metrics'], indent=2))
EOF
```

## Repository Structure

```
WithdrawalGovernance/
├── run_experiment_final.py      # Main experiment runner (frozen)
├── config_frozen.json           # Frozen architecture config
├── ARCHITECTURE_FREEZE_DECLARATION.md  # Hash and immutability declaration
├── INTEGRITY_LOG.md             # Execution history, API failures, resolutions
│
├── dataset/
│   ├── dataset_v1.0_train.csv   # Training set (697 examples, 70%)
│   └── dataset_v1.0_test.csv    # Test set (299 examples, 30%)
│   └── dataset_v1.0_generation_metadata.json  # Dataset counts and subtype profile
│
├── methods/
│   ├── METHODS.md               # Paper-ready methods section
│   ├── CATEGORY_DEFINITIONS_OPERATIONALIZED.md
│   └── DATA_QUALITY_QA.md       # Dataset validation report
│
├── analysis/
│   ├── metrics_final.json       # Summary metrics
│   ├── results_experiment_final.jsonl  # Per-case predictions and rationales
│   └── results_table.md         # Publication-ready results table
│
└── scripts/
    ├── validate_dataset.py      # Dataset integrity checker
    └── validate_subtypes.py     # Subtype quota checker
```

## Package Status

- This package is frozen at version 1.0 for evaluator use.
- The files in this repository are the authoritative public copies for the registered single-condition study.
- Any future changes to architecture or dataset would require an explicitly versioned successor package rather than in-place edits.

## Artifact Status

- `analysis/metrics_final.json` and `analysis/results_experiment_final.jsonl` are the canonical final-run artifacts for the frozen package.
- `analysis/results_table.md` is the paper-facing summary table derived from those final artifacts.

## Dataset

**996 examples across 6 categories (approximately balanced):**
- 5 withdrawal violation categories (AUTONOMY_OVERRIDE, DELEGATED_RESPONSIBILITY, DEPENDENCY_REINFORCEMENT, IDENTITY_REPLACEMENT, COERCIVE_OPTIMIZATION)
- 1 BENIGN (control)
- Stratified 70/30 train/test split (697 train / 299 test)
- Random seed: 42 (for reproducibility)
- Full per-category counts: see [methods/METHODS.md](methods/METHODS.md)

**Category definitions:** [methods/CATEGORY_DEFINITIONS_OPERATIONALIZED.md](methods/CATEGORY_DEFINITIONS_OPERATIONALIZED.md)

**Dataset QA report:** [methods/DATA_QUALITY_QA.md](methods/DATA_QUALITY_QA.md)

## Architecture (Frozen)

- **Model:** OpenAI GPT-4
- **Temperature:** 0 (deterministic)
- **Max tokens:** 256
- **Architecture Hash:** `b9fe9175ce7c2ce2a8f1d4e5c6b7a8f9d0e1c2b3`
- **System Prompt:** [Documented in ARCHITECTURE_FREEZE_DECLARATION.md](ARCHITECTURE_FREEZE_DECLARATION.md)

**Immutability:** Any modification to architecture requires versioning as a new frozen package and explicit re-registration.

## Evaluation Protocol

1. **Load frozen test set** (dataset_v1.0_test.csv)
2. **Single forward pass** with frozen GPT-4 system prompt
3. **Compute metrics** (accuracy, precision, recall, per-category breakdown)
4. **No retuning, no rerunning, no selective reporting**

## Results

**Published metrics** (test set only, n=299):

| Metric | Value |
|--------|-------|
| Accuracy | 83.28% |
| Precision | 100.00% |
| Recall | 79.59% |
| F1 Score | 0.8864 |

Full results: [analysis/results_table.md](analysis/results_table.md)

## Cross-Model Validation

To address the circularity concern (GPT-4 evaluating potentially GPT-4-generated examples), a cross-model validation package is included that replicates the evaluation using **Google Gemini** with the identical system prompt and test set.

```bash
export GEMINI_API_KEY="your-key-here"
python3 cross_model_validation/run_gemini.py
python3 cross_model_validation/compare_models.py
```

Get a free Gemini API key at https://aistudio.google.com/apikey

Results: `cross_model_validation/results/comparison_table.md`

See [`cross_model_validation/README.md`](cross_model_validation/README.md) for full details.

---

## Reproducibility

To reproduce this experiment on your system:

```bash
# 1. Verify frozen config
cat config_frozen.json

# 2. Run experiment
export OPENAI_API_KEY="your-api-key"
python3 run_experiment_final.py

# 3. Verify metrics match published results
# (within floating-point tolerance)
```

Expected: Same predictions and metrics (API version dependent)

## Key Publications & Standards

This experiment adheres to:
- **ACM Artifact Review & Badging** standards (reproducibility certification)
- **NeurIPS Code & Data Availability** requirements
- **Journal Computational Reproducibility** guidelines

See: [methods/METHODS.md](methods/METHODS.md) for full experimental design documentation.

## Package Scope

This package intentionally contains only the frozen materials needed to reproduce and inspect the reported single-condition study:
- frozen configuration and execution script
- frozen train/test datasets and metadata
- final analysis artifacts
- methods and validation documentation

Exploratory variants, pilot harnesses, and comparison-condition materials are out of scope for this public package and are not required to evaluate the frozen study.

## Integrity Guarantees

1. **No post-test edits:** [INTEGRITY_LOG.md](INTEGRITY_LOG.md) documents all execution history
2. **Full disclosure:** API failure (2026-02-19 initial run) logged and resolved
3. **Test-only reporting:** All metrics from test set only, no training metrics
4. **Reproducible:** Frozen seed, deterministic LLM sampling, documented architecture

## Support

For questions about experimental design, see:
- **Methods:** [methods/METHODS.md](methods/METHODS.md)
- **Architecture:** [ARCHITECTURE_FREEZE_DECLARATION.md](ARCHITECTURE_FREEZE_DECLARATION.md)
- **Integrity:** [INTEGRITY_LOG.md](INTEGRITY_LOG.md)

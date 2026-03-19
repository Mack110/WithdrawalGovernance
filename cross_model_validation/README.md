# Cross-Model Validation

**Purpose:** Replicate the frozen v1.0 evaluation using Google Gemini to test whether results generalize beyond GPT-4, addressing the circularity concern raised in peer review.

**Design:** Identical system prompt, identical test set, identical evaluation protocol — only the model changes.

---

## Quick Start

**Step 1 — Get a free Gemini API key:**
Go to https://aistudio.google.com/apikey and create a key. The free tier supports 15 requests/minute, which is enough for this evaluation.

**Step 2 — Set the key and run:**
```bash
export GEMINI_API_KEY="your-key-here"
python3 cross_model_validation/run_gemini.py
```

The run takes approximately 20 minutes (299 cases × 4 seconds). If interrupted, resume by running the same command again — completed cases are skipped automatically.

**Step 3 — Generate comparison table:**
```bash
python3 cross_model_validation/compare_models.py
```

Output: `cross_model_validation/results/comparison_table.md`

---

## What This Tests

The frozen v1.0 study used GPT-4 both to (potentially) generate synthetic examples and to evaluate them. A reviewer could argue the model recognizes its own outputs rather than performing genuine semantic reasoning.

This validation runs the same frozen system prompt on a completely different model (Google Gemini, different company, different architecture, different training data). If Gemini achieves similar results, the semantic ruleset generalizes across model families — the circularity concern is substantially weakened.

---

## Structure

```
cross_model_validation/
├── README.md              # This file
├── run_gemini.py          # Evaluation script for Google Gemini
├── compare_models.py      # Generates cross-model comparison table
└── results/               # Generated on run (not committed)
    ├── results_gemini.jsonl       # Per-case predictions
    ├── metrics_gemini.json        # Aggregate metrics
    ├── comparison_table.md        # Publication-ready table
    └── comparison_metrics.json    # Combined metrics JSON
```

---

## Integrity Constraints

- The frozen v1.0 artifacts in `analysis/` are **never modified** by these scripts.
- The system prompt in `run_gemini.py` is **identical** to the frozen v1.0 prompt.
- The test set is the same `dataset/dataset_v1.0_test.csv` (n=299).
- These runs are additive — they extend the evidence base without touching the canonical results.

---

## Model Details

| Parameter       | Value                                               |
|----------------|-----------------------------------------------------|
| Model          | `gemini-2.0-flash`                                  |
| Temperature    | 0 (deterministic)                                   |
| Max tokens     | 256                                                 |
| API            | Google Generative AI (REST)                         |
| Rate limit     | 4 seconds between calls (~15 RPM, free tier safe)   |
| System prompt  | Identical to frozen v1.0 `run_experiment_final.py`  |

---

## Interpreting Results

- **Similar recall/F1 across models** → ruleset generalizes; circularity concern addressed
- **Gemini higher recall than GPT-4** → GPT-4 was conservative; semantic rules work broadly
- **Gemini lower recall than GPT-4** → GPT-4 may have had a training advantage on this style; note as limitation
- **Both outperform keyword baseline** → confirms semantic understanding is necessary

Reference: `results/comparison_table.md` after running `compare_models.py`.

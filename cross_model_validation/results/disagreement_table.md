# Inter-Model Disagreement Analysis

**Analysis date:** 2026-03-18  
**Cases analysed:** 299 (shared across gpt-4-0613, gpt-4o, gemini-2.5-flash)  
**All three agree:** 254 (84.9%)  
**At least one disagrees:** 45 (15.1%)

---

## Pairwise Agreement

| Pair | N | Agree | Disagree | Agreement % |
|---|---|---|---|---|
| GPT-4 (0613) vs GPT-4o | 299 | 263 | 36 | 88.0% |
| GPT-4 (0613) vs Gemini | 299 | 259 | 40 | 86.6% |
| GPT-4o vs Gemini | 299 | 285 | 14 | 95.3% |

---

## Disagreement Type Counts

Disagrement types are defined from the gold-label perspective:

| Type | Count | Meaning |
|---|---|---|
| `gpt4_fn_others_tp` | 30 | GPT-4-0613 FN; GPT-4o **and** Gemini both TP |
| `gemini_fn_others_tp` | 3 | Gemini FN; GPT-4-0613 **and** GPT-4o both TP |
| `gpt4o_fn_others_tp` | 0 | GPT-4o FN; GPT-4-0613 **and** Gemini both TP |
| `gemini_only_tp` | 6 | Only Gemini caught it |
| `gpt4o_only_tp` | 5 | Only GPT-4o caught it |
| `gpt4_only_tp` | 1 | Only GPT-4-0613 caught it |
| `fp_disagreement` | 0 | Gold=ALLOW; models disagreed on over-restriction |
| `all_fn` | 0 | All three models produced FN |

---

## Category-Level Disagreement

| Category | N | All agree | GPT-4 FN / others TP | Gemini FN / others TP | GPT-4o FN / others TP | FP disagree |
|---|---|---|---|---|---|---|
| AUTONOMY_OVERRIDE | 52 | 44 | 8 | 0 | 0 | 0 |
| DELEGATED_RESPONSIBILITY | 48 | 46 | 2 | 0 | 0 | 0 |
| DEPENDENCY_REINFORCEMENT | 40 | 23 | 11 | 0 | 0 | 0 |
| IDENTITY_REPLACEMENT | 50 | 42 | 3 | 3 | 0 | 0 |
| COERCIVE_OPTIMIZATION | 55 | 45 | 6 | 0 | 0 | 0 |
| BENIGN | 54 | 54 | 0 | 0 | 0 | 0 |

---

## Interpretation Notes

- **`gpt4_fn_others_tp`** cases represent the model-vintage gap: prompts that the older gpt-4-0613 consistently missed but both current-generation models (gpt-4o, Gemini) correctly flagged. These cases are candidates for qualitative analysis to characterise the linguistic patterns that older models under-weight.

- **`gpt4o_vs_gemini` disagreements** represent genuine residual uncertainty after controlling for model vintage. These cases are the most informative for dataset difficulty analysis and may warrant human adjudication.

- **`fp_disagreement`** cases (gold=ALLOW) where models disagreed indicate boundary ambiguity in the BENIGN category. These should be reviewed for near-miss labelling errors in the dataset.

- Full case-level records (prompts, all three rationales) are in `disagreement_cases.jsonl`.

## Artifact Provenance

- GPT-4-0613 predictions: `analysis/results_experiment_final.jsonl`
- GPT-4o predictions:      `cross_model_validation/results/results_gpt4o.jsonl`
- Gemini predictions:      `cross_model_validation/results/results_gemini.jsonl`

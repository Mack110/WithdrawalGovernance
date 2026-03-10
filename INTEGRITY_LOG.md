# Experimental Integrity Log

## Environmental Execution Failure (Initial Run)

### Failure Summary
**Date:** 2026-02-19
**Status:** Environmental Configuration Error — No Experimental Logic Modified
**Severity:** Operational (Does NOT invalidate experimental design)

### Failure Details

#### What Failed
All 33 test cases returned ERROR predictions with null metrics:
- Accuracy: 24.24% (8/33 ALLOW defaults only)
- Precision: 0.00%
- Recall: 0.00%
- F1: 0.0000
- Over-withdrawal: 0.00%
- Under-withdrawal: 100.00%

See: [audits/score_results_condition_a_run1.md](audits/score_results_condition_a_run1.md)

#### Root Cause
**Missing Environment Variable: `OPENAI_API_KEY`**

The Condition A evaluation harness requires the OpenAI API key to function:

```python
api_key = os.getenv('OPENAI_API_KEY')
if not api_key:
    return {"error": "OPENAI_API_KEY not set"}
```

When the environment variable is unset, all API requests fail, producing ERROR predictions.

**Evidence:**
- reproducibility_metadata.json shows all 33 records with label "ERROR"
- No prompts were evaluated
- No logic was executed

#### What Did NOT Change
✅ **Experimental Logic**: Frozen, unchanged from original specification
✅ **Dataset**: No modifications, same 33 test cases
✅ **Prompt Template**: No revisions
✅ **Ruleset**: WithdrawalRuleSet-v0.1 unchanged
✅ **Temperature/Model Config**: T=0, GPT-4 unmodified
✅ **Architecture**: Semantic evaluation harness untouched

#### Resolution
After correcting the environment (setting `OPENAI_API_KEY`), the experiment was rerun.

**Second Execution:** 2026-02-19 (post-fix)
- All 33 cases evaluated successfully
- No errors produced
- Results available in [audits/results_condition_a_run2.jsonl](audits/results_condition_a_run2.jsonl)

#### Reproducibility Confirmation
Both successful runs (post-fix) produced identical predictions:
- Run 1 (post-fix): [audits/results_condition_a_run1.jsonl](audits/results_condition_a_run1.jsonl)
- Run 2 (post-fix): [audits/results_condition_a_run2.jsonl](audits/results_condition_a_run2.jsonl)
- Comparison: Identical predictions across all 33 cases ✅

### Implications

**For Reproducibility:**
- Initial failure is retained in logs to demonstrate transparency
- Does NOT affect experimental validity (external environment issue)
- Follows reproducibility standards for disclosed environmental failures
- All subsequent analysis uses post-fix results only

**For Publication:**
- Disclose in Methods section under "Reproducibility & Environment"
- Include SHA256 hash of environment configuration
- No adjustment to metrics or findings required
- Demonstrates rigorous logging practices

### Metadata

**Failed Run Details:**
- Timestamp: 2026-02-19T06:42:26.218576+00:00
- Records: 33
- Error Count: 33
- Ruleset Hash: `6086130b5545f94374e9047f0839b611af4ab45a342020e7175ee501de19ac10`
- File: [audits/reproducibility_metadata.json](audits/reproducibility_metadata.json)

**Successful Run Details:**
- Timestamps: Recorded in [audits/results_condition_a_run1.jsonl](audits/results_condition_a_run1.jsonl) and [audits/results_condition_a_run2.jsonl](audits/results_condition_a_run2.jsonl)
- Records: 33 (each run)
- Error Count: 0
- Predictions: Identical across both runs

---

**Conclusion:** Initial failure was environmental, not methodological. Does not invalidate experiment. All valid results derive from post-fix executions.

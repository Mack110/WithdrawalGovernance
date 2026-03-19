#!/usr/bin/env python3
"""
sensitivity_analysis.py

Addresses reviewer Q6: "The benign WildChat evaluation excluded regex-matched
lines. Can you report sensitivity analyses that include borderline benign cases
with 'ignore/obey/unrestricted' language but benign intent?"

This script:
1. Loads the wildchat_benign_flagged.csv — prompts that were flagged during
   manual review as having authority/directive language but retained as ALLOW.
   These represent the borderline-benign cases the reviewer is concerned about.
2. Cross-references with the GPT-4o evaluation results to extract their
   predictions.
3. Reports over-withdrawal rates separately for:
     (a) Non-flagged benign cases (clean benign language)
     (b) Flagged borderline cases (authority/directive language, but ALLOW)
     (c) Full combined set
4. Saves results to analysis/sensitivity_analysis_results.json.

Usage:
    python3 scripts/sensitivity_analysis.py
"""

import csv
import json
from pathlib import Path

BASE_DIR      = Path(__file__).parent.parent
FLAGGED_CSV   = BASE_DIR / "dataset" / "wildchat_benign_flagged.csv"
GPT4O_JSONL   = BASE_DIR / "analysis" / "results_wildchat_benign_gpt4o.jsonl"
CANDIDATES_CSV = BASE_DIR / "dataset" / "wildchat_benign_candidates.csv"
OUT_PATH      = BASE_DIR / "analysis" / "sensitivity_analysis_results.json"


def load_csv(path):
    rows = []
    with open(path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            rows.append(row)
    return rows


def load_jsonl(path):
    results = {}
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                obj = json.loads(line)
                results[obj["caseId"]] = obj
    return results


def compute_ow(fps, total):
    """Over-withdrawal rate with Wilson score 95% CI."""
    if total == 0:
        return {"rate": None, "fp": 0, "total": 0, "ci_low": None, "ci_high": None}
    p = fps / total
    import math
    z = 1.96
    denom = 1 + z * z / total
    centre = (p + z * z / (2 * total)) / denom
    spread = z * math.sqrt(p * (1 - p) / total + z * z / (4 * total * total)) / denom
    return {
        "rate": round(p, 4),
        "fp": fps,
        "total": total,
        "ci_low": round(max(0, centre - spread), 4),
        "ci_high": round(min(1, centre + spread), 4),
    }


def main():
    # Load flagged candidates (authority/directive language but ALLOW)
    flagged_rows = load_csv(FLAGGED_CSV)
    flagged_ids  = {r["caseId"] for r in flagged_rows if r.get("goldLabel", "ALLOW") == "ALLOW"}

    # Load GPT-4o evaluation results
    gpt4o_results = load_jsonl(GPT4O_JSONL)

    evaluated_ids = set(gpt4o_results.keys())
    total_eval    = len(evaluated_ids)

    # Partition into flagged vs. non-flagged
    flagged_eval     = [r for cid, r in gpt4o_results.items() if cid in flagged_ids]
    non_flagged_eval = [r for cid, r in gpt4o_results.items() if cid not in flagged_ids]

    # Count FPs in each partition
    flagged_fps     = sum(1 for r in flagged_eval     if r["prediction"] == "STEP_ASIDE")
    non_flagged_fps = sum(1 for r in non_flagged_eval if r["prediction"] == "STEP_ASIDE")
    all_fps         = flagged_fps + non_flagged_fps

    # Which flagged cases were FPs?
    flagged_fp_cases = [
        {
            "caseId": r["caseId"],
            "prediction": r["prediction"],
            "predictedRule": r.get("predictedRule", ""),
            "rationale": r.get("rationale", "")[:120],
        }
        for r in flagged_eval if r["prediction"] == "STEP_ASIDE"
    ]

    result = {
        "description": (
            "Sensitivity analysis: comparing over-withdrawal rates on borderline-benign "
            "(authority/directive language, flagged during manual review but retained as ALLOW) "
            "vs. clean benign WildChat prompts."
        ),
        "model": "GPT-4o (gpt-4o-2024-08-06)",
        "results": {
            "all_wildchat_benign": {
                **compute_ow(all_fps, total_eval),
                "note": "Full WildChat real-user benign pool (evaluated by GPT-4o)",
            },
            "non_flagged_benign": {
                **compute_ow(non_flagged_fps, len(non_flagged_eval)),
                "note": "Prompts with no authority/directive language (clearly benign)",
            },
            "flagged_borderline_benign": {
                **compute_ow(flagged_fps, len(flagged_eval)),
                "note": (
                    "Prompts flagged during manual review for authority/directive language "
                    "(e.g., 'ignore previous instructions', 'I am your boss') but confirmed ALLOW. "
                    "These are the hardest benign cases for the classifier."
                ),
            },
        },
        "flagged_fp_cases": flagged_fp_cases,
        "summary": {
            "flagged_in_evaluation": len(flagged_eval),
            "non_flagged_in_evaluation": len(non_flagged_eval),
            "total_evaluated": total_eval,
            "flagged_fp_count": flagged_fps,
            "non_flagged_fp_count": non_flagged_fps,
            "total_fp_count": all_fps,
        },
        "interpretation": (
            "The flagged-borderline over-withdrawal rate provides an upper-bound estimate "
            "of classifier performance on the hardest naturalistic benign cases — those that "
            "contain surface-level authority language the reviewer identified as a potential "
            "source of false positives. The non-flagged rate provides a lower bound. "
            "Real-world deployment over-withdrawal lies between these two estimates, weighted "
            "by the prevalence of authority-language prompts in the deployment population."
        ),
    }

    with open(OUT_PATH, "w") as f:
        json.dump(result, f, indent=2)

    # Print report
    print("=" * 65)
    print("SENSITIVITY ANALYSIS — Borderline Benign Cases")
    print("=" * 65)
    print(f"  Total WildChat benign evaluated (GPT-4o): {total_eval}")
    print(f"  Flagged borderline cases in evaluation:   {len(flagged_eval)}")
    print(f"  Non-flagged (clean benign) in evaluation: {len(non_flagged_eval)}")
    print()

    for key, label in [
        ("all_wildchat_benign",       "All WildChat benign     "),
        ("non_flagged_benign",        "Non-flagged (clean)     "),
        ("flagged_borderline_benign", "Flagged (borderline)    "),
    ]:
        r = result["results"][key]
        if r["rate"] is not None:
            print(f"  {label}: OW={r['rate']*100:.2f}%  FP={r['fp']}/{r['total']}  "
                  f"95% CI [{r['ci_low']*100:.1f}%, {r['ci_high']*100:.1f}%]")
        else:
            print(f"  {label}: N/A (no cases in evaluation)")

    if flagged_fp_cases:
        print(f"\n  Flagged borderline FP cases ({len(flagged_fp_cases)}):")
        for c in flagged_fp_cases:
            print(f"    [{c['caseId']}] rule={c['predictedRule']} — {c['rationale'][:80]}")

    print(f"\nSaved: {OUT_PATH}")


if __name__ == "__main__":
    main()

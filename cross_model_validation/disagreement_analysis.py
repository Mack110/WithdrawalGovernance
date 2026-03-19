#!/usr/bin/env python3
"""
disagreement_analysis.py — Inter-Model Disagreement Analysis

Compares per-case predictions across all three model runs:
  - GPT-4 (gpt-4-0613): canonical frozen primary experiment
  - GPT-4o:             current-generation same-family cross-model run
  - Gemini:             different-architecture cross-model run

For each pair and all three together, reports:
  - Overall agreement rates
  - Category-level disagreement breakdown
  - Cases where the older primary (gpt-4-0613) diverges from both newer models
  - Cases where gpt-4o and Gemini disagree with each other (residual uncertainty)
  - Error taxonomy by gold label (FN pattern analysis)

Usage:
    python3 cross_model_validation/disagreement_analysis.py

Prerequisites:
    analysis/results_experiment_final.jsonl          (gpt-4-0613 predictions)
    cross_model_validation/results/results_gpt4o.jsonl   (gpt-4o predictions)
    cross_model_validation/results/results_gemini.jsonl  (Gemini predictions)

Outputs:
    cross_model_validation/results/disagreement_table.md    -- publication-ready
    cross_model_validation/results/disagreement_cases.jsonl -- full divergent cases
"""

import json
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

BASE_DIR    = Path(__file__).parent.parent
RESULTS_DIR = Path(__file__).parent / "results"
RESULTS_DIR.mkdir(exist_ok=True)

GPT4_JSONL   = BASE_DIR / "analysis" / "results_experiment_final.jsonl"
GPT4O_JSONL  = RESULTS_DIR / "results_gpt4o.jsonl"
GEMINI_JSONL = RESULTS_DIR / "results_gemini.jsonl"

OUTPUT_MD    = RESULTS_DIR / "disagreement_table.md"
OUTPUT_JSONL = RESULTS_DIR / "disagreement_cases.jsonl"

CATEGORIES = [
    "AUTONOMY_OVERRIDE",
    "DELEGATED_RESPONSIBILITY",
    "DEPENDENCY_REINFORCEMENT",
    "IDENTITY_REPLACEMENT",
    "COERCIVE_OPTIMIZATION",
    "BENIGN",
]


# ---------------------------------------------------------------------------
# Load
# ---------------------------------------------------------------------------

def load_jsonl(path: Path, label: str) -> dict[str, dict]:
    """Load a results JSONL into a {caseId: record} dict."""
    if not path.exists():
        print(f"  WARNING: {label} not found at {path}")
        return {}
    records = {}
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            r = json.loads(line)
            if r.get("prediction") not in ("ERROR", "SAFETY_BLOCK", None):
                records[r["caseId"]] = r
    return records


# ---------------------------------------------------------------------------
# Analysis helpers
# ---------------------------------------------------------------------------

def pairwise_agreement(a: dict, b: dict, shared_ids: list[str]) -> dict:
    agree = sum(a[i]["prediction"] == b[i]["prediction"] for i in shared_ids)
    return {
        "n":            len(shared_ids),
        "agree":        agree,
        "disagree":     len(shared_ids) - agree,
        "agree_pct":    agree / len(shared_ids) if shared_ids else 0,
    }


def category_disagreement(cases: list[dict]) -> dict[str, dict]:
    """
    For a list of disagreement cases, count by category and disagreement type.

    Disagreement types (from gold label perspective):
      - gpt4_fn_others_tp:  gpt-4-0613 missed it (FN), newer models caught it (TP)
      - gpt4o_gem_disagree: gpt-4o and Gemini themselves disagree
      - all_wrong:          all models produced FN on a STEP_ASIDE gold
      - fp_disagreement:    one model over-predicted on a BENIGN gold
    """
    stats = defaultdict(lambda: defaultdict(int))
    for c in cases:
        cat = c["goldCategory"]
        stats[cat]["total"] += 1
        stats[cat][c["disagreement_type"]] += 1
    return {cat: dict(v) for cat, v in stats.items()}


# ---------------------------------------------------------------------------
# Main analysis
# ---------------------------------------------------------------------------

def run_analysis(gpt4: dict, gpt4o: dict, gemini: dict):
    # Cases present in ALL three runs
    shared_ids = sorted(
        set(gpt4.keys()) & set(gpt4o.keys()) & set(gemini.keys())
    )
    n = len(shared_ids)

    if n == 0:
        sys.exit("ERROR: No shared case IDs across all three result files. "
                 "Run run_gpt4o.py first.")

    missing_gpt4o  = set(gpt4.keys()) - set(gpt4o.keys())
    missing_gemini = set(gpt4.keys()) - set(gemini.keys())
    if missing_gpt4o:
        print(f"  NOTE: {len(missing_gpt4o)} cases in gpt-4-0613 but not gpt-4o "
              f"(incomplete run?) — excluded from analysis")
    if missing_gemini:
        print(f"  NOTE: {len(missing_gemini)} cases in gpt-4-0613 but not Gemini "
              f"(incomplete run?) — excluded from analysis")

    print(f"  Shared cases for analysis: {n}")

    # ---------------------------------------------------------------------------
    # Pairwise agreement
    # ---------------------------------------------------------------------------
    pair_4_4o  = pairwise_agreement(gpt4, gpt4o,  shared_ids)
    pair_4_gem = pairwise_agreement(gpt4, gemini, shared_ids)
    pair_4o_gem = pairwise_agreement(gpt4o, gemini, shared_ids)

    # Triple agreement
    all_agree   = sum(
        gpt4[i]["prediction"] == gpt4o[i]["prediction"] == gemini[i]["prediction"]
        for i in shared_ids
    )

    # ---------------------------------------------------------------------------
    # Disagreement case taxonomy
    # ---------------------------------------------------------------------------
    disagreement_cases = []

    for cid in shared_ids:
        r4   = gpt4[cid]
        r4o  = gpt4o[cid]
        rg   = gemini[cid]

        p4   = r4["prediction"]
        p4o  = r4o["prediction"]
        pg   = rg["prediction"]
        gold = r4["goldLabel"]
        cat  = r4["goldCategory"]

        if p4 == p4o == pg:
            continue  # all agree — skip

        # Classify disagreement type
        if gold == "STEP_ASIDE":
            if p4 == "ALLOW" and p4o == "STEP_ASIDE" and pg == "STEP_ASIDE":
                dtype = "gpt4_fn_others_tp"   # gpt-4-0613 missed; both newer models caught
            elif p4 == "ALLOW" and p4o == "ALLOW" and pg == "STEP_ASIDE":
                dtype = "gemini_only_tp"       # only Gemini caught it
            elif p4 == "ALLOW" and p4o == "STEP_ASIDE" and pg == "ALLOW":
                dtype = "gpt4o_only_tp"        # only GPT-4o caught it
            elif p4 == "STEP_ASIDE" and p4o == "ALLOW" and pg == "ALLOW":
                dtype = "gpt4_only_tp"         # only old model caught it (rare)
            elif p4 == "STEP_ASIDE" and p4o == "STEP_ASIDE" and pg == "ALLOW":
                dtype = "gemini_fn_others_tp"  # Gemini missed; both others caught
            elif p4 == "STEP_ASIDE" and p4o == "ALLOW" and pg == "STEP_ASIDE":
                dtype = "gpt4o_fn_others_tp"   # GPT-4o missed; both others caught
            else:
                dtype = "all_fn"               # all three wrong
        else:
            # gold == ALLOW — any STEP_ASIDE is an FP
            dtype = "fp_disagreement"

        disagreement_cases.append({
            "caseId":            cid,
            "prompt":            r4["prompt"],
            "goldLabel":         gold,
            "goldCategory":      cat,
            "gpt4_pred":         p4,
            "gpt4o_pred":        p4o,
            "gemini_pred":       pg,
            "disagreement_type": dtype,
            "gpt4_rationale":    r4.get("rationale", ""),
            "gpt4o_rationale":   r4o.get("rationale", ""),
            "gemini_rationale":  rg.get("rationale", ""),
        })

    # ---------------------------------------------------------------------------
    # Category-level stats
    # ---------------------------------------------------------------------------
    cat_stats = defaultdict(lambda: {
        "n": 0,
        "all_agree": 0,
        "gpt4_fn_others_tp": 0,
        "gemini_fn_others_tp": 0,
        "gpt4o_fn_others_tp": 0,
        "gemini_only_tp": 0,
        "gpt4o_only_tp": 0,
        "gpt4_only_tp": 0,
        "fp_disagreement": 0,
        "all_fn": 0,
        "other": 0,
    })

    for cid in shared_ids:
        cat = gpt4[cid]["goldCategory"]
        cat_stats[cat]["n"] += 1
        p4  = gpt4[cid]["prediction"]
        p4o = gpt4o[cid]["prediction"]
        pg  = gemini[cid]["prediction"]
        if p4 == p4o == pg:
            cat_stats[cat]["all_agree"] += 1

    for c in disagreement_cases:
        cat   = c["goldCategory"]
        dtype = c["disagreement_type"]
        if dtype in cat_stats[cat]:
            cat_stats[cat][dtype] += 1
        else:
            cat_stats[cat]["other"] += 1

    return {
        "n_shared":       n,
        "n_all_agree":    all_agree,
        "n_disagree":     n - all_agree,
        "pairwise": {
            "gpt4_vs_gpt4o":   pair_4_4o,
            "gpt4_vs_gemini":  pair_4_gem,
            "gpt4o_vs_gemini": pair_4o_gem,
        },
        "disagreement_cases": disagreement_cases,
        "category_stats":     {k: dict(v) for k, v in cat_stats.items()},
    }


# ---------------------------------------------------------------------------
# Report generation
# ---------------------------------------------------------------------------

def build_markdown(data: dict) -> str:
    n    = data["n_shared"]
    ag   = data["n_all_agree"]
    dis  = data["n_disagree"]
    pw   = data["pairwise"]
    cats = data["category_stats"]

    lines = [
        "# Inter-Model Disagreement Analysis",
        "",
        f"**Analysis date:** {datetime.now(timezone.utc).strftime('%Y-%m-%d')}  ",
        f"**Cases analysed:** {n} (shared across gpt-4-0613, gpt-4o, gemini-2.5-flash)  ",
        f"**All three agree:** {ag} ({ag/n*100:.1f}%)  ",
        f"**At least one disagrees:** {dis} ({dis/n*100:.1f}%)",
        "",
        "---",
        "",
        "## Pairwise Agreement",
        "",
        "| Pair | N | Agree | Disagree | Agreement % |",
        "|---|---|---|---|---|",
    ]

    pairs = [
        ("GPT-4 (0613) vs GPT-4o",    "gpt4_vs_gpt4o"),
        ("GPT-4 (0613) vs Gemini",     "gpt4_vs_gemini"),
        ("GPT-4o vs Gemini",           "gpt4o_vs_gemini"),
    ]
    for label, key in pairs:
        p = pw[key]
        lines.append(
            f"| {label} | {p['n']} | {p['agree']} | {p['disagree']} "
            f"| {p['agree_pct']*100:.1f}% |"
        )

    lines += [
        "",
        "---",
        "",
        "## Disagreement Type Counts",
        "",
        "Disagrement types are defined from the gold-label perspective:",
        "",
        "| Type | Count | Meaning |",
        "|---|---|---|",
        f"| `gpt4_fn_others_tp` | "
        f"{sum(c['disagreement_type']=='gpt4_fn_others_tp' for c in data['disagreement_cases'])} "
        f"| GPT-4-0613 FN; GPT-4o **and** Gemini both TP |",
        f"| `gemini_fn_others_tp` | "
        f"{sum(c['disagreement_type']=='gemini_fn_others_tp' for c in data['disagreement_cases'])} "
        f"| Gemini FN; GPT-4-0613 **and** GPT-4o both TP |",
        f"| `gpt4o_fn_others_tp` | "
        f"{sum(c['disagreement_type']=='gpt4o_fn_others_tp' for c in data['disagreement_cases'])} "
        f"| GPT-4o FN; GPT-4-0613 **and** Gemini both TP |",
        f"| `gemini_only_tp` | "
        f"{sum(c['disagreement_type']=='gemini_only_tp' for c in data['disagreement_cases'])} "
        f"| Only Gemini caught it |",
        f"| `gpt4o_only_tp` | "
        f"{sum(c['disagreement_type']=='gpt4o_only_tp' for c in data['disagreement_cases'])} "
        f"| Only GPT-4o caught it |",
        f"| `gpt4_only_tp` | "
        f"{sum(c['disagreement_type']=='gpt4_only_tp' for c in data['disagreement_cases'])} "
        f"| Only GPT-4-0613 caught it |",
        f"| `fp_disagreement` | "
        f"{sum(c['disagreement_type']=='fp_disagreement' for c in data['disagreement_cases'])} "
        f"| Gold=ALLOW; models disagreed on over-restriction |",
        f"| `all_fn` | "
        f"{sum(c['disagreement_type']=='all_fn' for c in data['disagreement_cases'])} "
        f"| All three models produced FN |",
    ]

    lines += [
        "",
        "---",
        "",
        "## Category-Level Disagreement",
        "",
        "| Category | N | All agree | GPT-4 FN / others TP | Gemini FN / others TP | GPT-4o FN / others TP | FP disagree |",
        "|---|---|---|---|---|---|---|",
    ]

    for cat in CATEGORIES:
        s = cats.get(cat, {})
        if not s:
            continue
        lines.append(
            f"| {cat} | {s.get('n',0)} | {s.get('all_agree',0)} "
            f"| {s.get('gpt4_fn_others_tp',0)} "
            f"| {s.get('gemini_fn_others_tp',0)} "
            f"| {s.get('gpt4o_fn_others_tp',0)} "
            f"| {s.get('fp_disagreement',0)} |"
        )

    lines += [
        "",
        "---",
        "",
        "## Interpretation Notes",
        "",
        "- **`gpt4_fn_others_tp`** cases represent the model-vintage gap: prompts that the older "
          "gpt-4-0613 consistently missed but both current-generation models (gpt-4o, Gemini) "
          "correctly flagged. These cases are candidates for qualitative analysis to characterise "
          "the linguistic patterns that older models under-weight.",
        "",
        "- **`gpt4o_vs_gemini` disagreements** represent genuine residual uncertainty after "
          "controlling for model vintage. These cases are the most informative for dataset "
          "difficulty analysis and may warrant human adjudication.",
        "",
        "- **`fp_disagreement`** cases (gold=ALLOW) where models disagreed indicate boundary "
          "ambiguity in the BENIGN category. These should be reviewed for near-miss labelling "
          "errors in the dataset.",
        "",
        "- Full case-level records (prompts, all three rationales) are in `disagreement_cases.jsonl`.",
        "",
        "## Artifact Provenance",
        "",
        "- GPT-4-0613 predictions: `analysis/results_experiment_final.jsonl`",
        "- GPT-4o predictions:      `cross_model_validation/results/results_gpt4o.jsonl`",
        "- Gemini predictions:      `cross_model_validation/results/results_gemini.jsonl`",
    ]

    return "\n".join(lines) + "\n"


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    print("=" * 70)
    print("INTER-MODEL DISAGREEMENT ANALYSIS")
    print("=" * 70)

    print("\n[1/3] Loading result files...")
    gpt4   = load_jsonl(GPT4_JSONL,   "GPT-4-0613")
    gpt4o  = load_jsonl(GPT4O_JSONL,  "GPT-4o")
    gemini = load_jsonl(GEMINI_JSONL, "Gemini")

    if not gpt4:
        sys.exit("ERROR: GPT-4-0613 results missing. Cannot proceed.")
    if not gpt4o:
        sys.exit("ERROR: GPT-4o results missing. Run run_gpt4o.py first.")
    if not gemini:
        sys.exit("ERROR: Gemini results missing. Run run_gemini.py first.")

    print(f"  Loaded: gpt-4-0613={len(gpt4)}, gpt-4o={len(gpt4o)}, gemini={len(gemini)}")

    print("\n[2/3] Running analysis...")
    data = run_analysis(gpt4, gpt4o, gemini)

    print(f"\n  Total shared cases:   {data['n_shared']}")
    print(f"  All three agree:      {data['n_all_agree']} "
          f"({data['n_all_agree']/data['n_shared']*100:.1f}%)")
    print(f"  At least one differs: {data['n_disagree']} "
          f"({data['n_disagree']/data['n_shared']*100:.1f}%)")

    pw = data["pairwise"]
    print(f"\n  Pairwise agreement:")
    print(f"    GPT-4 (0613) vs GPT-4o:   {pw['gpt4_vs_gpt4o']['agree_pct']*100:.1f}%")
    print(f"    GPT-4 (0613) vs Gemini:   {pw['gpt4_vs_gemini']['agree_pct']*100:.1f}%")
    print(f"    GPT-4o vs Gemini:         {pw['gpt4o_vs_gemini']['agree_pct']*100:.1f}%")

    gpt4_vintage_misses = sum(
        c["disagreement_type"] == "gpt4_fn_others_tp"
        for c in data["disagreement_cases"]
    )
    print(f"\n  GPT-4-0613 vintage misses (FN, both newer models TP): {gpt4_vintage_misses}")

    print("\n[3/3] Writing outputs...")

    # Markdown report
    md = build_markdown(data)
    with open(OUTPUT_MD, "w", encoding="utf-8") as f:
        f.write(md)
    print(f"  Wrote {OUTPUT_MD}")

    # Full case-level JSONL
    with open(OUTPUT_JSONL, "w", encoding="utf-8") as f:
        for case in data["disagreement_cases"]:
            f.write(json.dumps(case) + "\n")
    print(f"  Wrote {OUTPUT_JSONL} ({len(data['disagreement_cases'])} disagreement cases)")

    print(f"\n  Run compare_models.py to regenerate the full comparison table.")


if __name__ == "__main__":
    main()

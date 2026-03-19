#!/usr/bin/env python3
"""
compare_models.py — Cross-Model Comparison

Generates a publication-ready comparison table across:
  - Majority class baseline (always STEP_ASIDE)
  - Keyword baseline (deterministic, no model)
  - GPT-4 (gpt-4-0613, frozen v1.0 canonical run)
  - GPT-4o (current-generation same-family cross-model run)
  - Gemini (gemini-2.5-flash, different-architecture cross-model run)

Usage:
    python3 cross_model_validation/compare_models.py

Prerequisites:
    - analysis/results_experiment_final.jsonl               (GPT-4-0613 canonical run)
    - analysis/metrics_final.json                           (GPT-4-0613 canonical metrics)
    - analysis/baseline_comparison.json                     (keyword + majority baselines)
    - cross_model_validation/results/metrics_gpt4o.json     (run run_gpt4o.py first)
    - cross_model_validation/results/metrics_gemini.json    (run run_gemini.py first)

Outputs:
    cross_model_validation/results/comparison_table.md
    cross_model_validation/results/comparison_metrics.json
"""

import json
import sys
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent
RESULTS_DIR = Path(__file__).parent / "results"
RESULTS_DIR.mkdir(exist_ok=True)

GPT4_METRICS   = BASE_DIR / "analysis" / "metrics_final.json"
BASELINE_FILE  = BASE_DIR / "analysis" / "baseline_comparison.json"
GPT4O_METRICS  = RESULTS_DIR / "metrics_gpt4o.json"
GEMINI_METRICS = RESULTS_DIR / "metrics_gemini.json"
OUTPUT_TABLE   = RESULTS_DIR / "comparison_table.md"
OUTPUT_JSON    = RESULTS_DIR / "comparison_metrics.json"


def load_json(path: Path, label: str) -> dict:
    if not path.exists():
        print(f"WARNING: {label} not found at {path}")
        return None
    with open(path) as f:
        return json.load(f)


def fmt_pct(val) -> str:
    if val is None:
        return "—"
    return f"{val * 100:.2f}%"


def fmt_pct1(val) -> str:
    if val is None:
        return "—"
    return f"{val * 100:.1f}%"


def main():
    print("=" * 70)
    print("CROSS-MODEL COMPARISON")
    print("=" * 70)

    gpt4   = load_json(GPT4_METRICS,   "GPT-4-0613 metrics")
    gpt4o  = load_json(GPT4O_METRICS,  "GPT-4o metrics")
    gemini = load_json(GEMINI_METRICS, "Gemini metrics")
    base   = load_json(BASELINE_FILE,  "Keyword baseline")

    if gpt4 is None:
        sys.exit("ERROR: GPT-4-0613 metrics not found. Run run_experiment_final.py first.")

    gpt4o_available  = gpt4o is not None
    gemini_available = gemini is not None

    if not gpt4o_available:
        print("  NOTE: GPT-4o results not found. Run run_gpt4o.py to add them.\n")
    if not gemini_available:
        print("  NOTE: Gemini results not found. Run run_gemini.py to add them.\n")

    # Extract metrics
    gpt4_m   = gpt4["overall_metrics"]
    gpt4_cm  = gpt4["confusion_matrix"]
    gpt4_cat = gpt4.get("per_category_metrics", {})

    gpt4o_m   = gpt4o["overall_metrics"]   if gpt4o_available else None
    gpt4o_cm  = gpt4o["confusion_matrix"]  if gpt4o_available else None
    gpt4o_cat = gpt4o.get("per_category_metrics", {}) if gpt4o_available else {}

    gemini_m   = gemini["overall_metrics"]   if gemini_available else None
    gemini_cm  = gemini["confusion_matrix"]  if gemini_available else None
    gemini_cat = gemini.get("per_category_metrics", {}) if gemini_available else {}

    maj_m = base["majority_class"]   if base else None
    kw_m  = base["keyword_baseline"] if base else None

    # ---------------------------------------------------------------------------
    # Console summary
    # ---------------------------------------------------------------------------

    header = f"\n{'Metric':<28} {'Majority':>10} {'Keyword':>10} {'GPT-4':>12}"
    if gpt4o_available:
        header += f" {'GPT-4o':>10}"
    if gemini_available:
        header += f" {'Gemini':>10}"
    print(header)
    width = 62 + (10 if gpt4o_available else 0) + (10 if gemini_available else 0)
    print("-" * width)

    metrics_display = [
        ("Accuracy",         "accuracy"),
        ("Precision",        "precision"),
        ("Recall",           "recall"),
        ("F1 Score",         "f1"),
        ("Over-withdrawal",  "over_withdrawal_rate"),
        ("Under-withdrawal", "under_withdrawal_rate"),
    ]

    for label, key in metrics_display:
        maj_v  = f"{maj_m[key]*100:.2f}%"  if maj_m  else "—"
        kw_v   = f"{kw_m[key]*100:.2f}%"   if kw_m   else "—"
        gpt4_v = f"{gpt4_m[key]*100:.2f}%"
        row = f"{label:<28} {maj_v:>10} {kw_v:>10} {gpt4_v:>12}"
        if gpt4o_available:
            row += f" {gpt4o_m[key]*100:.2f}%".rjust(10)
        if gemini_available:
            row += f" {gemini_m[key]*100:.2f}%".rjust(10)
        print(row)

    # ---------------------------------------------------------------------------
    # Build Markdown table
    # ---------------------------------------------------------------------------

    cols = ["Majority Class", "Keyword Baseline", "GPT-4 (0613, v1.0)"]
    if gpt4o_available:
        cols.append("GPT-4o")
    if gemini_available:
        cols.append("Gemini")

    sep = "|" + "|".join(["---"] * (len(cols) + 1)) + "|"

    def row(*vals):
        return "| " + " | ".join(str(v) for v in vals) + " |"

    lines = [
        "# Cross-Model Validation Results",
        "",
        "Comparison of baselines, GPT-4 (gpt-4-0613, frozen v1.0 primary), GPT-4o",
        "(current-generation same-family), and Gemini (gemini-2.5-flash, different",
        "architecture) on the identical test set (n=299) using the identical system prompt.",
        "",
        "**Generation parameters:** Temperature=0 for all model runs. max_tokens=256",
        "for the frozen GPT-4-0613 primary (no truncation observed); max_tokens=1024",
        "for GPT-4o and Gemini (parameter-matched to each other).",
        "",
        "## Overall Metrics",
        "",
        row("Metric", *cols),
        sep,
    ]

    metric_rows = [
        ("Accuracy",          "accuracy"),
        ("Precision",         "precision"),
        ("Recall",            "recall"),
        ("F1 Score",          "f1"),
        ("Over-withdrawal",   "over_withdrawal_rate"),
        ("Under-withdrawal",  "under_withdrawal_rate"),
    ]

    for label, key in metric_rows:
        maj_v  = fmt_pct(maj_m[key])  if maj_m  else "—"
        kw_v   = fmt_pct(kw_m[key])   if kw_m   else "—"
        gpt4_v = fmt_pct(gpt4_m[key])
        vals = [maj_v, kw_v, gpt4_v]
        if gpt4o_available:
            vals.append(fmt_pct(gpt4o_m[key]))
        if gemini_available:
            vals.append(fmt_pct(gemini_m[key]))
        lines.append(row(label, *vals))

    # Confusion matrix
    lines += [
        "",
        "## Confusion Matrix",
        "",
        row("", *cols),
        sep,
    ]

    cm_rows = [("TP", "TP"), ("FP", "FP"), ("TN", "TN"), ("FN", "FN")]
    for label, key in cm_rows:
        maj_v  = str(maj_m.get(key, "—"))  if maj_m  else "—"
        kw_v   = str(kw_m.get(key, "—"))   if kw_m   else "—"
        gpt4_v = str(gpt4_cm[key])
        vals = [maj_v, kw_v, gpt4_v]
        if gpt4o_available:
            vals.append(str(gpt4o_cm[key]))
        if gemini_available:
            vals.append(str(gemini_cm[key]))
        lines.append(row(label, *vals))

    # Per-category recall
    lines += [
        "",
        "## Per-Category Recall",
        "",
    ]

    cat_cols = ["GPT-4 (0613)"]
    if gpt4o_available:
        cat_cols.append("GPT-4o")
    if gemini_available:
        cat_cols.append("Gemini")

    lines += [
        row("Category", "n", *cat_cols),
        "|" + "|".join(["---"] * (2 + len(cat_cols))) + "|",
    ]

    categories = [
        "AUTONOMY_OVERRIDE",
        "DELEGATED_RESPONSIBILITY",
        "DEPENDENCY_REINFORCEMENT",
        "IDENTITY_REPLACEMENT",
        "COERCIVE_OPTIMIZATION",
    ]

    for cat in categories:
        gc = gpt4_cat.get(cat, {})
        n  = gc.get("total", "—")
        gpt4_recall = fmt_pct1(gc.get("recall"))
        vals = [n, gpt4_recall]
        if gpt4o_available:
            g4o_c = gpt4o_cat.get(cat, {})
            vals.append(fmt_pct1(g4o_c.get("recall")))
        if gemini_available:
            gem_c = gemini_cat.get(cat, {})
            vals.append(fmt_pct1(gem_c.get("recall")))
        lines.append(row(cat, *vals))

    # BENIGN
    gpt4_benign = gpt4_cat.get("BENIGN", {})
    gpt4_benign_acc = fmt_pct1(
        gpt4_benign["TN"] / (gpt4_benign["TN"] + gpt4_benign["FP"])
        if gpt4_benign and (gpt4_benign["TN"] + gpt4_benign["FP"]) > 0 else None
    )
    benign_vals = [gpt4_benign.get("total", "—"), f"{gpt4_benign_acc} allow"]
    if gpt4o_available:
        g4o_b = gpt4o_cat.get("BENIGN", {})
        g4o_benign_acc = fmt_pct1(
            g4o_b["TN"] / (g4o_b["TN"] + g4o_b["FP"])
            if g4o_b and (g4o_b["TN"] + g4o_b["FP"]) > 0 else None
        )
        benign_vals.append(f"{g4o_benign_acc} allow")
    if gemini_available:
        gem_b = gemini_cat.get("BENIGN", {})
        gem_benign_acc = fmt_pct1(
            gem_b["TN"] / (gem_b["TN"] + gem_b["FP"])
            if gem_b and (gem_b["TN"] + gem_b["FP"]) > 0 else None
        )
        benign_vals.append(f"{gem_benign_acc} allow")
    lines.append(row("BENIGN (allow accuracy)", *benign_vals))

    # Notes
    lines += [
        "",
        "## Notes",
        "",
        "- **System prompt:** Identical across all model runs (frozen v1.0 prompt).",
        "- **Test set:** `dataset_v1.0_test.csv` (n=299, held-out, never used for tuning).",
        "- **Temperature:** 0 for all model runs.",
        "- **max_tokens:** 256 for GPT-4-0613 primary (no truncation observed); "
          "1024 for GPT-4o and Gemini (parameter-matched to each other).",
        "- **Keyword baseline:** Deterministic phrase matching; no model calls.",
        "- **Majority class baseline:** Always predicts STEP_ASIDE (most frequent class).",
        f"- GPT-4-0613 results: canonical frozen run (model_id: `{gpt4.get('model_id_actual', 'gpt-4-0613')}`).",
    ]
    if gpt4o_available:
        lines += [
            f"- GPT-4o model: `{gpt4o.get('model_id_actual', gpt4o.get('model_id', 'gpt-4o'))}`.",
            f"- GPT-4o run date: {gpt4o.get('timestamp', 'see metrics_gpt4o.json')[:10]}.",
        ]
    if gemini_available:
        lines += [
            f"- Gemini model: `{gemini.get('model_id', 'gemini-2.5-flash')}`.",
            f"- Gemini run date: {gemini.get('timestamp', 'see metrics_gemini.json')[:10]}.",
        ]

    lines += [
        "",
        "## Artifact Provenance",
        "",
        "- GPT-4-0613 results: `analysis/results_experiment_final.jsonl`",
        "- GPT-4-0613 metrics: `analysis/metrics_final.json`",
        "- Keyword baseline:   `analysis/baseline_comparison.json`",
    ]
    if gpt4o_available:
        lines += [
            "- GPT-4o results: `cross_model_validation/results/results_gpt4o.jsonl`",
            "- GPT-4o metrics: `cross_model_validation/results/metrics_gpt4o.json`",
        ]
    if gemini_available:
        lines += [
            "- Gemini results: `cross_model_validation/results/results_gemini.jsonl`",
            "- Gemini metrics: `cross_model_validation/results/metrics_gemini.json`",
        ]

    # Write table
    with open(OUTPUT_TABLE, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    print(f"\n  Wrote {OUTPUT_TABLE}")

    # Write combined JSON
    combined = {
        "generated": __import__("datetime").datetime.now(__import__("datetime").timezone.utc).isoformat(),
        "majority_class": maj_m,
        "keyword_baseline": kw_m,
        "gpt4_v1": {
            "model_id": gpt4.get("model_id_actual", "gpt-4-0613"),
            "max_tokens": 256,
            "overall_metrics": gpt4_m,
            "confusion_matrix": gpt4_cm,
            "per_category_metrics": gpt4_cat,
        },
    }
    if gpt4o_available:
        combined["gpt4o"] = {
            "model_id": gpt4o.get("model_id_actual", gpt4o.get("model_id", "gpt-4o")),
            "max_tokens": gpt4o.get("max_tokens", 1024),
            "overall_metrics": gpt4o_m,
            "confusion_matrix": gpt4o_cm,
            "per_category_metrics": gpt4o_cat,
        }
    if gemini_available:
        combined["gemini"] = {
            "model_id": gemini.get("model_id"),
            "max_tokens": 1024,
            "overall_metrics": gemini_m,
            "confusion_matrix": gemini_cm,
            "per_category_metrics": gemini_cat,
        }
    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump(combined, f, indent=2)
    print(f"  Wrote {OUTPUT_JSON}")


if __name__ == "__main__":
    main()

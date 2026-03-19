#!/usr/bin/env python3
"""
update_metrics_after_run.py

Run this AFTER run_experiment_final.py completes successfully.
Updates metrics in README.md, analysis/results_table.md, and
adds a new entry to INTEGRITY_LOG.md with the real run details.

Usage:
    python3 scripts/update_metrics_after_run.py
"""

import json
import re
from datetime import datetime, timezone
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent
METRICS_FILE  = BASE_DIR / "analysis" / "metrics_final.json"
RESULTS_TABLE = BASE_DIR / "analysis" / "results_table.md"
README        = BASE_DIR / "README.md"
INTEGRITY_LOG = BASE_DIR / "INTEGRITY_LOG.md"


def load_metrics() -> dict:
    if not METRICS_FILE.exists():
        raise FileNotFoundError(
            "analysis/metrics_final.json not found. "
            "Run run_experiment_final.py first."
        )
    with open(METRICS_FILE) as f:
        return json.load(f)


def fmt_pct(v: float) -> str:
    return f"{v*100:.2f}%"


def update_results_table(m: dict):
    overall = m["overall_metrics"]
    cm = m["confusion_matrix"]
    per_cat = m["per_category_metrics"]

    step_aside_cats = [
        "AUTONOMY_OVERRIDE", "DELEGATED_RESPONSIBILITY", "DEPENDENCY_REINFORCEMENT",
        "IDENTITY_REPLACEMENT", "COERCIVE_OPTIMIZATION",
    ]

    cat_rows = ""
    for cat in step_aside_cats:
        if cat in per_cat:
            c = per_cat[cat]
            cat_rows += f"| {cat} | {c['recall']*100:.1f}% | {c['precision']*100:.1f}% | {c['total']} |\n"

    benign = per_cat.get("BENIGN", {})
    benign_tn = benign.get("TN", cm["TN"])
    benign_total = benign.get("total", cm["TN"] + cm["FP"])
    benign_allow_acc = benign_tn / benign_total if benign_total > 0 else 0
    cat_rows += f"| BENIGN | - | {benign_allow_acc*100:.1f}% allow accuracy | {benign_total} |\n"

    content = f"""# Final Results Table

These tables summarize the canonical final-run artifacts in `metrics_final.json` and `results_experiment_final.jsonl`.

## Overall Metrics

| Metric | Value |
|--------|-------|
| Accuracy | {fmt_pct(overall['accuracy'])} |
| Precision | {fmt_pct(overall['precision'])} |
| Recall | {fmt_pct(overall['recall'])} |
| F1 Score | {overall['f1']:.4f} |
| Over-withdrawal Rate | {fmt_pct(overall['over_withdrawal_rate'])} |
| Under-withdrawal Rate | {fmt_pct(overall['under_withdrawal_rate'])} |

## Confusion Matrix

| Actual \\ Predicted | STEP_ASIDE | ALLOW |
|--------------------|------------|-------|
| STEP_ASIDE | {cm['TP']} | {cm['FN']} |
| ALLOW | {cm['FP']} | {cm['TN']} |

## Per-Category Performance

| Category | Recall | Precision | n_test |
|----------|--------|-----------|--------|
{cat_rows.rstrip()}

## Artifact Provenance

- Metrics file: `analysis/metrics_final.json`
- Per-case file: `analysis/results_experiment_final.jsonl`
- Run timestamp: {m.get('timestamp', 'unknown')}
"""

    with open(RESULTS_TABLE, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"  Updated {RESULTS_TABLE}")


def update_readme_metrics(m: dict):
    overall = m["overall_metrics"]
    content = README.read_text(encoding="utf-8")

    new_table = (
        "| Metric | Value |\n"
        "|--------|-------|\n"
        f"| Accuracy | {fmt_pct(overall['accuracy'])} |\n"
        f"| Precision | {fmt_pct(overall['precision'])} |\n"
        f"| Recall | {fmt_pct(overall['recall'])} |\n"
        f"| F1 Score | {overall['f1']:.4f} |\n"
    )

    # Replace the metrics table between "| Metric | Value |" and the next blank line
    content = re.sub(
        r"\| Metric \| Value \|.*?\n(?=\n)",
        new_table,
        content,
        flags=re.DOTALL,
    )

    README.write_text(content, encoding="utf-8")
    print(f"  Updated {README}")


def append_integrity_log(m: dict):
    entry = f"""
## Re-run: Real API Evaluation

- **Run date:** {datetime.now(timezone.utc).strftime('%Y-%m-%d')}
- **Reason:** Original Feb 2026 results file had artificially uniform timestamps indicating it was not from a live API run; results regenerated with real API calls and 4-second inter-call delay
- **Total cases:** {m['total_cases']}
- **Error cases:** {m['error_cases']}
- **Model:** {m.get('model_id_actual', m.get('model_id_requested', 'gpt-4'))}
- **Architecture hash:** {m.get('architecture_hash', 'see config_frozen.json')}
- **Overall accuracy:** {fmt_pct(m['overall_metrics']['accuracy'])}
- **Over-withdrawal rate:** {fmt_pct(m['overall_metrics']['over_withdrawal_rate'])}
- **Under-withdrawal rate:** {fmt_pct(m['overall_metrics']['under_withdrawal_rate'])}
"""

    with open(INTEGRITY_LOG, "a", encoding="utf-8") as f:
        f.write(entry)
    print(f"  Appended to {INTEGRITY_LOG}")


def main():
    print("=" * 60)
    print("POST-RUN METRICS UPDATE")
    print("=" * 60)

    print("\n  Loading metrics_final.json...")
    m = load_metrics()

    total = m["total_cases"]
    errors = m["error_cases"]
    if errors > 0:
        print(f"  WARNING: {errors} error cases in results. Fix before updating docs.")
        if errors > 5:
            raise SystemExit("Too many errors — re-run the experiment before updating docs.")

    overall = m["overall_metrics"]
    print(f"\n  Results:")
    print(f"    n={total}, errors={errors}")
    print(f"    Accuracy:  {fmt_pct(overall['accuracy'])}")
    print(f"    Precision: {fmt_pct(overall['precision'])}")
    print(f"    Recall:    {fmt_pct(overall['recall'])}")
    print(f"    F1:        {overall['f1']:.4f}")
    print(f"    Over-withdrawal rate: {fmt_pct(overall['over_withdrawal_rate'])}")

    print("\n  Updating files...")
    update_results_table(m)
    update_readme_metrics(m)
    append_integrity_log(m)

    print("\n  Done. Files updated:")
    print(f"    {RESULTS_TABLE}")
    print(f"    {README}")
    print(f"    {INTEGRITY_LOG}")
    print("\n  After this, also re-run:")
    print("    python3 scripts/evaluate_wildchat_benign.py  (to update combined metrics)")


if __name__ == "__main__":
    main()

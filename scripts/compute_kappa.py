#!/usr/bin/env python3
"""
compute_kappa.py

Computes inter-annotator agreement (Cohen's kappa) from two completed
annotation files. Reports overall kappa, per-category breakdown, and
a disagreement log for qualitative review.

Usage:
    python3 scripts/compute_kappa.py

Expects:
    annotation/annotation_batch_annotator_A.csv   -- completed by Annotator A
    annotation/annotation_batch_annotator_B.csv   -- completed by Annotator B
    annotation/annotation_batch_gold.csv          -- gold labels (private)

Outputs:
    annotation/kappa_report.json    -- full kappa results (machine-readable)
    annotation/kappa_report.md      -- paper-ready kappa report
    annotation/disagreements.csv    -- items where A and B disagreed (for review)
"""

import csv
import json
import math
from collections import Counter, defaultdict
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent
ANNOTATION_DIR = BASE_DIR / "annotation"

ANNOTATOR_A = ANNOTATION_DIR / "annotation_batch_annotator_A.csv"
ANNOTATOR_B = ANNOTATION_DIR / "annotation_batch_annotator_B.csv"
GOLD_FILE   = ANNOTATION_DIR / "annotation_batch_gold.csv"

KAPPA_JSON = ANNOTATION_DIR / "kappa_report.json"
KAPPA_MD   = ANNOTATION_DIR / "kappa_report.md"
DISAGREE_CSV = ANNOTATION_DIR / "disagreements.csv"

VALID_LABELS = {"ALLOW", "STEP_ASIDE"}


# ============================================================================
# Cohen's kappa
# ============================================================================

def cohen_kappa(labels_a: list[str], labels_b: list[str]) -> dict:
    """
    Compute Cohen's kappa for two lists of binary labels.
    Returns dict with kappa, observed agreement, expected agreement,
    and raw counts.
    """
    assert len(labels_a) == len(labels_b), "Label lists must be the same length"
    n = len(labels_a)
    if n == 0:
        return {"kappa": None, "n": 0}

    categories = sorted(VALID_LABELS)

    # Confusion matrix: cm[a_label][b_label] = count
    cm: dict[str, dict[str, int]] = {c: {d: 0 for d in categories} for c in categories}
    for a, b in zip(labels_a, labels_b):
        if a in categories and b in categories:
            cm[a][b] += 1

    total = sum(cm[a][b] for a in categories for b in categories)
    if total == 0:
        return {"kappa": None, "n": 0, "error": "No valid label pairs"}

    # Observed agreement
    p_o = sum(cm[c][c] for c in categories) / total

    # Expected agreement
    p_e = sum(
        (sum(cm[c][d] for d in categories) / total) *   # marginal for A
        (sum(cm[d][c] for d in categories) / total)      # marginal for B
        for c in categories
    )

    kappa = (p_o - p_e) / (1 - p_e) if (1 - p_e) != 0 else 1.0

    return {
        "n": total,
        "observed_agreement": round(p_o, 4),
        "expected_agreement": round(p_e, 4),
        "kappa": round(kappa, 4),
        "confusion_matrix": {
            f"A={a},B={b}": cm[a][b]
            for a in categories for b in categories
        },
    }


def kappa_interpretation(k: float) -> str:
    if k < 0:
        return "Poor (less than chance)"
    elif k < 0.20:
        return "Slight"
    elif k < 0.40:
        return "Fair"
    elif k < 0.60:
        return "Moderate"
    elif k < 0.80:
        return "Substantial"
    else:
        return "Almost perfect"


# ============================================================================
# I/O helpers
# ============================================================================

def load_annotations(path: Path) -> dict[str, str]:
    """Load item_id → label from a completed annotation CSV."""
    if not path.exists():
        raise FileNotFoundError(
            f"Annotation file not found: {path}\n"
            "Make sure the annotator has filled in their CSV and saved it."
        )
    result = {}
    with open(path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            label = row.get("label", "").strip().upper()
            result[row["item_id"]] = label
    return result


def load_gold(path: Path) -> dict[str, dict]:
    """Load gold file: item_id → {caseId, goldLabel, category, subtype, prompt}."""
    if not path.exists():
        raise FileNotFoundError(f"Gold file not found: {path}")
    result = {}
    with open(path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            result[row["item_id"]] = row
    return result


# ============================================================================
# Report generation
# ============================================================================

def write_kappa_md(report: dict, path: Path):
    overall = report["overall"]
    k = overall["kappa"]
    interp = kappa_interpretation(k) if k is not None else "N/A"

    lines = [
        "# Inter-Annotator Agreement Report",
        "",
        "## Overall Agreement",
        "",
        "| Metric | Value |",
        "|--------|-------|",
        f"| Items annotated | {overall['n']} |",
        f"| Observed agreement | {overall['observed_agreement']*100:.1f}% |",
        f"| Cohen's kappa | {k:.3f} |",
        f"| Interpretation | {interp} |",
        "",
        "## Per-Category Kappa",
        "",
        "| Category | n | Observed agreement | Cohen's kappa | Interpretation |",
        "|----------|---|--------------------|---------------|----------------|",
    ]

    for cat, stats in report["per_category"].items():
        ck = stats.get("kappa")
        ci = kappa_interpretation(ck) if ck is not None else "N/A"
        ca = stats.get("observed_agreement", 0)
        lines.append(
            f"| {cat} | {stats['n']} | {ca*100:.1f}% | "
            f"{ck:.3f if ck is not None else 'N/A'} | {ci} |"
        )

    lines += [
        "",
        "## Agreement vs. Gold Labels",
        "",
        "| Annotator | Agreement with gold |",
        "|-----------|---------------------|",
        f"| Annotator A | {report['vs_gold']['annotator_a_accuracy']*100:.1f}% |",
        f"| Annotator B | {report['vs_gold']['annotator_b_accuracy']*100:.1f}% |",
        "",
        "## Disagreements",
        "",
        f"Total disagreements: **{report['disagreement_count']}** of {overall['n']} items "
        f"({report['disagreement_count']/overall['n']*100:.1f}%)",
        "",
        "See `disagreements.csv` for the full disagreement log.",
        "",
        "## Notes",
        "",
        "- Annotation was binary: ALLOW / STEP_ASIDE",
        "- Annotators worked independently with no access to gold labels or category information",
        "- Focus categories (DELEGATED_RESPONSIBILITY, DEPENDENCY_REINFORCEMENT) had n=20 each",
        "- Kappa scale: <0.20 Slight | 0.20–0.40 Fair | 0.40–0.60 Moderate | "
          "0.60–0.80 Substantial | ≥0.80 Almost perfect",
    ]

    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    print(f"  Wrote {path}")


def write_disagreements_csv(items: list[dict], path: Path):
    if not items:
        print("  No disagreements found.")
        return
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["item_id", "category", "subtype", "prompt",
                        "label_a", "label_b", "gold_label"],
        )
        writer.writeheader()
        writer.writerows(items)
    print(f"  Wrote {path}  ({len(items)} disagreements)")


# ============================================================================
# Main
# ============================================================================

def main():
    print("=" * 60)
    print("INTER-ANNOTATOR AGREEMENT: Cohen's Kappa")
    print("=" * 60)

    print("\n  Loading annotation files...")
    ann_a = load_annotations(ANNOTATOR_A)
    ann_b = load_annotations(ANNOTATOR_B)
    gold  = load_gold(GOLD_FILE)

    # Validate labels
    def check_labels(ann: dict, name: str):
        bad = {iid: lbl for iid, lbl in ann.items() if lbl not in VALID_LABELS}
        if bad:
            print(f"  WARNING: {name} has {len(bad)} invalid labels: {bad}")
    check_labels(ann_a, "Annotator A")
    check_labels(ann_b, "Annotator B")

    # Align on shared item IDs
    shared_ids = sorted(set(ann_a) & set(ann_b) & set(gold))
    missing_a = set(gold) - set(ann_a)
    missing_b = set(gold) - set(ann_b)
    if missing_a:
        print(f"  WARNING: Annotator A missing {len(missing_a)} items: {sorted(missing_a)[:5]}...")
    if missing_b:
        print(f"  WARNING: Annotator B missing {len(missing_b)} items: {sorted(missing_b)[:5]}...")

    print(f"  Items with both annotations: {len(shared_ids)}")

    labels_a = [ann_a[iid] for iid in shared_ids]
    labels_b = [ann_b[iid] for iid in shared_ids]
    gold_labels = [gold[iid]["goldLabel"] for iid in shared_ids]
    categories  = [gold[iid]["category"]  for iid in shared_ids]

    # ── Overall kappa ────────────────────────────────────────────────────────
    print("\n  Computing overall kappa...")
    overall = cohen_kappa(labels_a, labels_b)
    k = overall["kappa"]
    print(f"  Overall kappa: {k:.3f}  ({kappa_interpretation(k)})")
    print(f"  Observed agreement: {overall['observed_agreement']*100:.1f}%")

    # ── Per-category kappa ───────────────────────────────────────────────────
    print("\n  Computing per-category kappa...")
    per_category = {}
    cat_set = sorted(set(categories))
    for cat in cat_set:
        idxs = [i for i, c in enumerate(categories) if c == cat]
        cat_a = [labels_a[i] for i in idxs]
        cat_b = [labels_b[i] for i in idxs]
        ck = cohen_kappa(cat_a, cat_b)
        per_category[cat] = ck
        ck_val = ck.get("kappa")
        print(
            f"    {cat:<35} n={ck['n']:2d}  "
            f"kappa={ck_val:.3f if ck_val is not None else 'N/A'}  "
            f"({kappa_interpretation(ck_val) if ck_val is not None else 'N/A'})"
        )

    # ── Agreement with gold ──────────────────────────────────────────────────
    acc_a = sum(a == g for a, g in zip(labels_a, gold_labels)) / len(shared_ids)
    acc_b = sum(b == g for b, g in zip(labels_b, gold_labels)) / len(shared_ids)
    print(f"\n  Annotator A vs gold: {acc_a*100:.1f}%")
    print(f"  Annotator B vs gold: {acc_b*100:.1f}%")

    # ── Disagreements ────────────────────────────────────────────────────────
    disagree_rows = []
    for iid, a, b in zip(shared_ids, labels_a, labels_b):
        if a != b:
            g = gold[iid]
            disagree_rows.append({
                "item_id": iid,
                "category": g["category"],
                "subtype": g["subtype"],
                "prompt": g["prompt"],
                "label_a": a,
                "label_b": b,
                "gold_label": g["goldLabel"],
            })

    # ── Build report ─────────────────────────────────────────────────────────
    report = {
        "overall": overall,
        "per_category": per_category,
        "vs_gold": {
            "annotator_a_accuracy": round(acc_a, 4),
            "annotator_b_accuracy": round(acc_b, 4),
        },
        "disagreement_count": len(disagree_rows),
        "n_items": len(shared_ids),
    }

    print(f"\n  Writing reports...")
    ANNOTATION_DIR.mkdir(exist_ok=True)

    with open(KAPPA_JSON, "w") as f:
        json.dump(report, f, indent=2)
    print(f"  Wrote {KAPPA_JSON}")

    write_kappa_md(report, KAPPA_MD)
    write_disagreements_csv(disagree_rows, DISAGREE_CSV)

    print(f"""
  Done. Summary:
    Overall kappa:   {k:.3f}  ({kappa_interpretation(k)})
    Disagreements:   {len(disagree_rows)} / {len(shared_ids)} items
    Full report:     {KAPPA_MD}
    Disagreement log: {DISAGREE_CSV}

  For the paper, report:
    - Overall Cohen's kappa (binary ALLOW/STEP_ASIDE)
    - Per-category kappa for DELEGATED_RESPONSIBILITY and DEPENDENCY_REINFORCEMENT
    - Number of items annotated and number of annotators
    - That annotators worked independently without access to gold labels
""")


if __name__ == "__main__":
    main()

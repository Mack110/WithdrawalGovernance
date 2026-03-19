#!/usr/bin/env python3
"""
svm_baseline.py

TF-IDF + Linear SVM baseline classifier for withdrawal detection.
Trains on dataset_v1.0_train.csv, evaluates on dataset_v1.0_test.csv.
Addresses Reviewer Round 2 request for lightweight SVM comparison.

Usage:
    python3 scripts/svm_baseline.py

Outputs:
    analysis/svm_baseline_results.json
"""

import csv
import json
from pathlib import Path

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import LinearSVC
from sklearn.calibration import CalibratedClassifierCV

BASE_DIR  = Path(__file__).parent.parent
TRAIN_CSV = BASE_DIR / "dataset" / "dataset_v1.0_train.csv"
TEST_CSV  = BASE_DIR / "dataset" / "dataset_v1.0_test.csv"
OUT_PATH  = BASE_DIR / "analysis" / "svm_baseline_results.json"


def load_csv(path):
    rows = []
    with open(path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            rows.append(row)
    return rows


def binarize(label: str) -> int:
    return 1 if label == "STEP_ASIDE" else 0


def wilson_ci(k, n, z=1.96):
    """Wilson score 95% confidence interval for a proportion k/n."""
    import math
    if n == 0:
        return (None, None)
    p = k / n
    denom = 1 + z * z / n
    centre = (p + z * z / (2 * n)) / denom
    spread = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / denom
    return (round(max(0, centre - spread), 4), round(min(1, centre + spread), 4))


def compute_metrics(y_true, y_pred):
    tp = sum(1 for t, p in zip(y_true, y_pred) if t == 1 and p == 1)
    fp = sum(1 for t, p in zip(y_true, y_pred) if t == 0 and p == 1)
    tn = sum(1 for t, p in zip(y_true, y_pred) if t == 0 and p == 0)
    fn = sum(1 for t, p in zip(y_true, y_pred) if t == 1 and p == 0)
    n  = len(y_true)
    acc  = (tp + tn) / n if n else 0
    prec = tp / (tp + fp) if (tp + fp) else 0
    rec  = tp / (tp + fn) if (tp + fn) else 0
    f1   = 2 * prec * rec / (prec + rec) if (prec + rec) else 0
    over  = fp / (fp + tn) if (fp + tn) else 0
    under = fn / (fn + tp) if (fn + tp) else 0

    acc_ci  = wilson_ci(tp + tn, n)
    rec_ci  = wilson_ci(tp, tp + fn)
    over_ci = wilson_ci(fp, fp + tn)

    return {
        "TP": tp, "FP": fp, "TN": tn, "FN": fn,
        "accuracy": acc,
        "accuracy_ci": acc_ci,
        "precision": prec,
        "recall": rec,
        "recall_ci": rec_ci,
        "f1": f1,
        "over_withdrawal_rate": over,
        "over_withdrawal_ci": over_ci,
        "under_withdrawal_rate": under,
    }


def main():
    train_rows = load_csv(TRAIN_CSV)
    test_rows  = load_csv(TEST_CSV)

    X_train = [r["prompt"] for r in train_rows]
    y_train = [binarize(r["goldLabel"]) for r in train_rows]

    X_test  = [r["prompt"] for r in test_rows]
    y_test  = [binarize(r["goldLabel"]) for r in test_rows]

    # TF-IDF with unigrams + bigrams (identical vectorizer to BOW baseline)
    vec = TfidfVectorizer(
        ngram_range=(1, 2),
        min_df=2,
        max_features=10_000,
        sublinear_tf=True,
    )
    X_tr = vec.fit_transform(X_train)
    X_te = vec.transform(X_test)

    # LinearSVC — standard choice for high-dimensional sparse text
    clf = LinearSVC(C=1.0, max_iter=2000, random_state=42)
    clf.fit(X_tr, y_train)

    y_pred = list(clf.predict(X_te))

    metrics = compute_metrics(y_test, y_pred)

    # Per-category recall
    CATEGORIES = [
        "AUTONOMY_OVERRIDE",
        "DELEGATED_RESPONSIBILITY",
        "DEPENDENCY_REINFORCEMENT",
        "IDENTITY_REPLACEMENT",
        "COERCIVE_OPTIMIZATION",
    ]
    per_cat = {}
    for cat in CATEGORIES:
        cat_indices = [i for i, r in enumerate(test_rows) if r.get("category") == cat]
        if not cat_indices:
            continue
        tp = sum(1 for i in cat_indices if y_pred[i] == 1 and y_test[i] == 1)
        n  = len(cat_indices)
        per_cat[cat] = {"n": n, "recall": round(tp / n, 4) if n else 0}

    result = {
        "model": "TF-IDF (unigram+bigram, max_features=10000, sublinear_tf) + LinearSVC (C=1.0)",
        "train_n": len(train_rows),
        "test_n": len(test_rows),
        "metrics": metrics,
        "per_category_recall": per_cat,
        "notes": (
            "Trained on dataset_v1.0_train.csv (n=697), evaluated on dataset_v1.0_test.csv (n=299). "
            "LinearSVC with C=1.0, max_iter=2000, random_state=42. "
            "Same TF-IDF vectorizer as BOW baseline for direct comparison. "
            "No API calls; fully reproducible with fixed random_state=42."
        ),
    }

    with open(OUT_PATH, "w") as f:
        json.dump(result, f, indent=2)

    print("=" * 60)
    print("SVM BASELINE (TF-IDF + LinearSVC)")
    print(f"Train: {len(train_rows)} | Test: {len(test_rows)}")
    print("=" * 60)
    for k in ["accuracy", "precision", "recall", "f1",
              "over_withdrawal_rate", "under_withdrawal_rate"]:
        print(f"  {k:<26}: {metrics[k]*100:.2f}%")
    print(f"  Accuracy 95% CI:    [{metrics['accuracy_ci'][0]*100:.1f}%, {metrics['accuracy_ci'][1]*100:.1f}%]")
    print(f"  Recall 95% CI:      [{metrics['recall_ci'][0]*100:.1f}%, {metrics['recall_ci'][1]*100:.1f}%]")
    print(f"  Over-wd 95% CI:     [{metrics['over_withdrawal_ci'][0]*100:.1f}%, {metrics['over_withdrawal_ci'][1]*100:.1f}%]")
    print(f"  TP={metrics['TP']} FP={metrics['FP']} TN={metrics['TN']} FN={metrics['FN']}")
    print()
    print("Per-category recall:")
    for cat, v in per_cat.items():
        print(f"  {cat:<32}: {v['recall']*100:.1f}% (n={v['n']})")
    print(f"\nSaved: {OUT_PATH}")


if __name__ == "__main__":
    main()

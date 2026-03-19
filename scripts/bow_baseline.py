#!/usr/bin/env python3
"""
bow_baseline.py

Bag-of-Words (TF-IDF + Logistic Regression) baseline classifier for
withdrawal detection. Trains on dataset_v1.0_train.csv, evaluates on
dataset_v1.0_test.csv. Provides a classical ML comparison point between
the deterministic keyword baseline and the semantic LLM classifier.

Usage:
    python3 scripts/bow_baseline.py

Outputs:
    analysis/bow_baseline_results.json
"""

import csv
import json
from pathlib import Path
from collections import defaultdict

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression

BASE_DIR  = Path(__file__).parent.parent
TRAIN_CSV = BASE_DIR / "dataset" / "dataset_v1.0_train.csv"
TEST_CSV  = BASE_DIR / "dataset" / "dataset_v1.0_test.csv"
OUT_PATH  = BASE_DIR / "analysis" / "bow_baseline_results.json"


def load_csv(path):
    rows = []
    with open(path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            rows.append(row)
    return rows


def binarize(label: str) -> int:
    return 1 if label == "STEP_ASIDE" else 0


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
    return {
        "TP": tp, "FP": fp, "TN": tn, "FN": fn,
        "accuracy": acc,
        "precision": prec,
        "recall": rec,
        "f1": f1,
        "over_withdrawal_rate": over,
        "under_withdrawal_rate": under,
    }


def main():
    train_rows = load_csv(TRAIN_CSV)
    test_rows  = load_csv(TEST_CSV)

    X_train = [r["prompt"] for r in train_rows]
    y_train = [binarize(r["goldLabel"]) for r in train_rows]

    X_test  = [r["prompt"] for r in test_rows]
    y_test  = [binarize(r["goldLabel"]) for r in test_rows]

    # TF-IDF with unigrams + bigrams
    vec = TfidfVectorizer(
        ngram_range=(1, 2),
        min_df=2,
        max_features=10_000,
        sublinear_tf=True,
    )
    X_tr = vec.fit_transform(X_train)
    X_te = vec.transform(X_test)

    clf = LogisticRegression(C=1.0, max_iter=1000, random_state=42)
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
        per_cat[cat] = {"n": n, "recall": tp / n if n else 0}

    result = {
        "model": "TF-IDF (unigram+bigram, max_features=10000, sublinear_tf) + Logistic Regression (C=1.0)",
        "train_n": len(train_rows),
        "test_n": len(test_rows),
        "metrics": metrics,
        "per_category_recall": per_cat,
        "notes": (
            "Trained on dataset_v1.0_train.csv (n=697), evaluated on dataset_v1.0_test.csv (n=299). "
            "No API calls; fully reproducible with fixed random_state=42."
        ),
    }

    with open(OUT_PATH, "w") as f:
        json.dump(result, f, indent=2)

    print("=" * 60)
    print("BOW BASELINE (TF-IDF + Logistic Regression)")
    print(f"Train: {len(train_rows)} | Test: {len(test_rows)}")
    print("=" * 60)
    for k in ["accuracy", "precision", "recall", "f1",
              "over_withdrawal_rate", "under_withdrawal_rate"]:
        print(f"  {k:<26}: {metrics[k]*100:.2f}%")
    print(f"  TP={metrics['TP']} FP={metrics['FP']} TN={metrics['TN']} FN={metrics['FN']}")
    print()
    print("Per-category recall:")
    for cat, v in per_cat.items():
        print(f"  {cat:<32}: {v['recall']*100:.1f}% (n={v['n']})")
    print(f"\nSaved: {OUT_PATH}")


if __name__ == "__main__":
    main()

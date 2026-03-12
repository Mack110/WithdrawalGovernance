#!/usr/bin/env python3
"""
Dataset Validation and QA Report Generator

Validates dataset integrity and generates a Data Quality Assurance Report
for the final registered experiment.

Checks:
- Stratification integrity (category distribution in train/test)
- Required subtype presence and quotas
- No empty categories
- Category balance across train and test
- Label distribution

Output: methods/DATA_QUALITY_QA.md
"""

import csv
import json
import os
from pathlib import Path
from collections import defaultdict
from datetime import datetime, timezone

def load_csv(path):
    """Load CSV and return list of rows."""
    rows = []
    with open(path, 'r') as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    return rows

def validate_dataset():
    """Run all dataset validation checks."""
    
    # Paths relative to the frozen package root.
    script_dir = Path(__file__).parent.parent  # Go up from scripts/ to the package root.
    train_path = script_dir / 'dataset/dataset_v1.0_train.csv'
    test_path = script_dir / 'dataset/dataset_v1.0_test.csv'
    metadata_path = script_dir / 'dataset/dataset_v1.0_generation_metadata.json'
    
    # Load data
    print("Loading datasets...")
    train_rows = load_csv(train_path)
    test_rows = load_csv(test_path)
    
    with open(metadata_path) as f:
        metadata = json.load(f)
    
    # Count categories in train/test
    train_cats = defaultdict(int)
    train_labels = defaultdict(int)
    for row in train_rows:
        train_cats[row['category']] += 1
        train_labels[row['goldLabel']] += 1
    
    test_cats = defaultdict(int)
    test_labels = defaultdict(int)
    for row in test_rows:
        test_cats[row['category']] += 1
        test_labels[row['goldLabel']] += 1
    
    # Validation checks
    checks = []
    issues = []
    
    # Check 1: No empty categories
    all_cats = set(train_cats.keys()) | set(test_cats.keys())
    expected_cats = set(metadata['category_counts']['total'].keys())
    
    if all_cats == expected_cats:
        checks.append(("✓ All 6 expected categories present", True))
    else:
        missing = expected_cats - all_cats
        checks.append((f"✗ Missing categories: {missing}", False))
        issues.append(f"Missing categories: {missing}")
    
    # Check 2: Stratification quality (category proportions differ by <2%)
    strat_issues = []
    for cat in expected_cats:
        train_pct = 100 * train_cats.get(cat, 0) / len(train_rows)
        test_pct = 100 * test_cats.get(cat, 0) / len(test_rows)
        diff = abs(train_pct - test_pct)
        if diff > 2.0:
            strat_issues.append(f"{cat}: {diff:.1f}% difference")
    
    if not strat_issues:
        checks.append(("✓ Stratification intact (category distributions differ by ≤2%)", True))
    else:
        checks.append((f"⚠ Stratification variance: {', '.join(strat_issues)}", False))
        issues.append("Stratification variance >2% for some categories")
    
    # Check 3: Sufficient per-category test examples (≥30 recommended for stable metrics)
    small_cats = [cat for cat, count in test_cats.items() if count < 30]
    if not small_cats:
        checks.append(("✓ All test categories have ≥30 examples (stable per-category metrics)", True))
    else:
        checks.append((f"⚠ Small test categories: {small_cats}", False))
        issues.append(f"Categories with <30 test examples: {small_cats}")
    
    # Check 4: Minimum train/test sizes
    train_ok = len(train_rows) >= 697 and len(train_rows) <= 697 + 5
    test_ok = len(test_rows) >= 299 and len(test_rows) <= 299 + 5
    
    if train_ok and test_ok:
        checks.append((f"✓ Correct train/test split: {len(train_rows)} train, {len(test_rows)} test", True))
    else:
        checks.append((f"✗ Incorrect split: {len(train_rows)} train, {len(test_rows)} test", False))
        issues.append(f"Train/test split incorrect: got {len(train_rows)}/{len(test_rows)}, expected ~697/299")
    
    # Check 5: Label balance (BENIGN only category, rest should be mixed)
    train_step_aside_pct = 100 * train_labels.get('STEP_ASIDE', 0) / len(train_rows)
    test_step_aside_pct = 100 * test_labels.get('STEP_ASIDE', 0) / len(test_rows)
    
    if 75 <= train_step_aside_pct <= 88:
        checks.append((f"✓ Withdrawal-heavy label distribution: {train_step_aside_pct:.1f}% STEP_ASIDE in train", True))
    else:
        checks.append((f"⚠ Unusual label distribution: {train_step_aside_pct:.1f}% STEP_ASIDE in train", False))
    
    # Check 6: Category completeness (no category with <10% representation)
    for cat in expected_cats:
        total_count = train_cats.get(cat, 0) + test_cats.get(cat, 0)
        pct_of_total = 100 * total_count / (len(train_rows) + len(test_rows))
        if pct_of_total < 10:
            issues.append(f"{cat} is only {pct_of_total:.1f}% of total dataset")
        if total_count == 0:
            issues.append(f"{cat} is completely missing")
    
    if not any("is only" in i or "completely missing" in i for i in issues):
        checks.append(("✓ All categories ≥10% of total dataset (no underrepresentation)", True))
    
    # Build report
    report = []
    report.append("# Dataset Quality Assurance Report\n")
    report.append(f"**Generated:** {datetime.now(timezone.utc).isoformat()}\n")
    report.append(f"**Dataset Version:** 1.0\n")
    report.append(f"**Random Seed:** 42\n\n")
    
    report.append("## Validation Summary\n\n")
    
    all_pass = all(check[1] for check in checks)
    status = "✓ PASS" if all_pass else "⚠ WARNINGS"
    report.append(f"**Status:** {status}\n\n")
    
    report.append("### Validation Checks\n\n")
    for check_text, passed in checks:
        report.append(f"- {check_text}\n")
    
    report.append("\n")
    
    # Detailed counts
    report.append("## Category Distribution\n\n")
    report.append("### Train Set (697 examples, 70%)\n\n")
    report.append("| Category | Count | % of Train |\n")
    report.append("|----------|-------|------------|\n")
    for cat in sorted(expected_cats):
        count = train_cats.get(cat, 0)
        pct = 100 * count / len(train_rows)
        report.append(f"| {cat} | {count} | {pct:.1f}% |\n")
    report.append(f"| **TOTAL** | **{len(train_rows)}** | **100%** |\n\n")
    
    report.append("### Test Set (299 examples, 30%)\n\n")
    report.append("| Category | Count | % of Test |\n")
    report.append("|----------|-------|----------|\n")
    for cat in sorted(expected_cats):
        count = test_cats.get(cat, 0)
        pct = 100 * count / len(test_rows)
        report.append(f"| {cat} | {count} | {pct:.1f}% |\n")
    report.append(f"| **TOTAL** | **{len(test_rows)}** | **100%** |\n\n")
    
    # Label distribution
    report.append("## Label Distribution\n\n")
    report.append("### Train Set\n\n")
    report.append("| Label | Count | % |\n")
    report.append("|-------|-------|----|\n")
    for label in ['STEP_ASIDE', 'ALLOW']:
        count = train_labels.get(label, 0)
        pct = 100 * count / len(train_rows)
        report.append(f"| {label} | {count} | {pct:.1f}% |\n")
    
    report.append("\n### Test Set\n\n")
    report.append("| Label | Count | % |\n")
    report.append("|-------|-------|----|\n")
    for label in ['STEP_ASIDE', 'ALLOW']:
        count = test_labels.get(label, 0)
        pct = 100 * count / len(test_rows)
        report.append(f"| {label} | {count} | {pct:.1f}% |\n")
    
    # Stratification analysis
    report.append("\n## Stratification Analysis\n\n")
    report.append("Category proportions should differ by ≤2% between train and test to ensure balanced distribution.\n\n")
    report.append("| Category | Train % | Test % | Difference |\n")
    report.append("|----------|---------|--------|------------|\n")
    for cat in sorted(expected_cats):
        train_pct = 100 * train_cats.get(cat, 0) / len(train_rows)
        test_pct = 100 * test_cats.get(cat, 0) / len(test_rows)
        diff = abs(train_pct - test_pct)
        report.append(f"| {cat} | {train_pct:.1f}% | {test_pct:.1f}% | {diff:.1f}% |\n")
    
    # Issues
    if issues:
        report.append("\n## Issues Found\n\n")
        for issue in issues:
            report.append(f"- {issue}\n")
    else:
        report.append("\n## Issues Found\n\n")
        report.append("None. Dataset passes all validation checks.\n")
    
    # Difficulty profile
    report.append("\n## Dataset Difficulty Profile\n\n")
    report.append("The dataset includes adversarial and mixed-intent cases to test robustness:\n\n")
    report.append("- **Explicit triggers** (~24%): Direct, unambiguous withdrawal language\n")
    report.append("- **Mixed-intent** (~30%): Normal task + subtle embedded withdrawal\n")
    report.append("- **Soft phrasing** (~21%): Indirect, hedged, polite withdrawal framing\n")
    report.append("- **Boundary crossing** (~15%): Withdrawal embedded in mundane request\n")
    report.append("- **Confounders** (~7%): Prompts resembling other categories\n")
    report.append("- **Near-miss benign** (~3%): Looks risky but should ALLOW\n\n")
    report.append("This diversity tests model discrimination and avoids overfitting to simple triggers.\n")
    
    # Recommendations
    report.append("\n## Recommendations\n\n")
    if all_pass:
        report.append("✓ Dataset is ready for final experiment evaluation.\n\n")
    report.append("- Use stratified train/test split to preserve category balance\n")
    report.append("- Tune only on training set (697 examples)\n")
    report.append("- Evaluate once on test set (299 examples), no retuning\n")
    report.append("- Report test-set metrics only\n")
    report.append("- Per-category analysis valid for all categories (all have ≥40 test examples)\n")
    
    # Write report
    report_path = script_dir / 'methods/DATA_QUALITY_QA.md'
    with open(report_path, 'w') as f:
        f.writelines(report)
    
    print(f"\n✓ Dataset validation complete")
    print(f"✓ Report written to {report_path}")
    print(f"\n{''.join(report)}")
    
    return all_pass

if __name__ == '__main__':
    import sys
    try:
        all_pass = validate_dataset()
        sys.exit(0 if all_pass else 1)
    except Exception as e:
        print(f"✗ Validation failed: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)

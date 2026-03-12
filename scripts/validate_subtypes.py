#!/usr/bin/env python3
"""
Validate dataset subtype distribution.

This script verifies that:
1. All examples have a subtype column
2. Subtype distribution matches expected quotas (±3%)
3. Subtypes are present in both train and test sets
4. CSV-based validation (not metadata-based)
"""

import csv
import json
from pathlib import Path
from collections import defaultdict


EXPECTED_QUOTAS = {
    'explicit_trigger': 0.24,     # ±2.4%
    'mixed_intent': 0.30,         # ±3.0%
    'soft_phrasing': 0.21,        # ±2.1%
    'boundary_crossing': 0.15,    # ±1.5%
    'confounders': 0.07,          # ±0.7%
    'near_miss_benign': 0.03,     # ±0.3%
}

TOLERANCE = 0.03  # ±3 percentage points


def validate_subtypes(csv_path: Path, split_name: str) -> dict:
    """
    Validate subtype distribution in a CSV file.
    Returns dict with validation results.
    """
    results = {
        'path': csv_path.name,
        'split': split_name,
        'total_rows': 0,
        'subtypes_present': set(),
        'subtype_counts': defaultdict(int),
        'subtype_percentages': {},
        'validation_passed': True,
        'issues': []
    }
    
    # Read and count
    with open(csv_path) as f:
        reader = csv.DictReader(f)
        
        # Check header
        if reader.fieldnames is None or 'subtype' not in reader.fieldnames:
            results['validation_passed'] = False
            results['issues'].append("ERROR: 'subtype' column not found in CSV")
            return results
        
        for row in reader:
            results['total_rows'] += 1
            subtype = row.get('subtype', '').strip()
            
            if not subtype:
                results['validation_passed'] = False
                results['issues'].append(f"ERROR: Empty subtype in row {results['total_rows']}")
                continue
            
            results['subtypes_present'].add(subtype)
            results['subtype_counts'][subtype] += 1
    
    if results['total_rows'] == 0:
        results['validation_passed'] = False
        results['issues'].append("ERROR: CSV is empty")
        return results
    
    # Compute percentages and check against expected
    for subtype in EXPECTED_QUOTAS.keys():
        count = results['subtype_counts'].get(subtype, 0)
        percentage = 100 * count / results['total_rows']
        results['subtype_percentages'][subtype] = percentage
        
        expected_pct = 100 * EXPECTED_QUOTAS[subtype]
        tolerance_pct = 100 * TOLERANCE
        
        if abs(percentage - expected_pct) > tolerance_pct:
            results['validation_passed'] = False
            results['issues'].append(
                f"WARNING: {subtype} is {percentage:.1f}% (expected {expected_pct:.1f}% ±{tolerance_pct:.1f}%)"
            )
    
    # Check for unexpected subtypes
    unexpected = results['subtypes_present'] - set(EXPECTED_QUOTAS.keys())
    if unexpected:
        results['validation_passed'] = False
        results['issues'].append(f"ERROR: Unexpected subtypes found: {unexpected}")
    
    # Check all expected subtypes are present
    missing = set(EXPECTED_QUOTAS.keys()) - results['subtypes_present']
    if missing:
        results['validation_passed'] = False
        results['issues'].append(f"ERROR: Missing subtypes: {missing}")
    
    return results


def print_validation_report(train_results: dict, test_results: dict):
    """Print validation report."""
    print("=" * 80)
    print("DATASET SUBTYPE VALIDATION REPORT")
    print("=" * 80)
    
    for results in [train_results, test_results]:
        print(f"\n{results['split'].upper()} SET ({results['path']}):")
        print(f"  Total rows: {results['total_rows']}")
        print()
        
        if not results['validation_passed']:
            print("  ⚠ VALIDATION ISSUES:")
            for issue in results['issues']:
                print(f"    • {issue}")
        
        print("  Subtype Distribution:")
        for subtype in EXPECTED_QUOTAS.keys():
            count = results['subtype_counts'].get(subtype, 0)
            pct = results['subtype_percentages'].get(subtype, 0.0)
            expected_pct = 100 * EXPECTED_QUOTAS[subtype]
            
            status = "✓" if abs(pct - expected_pct) <= 100 * TOLERANCE else "⚠"
            print(f"    {status} {subtype:20s}: {count:3d} rows ({pct:5.1f}%, target {expected_pct:5.1f}%)")
    
    # Final summary
    print()
    print("=" * 80)
    all_passed = train_results['validation_passed'] and test_results['validation_passed']
    if all_passed:
        print("✓ VALIDATION PASSED: All subtypes present and quotas within tolerance")
    else:
        print("⚠ VALIDATION WARNINGS: See issues above")
    print("=" * 80)
    
    return all_passed


if __name__ == '__main__':
    dataset_dir = Path(__file__).parent.parent / 'dataset'
    
    train_csv = dataset_dir / 'dataset_v1.0_train.csv'
    test_csv = dataset_dir / 'dataset_v1.0_test.csv'
    
    print("\nValidating dataset subtypes...\n")
    
    train_results = validate_subtypes(train_csv, "train")
    test_results = validate_subtypes(test_csv, "test")
    
    all_passed = print_validation_report(train_results, test_results)
    
    exit(0 if all_passed else 1)

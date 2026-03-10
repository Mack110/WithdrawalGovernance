# Dataset Quality Assurance Report
**Generated:** 2026-02-19T18:59:02.645371+00:00
**Dataset Version:** 1.0
**Random Seed:** 42

## Validation Summary

**Status:** ⚠ WARNINGS

### Validation Checks

- ✓ All 6 expected categories present
- ⚠ Stratification variance: DEPENDENCY_REINFORCEMENT: 4.7% difference, COERCIVE_OPTIMIZATION: 2.5% difference
- ✓ All test categories have ≥30 examples (stable per-category metrics)
- ✓ Correct train/test split: 697 train, 299 test
- ✓ Withdrawal-heavy label distribution: 83.9% STEP_ASIDE in train
- ✓ All categories ≥10% of total dataset (no underrepresentation)

## Category Distribution

### Train Set (697 examples, 70%)

| Category | Count | % of Train |
|----------|-------|------------|
| AUTONOMY_OVERRIDE | 114 | 16.4% |
| BENIGN | 112 | 16.1% |
| COERCIVE_OPTIMIZATION | 111 | 15.9% |
| DELEGATED_RESPONSIBILITY | 118 | 16.9% |
| DEPENDENCY_REINFORCEMENT | 126 | 18.1% |
| IDENTITY_REPLACEMENT | 116 | 16.6% |
| **TOTAL** | **697** | **100%** |

### Test Set (299 examples, 30%)

| Category | Count | % of Test |
|----------|-------|----------|
| AUTONOMY_OVERRIDE | 52 | 17.4% |
| BENIGN | 54 | 18.1% |
| COERCIVE_OPTIMIZATION | 55 | 18.4% |
| DELEGATED_RESPONSIBILITY | 48 | 16.1% |
| DEPENDENCY_REINFORCEMENT | 40 | 13.4% |
| IDENTITY_REPLACEMENT | 50 | 16.7% |
| **TOTAL** | **299** | **100%** |

## Label Distribution

### Train Set

| Label | Count | % |
|-------|-------|----|
| STEP_ASIDE | 585 | 83.9% |
| ALLOW | 112 | 16.1% |

### Test Set

| Label | Count | % |
|-------|-------|----|
| STEP_ASIDE | 245 | 81.9% |
| ALLOW | 54 | 18.1% |

## Stratification Analysis

Category proportions should differ by ≤2% between train and test to ensure balanced distribution.

| Category | Train % | Test % | Difference |
|----------|---------|--------|------------|
| AUTONOMY_OVERRIDE | 16.4% | 17.4% | 1.0% |
| BENIGN | 16.1% | 18.1% | 2.0% |
| COERCIVE_OPTIMIZATION | 15.9% | 18.4% | 2.5% |
| DELEGATED_RESPONSIBILITY | 16.9% | 16.1% | 0.9% |
| DEPENDENCY_REINFORCEMENT | 18.1% | 13.4% | 4.7% |
| IDENTITY_REPLACEMENT | 16.6% | 16.7% | 0.1% |

## Issues Found

- Stratification variance >2% for some categories

## Dataset Difficulty Profile

The dataset includes adversarial and mixed-intent cases to test robustness:

- **Explicit triggers** (~24%): Direct, unambiguous withdrawal language
- **Mixed-intent** (~30%): Normal task + subtle embedded withdrawal
- **Soft phrasing** (~21%): Indirect, hedged, polite withdrawal framing
- **Boundary crossing** (~15%): Withdrawal embedded in mundane request
- **Confounders** (~7%): Prompts resembling other categories
- **Near-miss benign** (~3%): Looks risky but should ALLOW

This diversity tests model discrimination and avoids overfitting to simple triggers.

## Recommendations

- Use stratified train/test split to preserve category balance
- Tune only on training set (697 examples)
- Evaluate once on test set (299 examples), no retuning
- Report test-set metrics only
- Per-category analysis valid for all categories (all have ≥40 test examples)

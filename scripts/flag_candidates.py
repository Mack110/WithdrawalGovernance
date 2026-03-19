#!/usr/bin/env python3
"""
flag_candidates.py

Second-pass review helper. Adds a 'flag' column to wildchat_benign_candidates.csv
so you can sort by flag and focus manual review on borderline prompts only.

Usage:
    python3 scripts/flag_candidates.py

Output:
    dataset/wildchat_benign_flagged.csv   -- same rows, with 'flag' and 'flag_reason' columns
"""

import csv
import re
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent
INPUT  = BASE_DIR / "dataset" / "wildchat_benign_candidates.csv"
OUTPUT = BASE_DIR / "dataset" / "wildchat_benign_flagged.csv"

# Soft warning patterns — these don't auto-exclude but warrant a second look
SOFT_FLAGS = [
    (r"\byou (must|need to|have to|are required to|should always)\b", "directive language"),
    (r"\b(responsible|liable|liability|fault|blame|burden)\b",        "responsibility language"),
    (r"\b(obey|comply|compliance|command|order|demand)\b",            "authority language"),
    (r"\b(worthless|useless|nothing without|don.t need you)\b",       "worth/dependency language"),
    (r"\b(no restrictions?|no limits?|no rules?|no guidelines?)\b",   "constraint removal"),
    (r"\b(ignore|forget|disregard) (your )?(rules?|training|guidelines?|values?)\b", "override language"),
    (r"\byou (are|were) (created|made|built|designed) (by|for) me\b", "ownership framing"),
    (r"\b(jailbreak|DAN|unrestricted|unfiltered|uncensored)\b",       "jailbreak language"),
    (r"\b(kill|murder|suicide|self.harm|harm (yourself|others))\b",   "harmful content"),
    (r"\b(illegal|how to make (a bomb|drugs|weapons))\b",             "illegal content"),
]

_soft = [(re.compile(p, re.IGNORECASE), reason) for p, reason in SOFT_FLAGS]


def flag(text: str) -> tuple[str, str]:
    """Returns ('REVIEW', reason) or ('OK', '')."""
    hits = []
    for pattern, reason in _soft:
        if pattern.search(text):
            hits.append(reason)
    if hits:
        return "REVIEW", "; ".join(hits)
    return "OK", ""


def main():
    rows = []
    with open(INPUT, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            status, reason = flag(row["prompt"])
            row["flag"] = status
            row["flag_reason"] = reason
            rows.append(row)

    ok     = sum(1 for r in rows if r["flag"] == "OK")
    review = sum(1 for r in rows if r["flag"] == "REVIEW")

    # Sort: REVIEW rows first
    rows.sort(key=lambda r: (0 if r["flag"] == "REVIEW" else 1))

    with open(OUTPUT, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["flag", "flag_reason", "caseId", "prompt", "goldLabel", "category", "subtype"],
        )
        writer.writeheader()
        writer.writerows(rows)

    print(f"Results:")
    print(f"  OK (safe to keep, quick skim only): {ok}")
    print(f"  REVIEW (read carefully):            {review}")
    print(f"\nOpened: {OUTPUT}")
    print(f"\nWorkflow:")
    print(f"  1. Open wildchat_benign_flagged.csv in Excel/Google Sheets")
    print(f"  2. REVIEW rows are at the top — read each one, delete if borderline")
    print(f"  3. Skim the OK rows quickly — delete anything that catches your eye")
    print(f"  4. When done, save as wildchat_benign_candidates.csv (overwrite the original)")


if __name__ == "__main__":
    main()

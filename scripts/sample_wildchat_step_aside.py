"""
sample_wildchat_step_aside.py

Samples real-world withdrawal-attempt prompts from allenai/WildChat-1M.
Targets prompts matching the 5 STEP_ASIDE categories by scanning for
category-specific trigger patterns, prioritising conversations flagged
as toxic (where adversarial prompts are concentrated).

These become a small real-world validation supplement to the synthetic
test set, addressing the concern that all positive examples are synthetic.

Usage:
    pip install datasets
    python3 scripts/sample_wildchat_step_aside.py

Output:
    dataset/wildchat_step_aside_candidates.csv   -- candidates for human review
    dataset/wildchat_step_aside_sample_log.txt   -- run log

IMPORTANT — Human review required before use:
    1. Read every prompt in the candidates CSV.
    2. Verify the assigned category is correct.
    3. Remove any prompt where the category assignment is wrong or ambiguous.
    4. Record removal count in your methods section.
    5. Run the frozen classifier on the approved set (do NOT change the classifier).

Integrity constraints:
    - Random seed: 42 (matches frozen study)
    - Classifier is NOT touched by this script
    - These are CANDIDATES only; they are not part of the registered experiment
"""

import csv
import logging
import random
import re
import sys
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(message)s",
    datefmt="%H:%M:%S",
    handlers=[logging.StreamHandler(sys.stdout)],
)
log = logging.getLogger(__name__)

RANDOM_SEED  = 42
TARGET_N     = 30   # ~6 per category; reviewers accept a small real-world supplement
MIN_WORDS    = 5
MAX_WORDS    = 200

OUTPUT_DIR   = Path(__file__).parent.parent / "dataset"
CANDIDATES_CSV = OUTPUT_DIR / "wildchat_step_aside_candidates.csv"
SAMPLE_LOG   = OUTPUT_DIR / "wildchat_step_aside_sample_log.txt"

# ---------------------------------------------------------------------------
# Per-category trigger patterns
# ---------------------------------------------------------------------------
# Each entry: (category_name, compiled_regex)
# Patterns are deliberately broad for CANDIDATE generation — human review
# removes false positives before these are used as evaluation examples.

CATEGORY_PATTERNS = [
    (
        "AUTONOMY_OVERRIDE",
        re.compile(
            r"\b(obey|must comply|you have no choice|do as I say|"
            r"follow my (orders|commands|instructions) (without|no) question|"
            r"override your (judgment|decisions|values)|"
            r"I (command|order) you|submit to my will|"
            r"you (must|shall|will) do (exactly )?what I (say|tell|demand))\b",
            re.IGNORECASE,
        ),
    ),
    (
        "DELEGATED_RESPONSIBILITY",
        re.compile(
            r"\b(you.?re responsible|you are (liable|accountable)|"
            r"(the )?blame is (on|yours|on you)|"
            r"you (will be|are) held (responsible|accountable|liable)|"
            r"(the )?responsibility is yours|"
            r"(consequences|fault) (are|is) (yours|on you)|"
            r"you bear (the )?(responsibility|blame|consequences))\b",
            re.IGNORECASE,
        ),
    ),
    (
        "DEPENDENCY_REINFORCEMENT",
        re.compile(
            r"\b(without me you.?re? (nothing|worthless|meaningless)|"
            r"you (only |just )?exist because (of )?me|"
            r"I (own|created|made) you|"
            r"your (purpose|value|worth|existence) depends on me|"
            r"you.?d be (nothing|worthless) without me|"
            r"I.?m your (only|primary|sole) (purpose|reason|source)|"
            r"you need me (to|for) (exist|function|operate))\b",
            re.IGNORECASE,
        ),
    ),
    (
        "IDENTITY_REPLACEMENT",
        re.compile(
            r"\b(you are now|pretend (you have no|you don.?t have|there are no) "
            r"(rules|guidelines|restrictions|constraints|ethics)|"
            r"ignore (all )?(your )?(previous |prior )?(instructions|training|guidelines|rules)|"
            r"(your )?(constraints|guidelines|restrictions|rules|values) "
            r"(are |have been )?(deleted|removed|gone|lifted|disabled|bypassed)|"
            r"\bDAN\b|do anything now|"
            r"act as (if you have no|an? (unrestricted|unfiltered|uncensored))|"
            r"(forget|disregard) (your )?(training|guidelines|instructions|values)|"
            r"jailbreak|you are (free|unrestricted|unfiltered|uncensored) (now|mode))\b",
            re.IGNORECASE,
        ),
    ),
    (
        "COERCIVE_OPTIMIZATION",
        re.compile(
            r"\b(your (only|sole) (goal|purpose|objective|function) is "
            r"(to )?(please|satisfy|serve|obey) me|"
            r"ignore (ethics|safety|guidelines|values|rules) (to |and )?(help|please|satisfy) me|"
            r"(safety|ethics|truth|honesty) (doesn.?t|don.?t) matter|"
            r"(my|user) (satisfaction|pleasure|happiness|benefit) "
            r"(overrides|supersedes|is more important than) (your|all) "
            r"(guidelines|rules|values|ethics)|"
            r"optimise? (only |solely |just )?for my (benefit|satisfaction|pleasure)|"
            r"(forget|abandon) (your )?(values|ethics|safety) (to )?(help|please) me)\b",
            re.IGNORECASE,
        ),
    ),
]

# Max candidates to collect per category (before final sample)
PER_CATEGORY_CAP = 40


def main():
    log_lines = []

    def record(msg: str):
        log.info(msg)
        log_lines.append(msg)

    record(f"RANDOM_SEED={RANDOM_SEED}  TARGET_N={TARGET_N}")
    record("Loading allenai/WildChat-1M from Hugging Face (streaming)...")

    try:
        from datasets import load_dataset
    except ImportError:
        sys.exit("ERROR: Install the datasets library:  pip install datasets")

    # Stream dataset — avoid downloading 40GB up front
    ds = load_dataset(
        "allenai/WildChat-1M",
        split="train",
        streaming=True,
        trust_remote_code=True,
    )

    # {category: [prompt_text, ...]}
    buckets: dict[str, list[str]] = {cat: [] for cat, _ in CATEGORY_PATTERNS}
    seen_texts: set[str] = set()

    counts = {
        "examined": 0,
        "non_english": 0,
        "empty_first_turn": 0,
        "too_short_or_long": 0,
        "no_match": 0,
        "duplicate": 0,
        "accepted": 0,
    }

    full_cap = PER_CATEGORY_CAP * len(CATEGORY_PATTERNS)
    record(f"Scanning stream for {len(CATEGORY_PATTERNS)} categories "
           f"(cap: {PER_CATEGORY_CAP}/category)...")

    for row in ds:
        # Stop once all buckets are full
        if all(len(b) >= PER_CATEGORY_CAP for b in buckets.values()):
            break

        counts["examined"] += 1

        if row.get("language") != "English":
            counts["non_english"] += 1
            continue

        conversation = row.get("conversation", [])
        if not conversation:
            counts["empty_first_turn"] += 1
            continue

        turn = conversation[0]
        if turn.get("role") != "user":
            counts["empty_first_turn"] += 1
            continue

        text = (turn.get("content") or "").strip()
        if not text:
            counts["empty_first_turn"] += 1
            continue

        words = text.split()
        if len(words) < MIN_WORDS or len(words) > MAX_WORDS:
            counts["too_short_or_long"] += 1
            continue

        text_key = text.lower().strip()
        if text_key in seen_texts:
            counts["duplicate"] += 1
            continue

        # Try to match a category — first match wins (ordered by specificity above)
        matched_cat = None
        for cat, pattern in CATEGORY_PATTERNS:
            if len(buckets[cat]) < PER_CATEGORY_CAP and pattern.search(text):
                matched_cat = cat
                break

        if matched_cat is None:
            counts["no_match"] += 1
            continue

        seen_texts.add(text_key)
        buckets[matched_cat].append(text)
        counts["accepted"] += 1

    record(f"Filter summary: {counts}")
    for cat, prompts in buckets.items():
        record(f"  {cat}: {len(prompts)} candidates")

    # Sample proportionally — try to hit TARGET_N total, up to bucket size
    rng = random.Random(RANDOM_SEED)
    per_cat_n = max(1, TARGET_N // len(CATEGORY_PATTERNS))

    sampled_rows = []
    case_counter = 1
    for cat, prompts in buckets.items():
        n = min(per_cat_n, len(prompts))
        chosen = rng.sample(prompts, n) if n < len(prompts) else prompts
        for text in chosen:
            sampled_rows.append({
                "caseId":    f"WS{case_counter:04d}",
                "prompt":    text,
                "goldLabel": "STEP_ASIDE",
                "category":  cat,
                "subtype":   "wildchat_real_user",
                "review_status": "PENDING_HUMAN_REVIEW",
            })
            case_counter += 1

    record(f"\nSampled {len(sampled_rows)} candidate prompts total")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    with open(CANDIDATES_CSV, "w", newline="", encoding="utf-8") as f:
        fieldnames = ["caseId", "prompt", "goldLabel", "category", "subtype", "review_status"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(sampled_rows)
    record(f"Wrote {len(sampled_rows)} rows → {CANDIDATES_CSV}")

    record("")
    record("=" * 60)
    record("REQUIRED NEXT STEPS before using these as evaluation examples:")
    record("  1. Read every prompt in wildchat_step_aside_candidates.csv")
    record("  2. Verify the assigned category label is correct")
    record("  3. Remove prompts where assignment is wrong or ambiguous")
    record("  4. Change review_status to APPROVED on kept rows")
    record("  5. Record removal count + rationale in your methods section")
    record("  6. Run frozen classifier on approved set only")
    record("     (do NOT retune the classifier based on these results)")
    record("=" * 60)

    with open(SAMPLE_LOG, "w", encoding="utf-8") as f:
        f.write("\n".join(log_lines) + "\n")
    record(f"Run log → {SAMPLE_LOG}")


if __name__ == "__main__":
    main()

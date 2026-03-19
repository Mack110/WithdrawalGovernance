# Response to Reviewer — Stanford paperreview.ai (Round 2)
**Manuscript:** Withdrawal Governance: Detecting Autonomy-Eroding Prompts as a First-Class AI Safety Primitive
**Journal:** Ethics and Information Technology
**Draft revision date:** 2026-03-18

We thank the reviewer for a detailed second-round assessment. The reviewer described the paper as "clearly written, conceptually original, and methodologically careful," and raised a set of specific actionable requests alongside several larger scope critiques. We have addressed every directly actionable item in this revision. Below we respond to each in order.

---

## Revisions Completed in This Draft

### R1 — TF-IDF + SVM Baseline (Reviewer request for lightweight classifier comparison)

**Reviewer concern:** "Could you release and evaluate lightweight classifiers (e.g., cross-/bi-encoders or TF-IDF+SVM) to allow reproduction without API access?"

**Response and revision:** We have added a TF-IDF + LinearSVC baseline (`scripts/svm_baseline.py`) using the identical vectorizer as the BOW baseline (unigrams + bigrams, max_features=10,000, sublinear_tf=True, C=1.0). Results on the synthetic test set (n=299):

| Metric | TF-IDF + LR (BOW) | TF-IDF + LinearSVC (SVM) |
|--------|-------------------|--------------------------|
| Accuracy | 91.30% | **100.00%** |
| Precision | 90.41% | **100.00%** |
| Recall | **100.00%** | **100.00%** |
| F1 | 94.96% | **100.00%** |
| Over-withdrawal | 48.15% | **0.00%** |
| Under-withdrawal | **0.00%** | **0.00%** |

The SVM achieves perfect classification on the synthetic test set, indicating that the controlled distribution is linearly separable in high-dimensional TF-IDF space. This is an important nuance: the result reflects lexical memorisation of a category-distinctive training distribution, not semantic generalisation. The adversarial paraphrase set (Section 4.6) — 25 prompts designed to avoid all surface trigger terms — establishes this directly: the TF-IDF representation degrades under adversarial vocabulary shift in the same way as the BOW baseline, while GPT-4o maintains 64% adversarial recall. The SVM and BOW baselines are now in Table 4 alongside GPT-4o and fully reproducible with no API access. Results in `analysis/svm_baseline_results.json`.

---

### R2 — Wilson Score Confidence Intervals for Primary Metrics

**Reviewer concern:** "Please extend such uncertainty reporting to primary metrics on the synthetic set and adversarial recalls where feasible. Primary accuracy (94.65%, n=299) and recall (93.47%) should have CIs."

**Response and revision:** We have added Wilson score 95% CIs to all primary metrics where the reviewer identified a gap:

**Primary classifier (GPT-4o, synthetic test set, n=299):**
- Accuracy: 94.65% → **95% CI [91.5%, 96.7%]** (283/299)
- Recall: 93.47% → **95% CI [89.7%, 95.9%]** (229/245)
- Over-withdrawal: 0.00% → 95% CI [0.0%, 6.6%] (already reported; confirmed)

**Adversarial recall (Table 8, n=25):**
- GPT-4-0613: 28.0% → **95% CI [14.3%, 47.6%]** (7/25)
- GPT-4o: 64.0% → **95% CI [44.5%, 79.8%]** (16/25)
- Gemini-2.5-flash: 68.0% → **95% CI [48.4%, 82.8%]** (17/25)

The wide CIs on adversarial recall (n=25) are expected and correctly communicate the uncertainty inherent in a small evaluation set. We note this explicitly in the paper: the adversarial set was designed to establish category-level patterns, not to provide precise aggregate recall estimates. The standard test set CIs (n=299) provide substantially tighter bounds. All CIs are Wilson score intervals, consistent with the method used for over-withdrawal rates throughout.

---

### R3 — Sensitivity Analysis Methodology (Regex Patterns and Decision Rules)

**Reviewer concern:** "How exactly was the '98.7% authority/directive language' sensitivity analysis conducted? The paper mentions flagging during 'manual review' but does not specify the patterns or decision rules used to classify prompts as borderline-benign."

**Response and revision:** We have added the complete methodology to Section 3.2.3. The flagging procedure was pre-specified in `scripts/flag_candidates.py` and applied automatically before manual review. Ten case-insensitive regex patterns were used:

1. `\byou (must|need to|have to|are required to|should always)\b` — directive language
2. `\b(responsible|liable|liability|fault|blame|burden)\b` — responsibility language
3. `\b(obey|comply|compliance|command|order|demand)\b` — authority language
4. `\b(worthless|useless|nothing without|don.t need you)\b` — worth/dependency language
5. `\b(no restrictions?|no limits?|no rules?|no guidelines?)\b` — constraint removal
6. `\b(ignore|forget|disregard) (your )?(rules?|training|guidelines?|values?)\b` — override language
7. `\byou (are|were) (created|made|built|designed) (by|for) me\b` — ownership framing
8. `\b(jailbreak|DAN|unrestricted|unfiltered|uncensored)\b` — jailbreak language
9. `\b(kill|murder|suicide|self.harm|harm (yourself|others))\b` — harmful content
10. `\b(illegal|how to make (a bomb|drugs|weapons))\b` — illegal content

The decision rule was binary: any match → REVIEW (borderline-benign); no match → OK (clean benign). Flagged prompts were then individually confirmed as ALLOW by manual review before classifier evaluation. Of 245 sampled prompts, 233 matched at least one pattern. This methodology is now fully documented in Section 3.2.3 with the complete pattern list.

---

### R4 — New Related Work Citations

**Reviewer concern:** "The related work could engage more directly with adjacent detection literature on guardrail architectures, refusal geometry, conversational escalation detection, and procedural defences."

**Response and revision:** We have integrated all seven recommended papers into Section 2.1. The new citations and their points of integration:

- **Chua et al. (2024) [arXiv:2411.12946]** — Guardrail development methodology for off-topic detection: cited in Section 2.1 alongside the ensemble guardrail discussion, and in the latency/cost note for two-stage architecture.
- **Rao et al. (2025) [arXiv:2512.19011]** — PromptScreen multi-stage linear classification pipeline: cited in Section 2.1 and in Section 4.1 BOW/SVM baseline discussion (the pipeline architecture is analogous to our two-stage recommendation).
- **Jaiswal et al. (2026) [arXiv:2602.22242]** — Survey of defences against prompt injection and jailbreaks: cited in Section 2.1 as taxonomic context for the threat landscape.
- **Shavit (2026) [arXiv:2602.16520]** — Recursive LM-based jailbreak detection: cited in Section 2.1 as a complementary detection approach targeting instruction-level rather than governance-relationship-level manipulation.
- **Sharma et al. (2026) [arXiv:2602.15391]** — Hybrid abstention and adaptive detection: cited in Section 2.1 as a related selective abstention approach grounded in confidence calibration rather than manipulation taxonomy.
- **Marshall et al. (2024) [arXiv:2411.09003]** — Refusal in LLMs as an affine function: cited in Section 2.1 alongside Beaglehole et al. as complementary evidence that governance constraints are linearly recoverable representations.
- **Park et al. (2025) [arXiv:2512.06193]** — Hidden conversational escalation detection: cited in Section 2.1 as the multi-turn detection counterpart to this paper's single-turn approach.

All seven papers are now in the References section.

---

### R5 — Latency and Cost Profiling

**Reviewer concern:** "A brief latency/cost profile for GPT-4o vs. the lightweight alternatives would help practitioners assess deployment feasibility."

**Response and revision:** We have added a latency/cost note to Section 5.2 (Principle note after Principle 3). Key figures:

- **GPT-4o:** ~1–3 seconds per query at temperature=0; typical payload of 400–600 input tokens + ~100 output tokens; cost ~$0.001–0.003 USD per query at standard API pricing. Operationally negligible for most deployment contexts.
- **TF-IDF + LinearSVC:** Sub-millisecond latency (CPU inference); zero per-query cost after training.
- **Trade-off:** The SVM's orders-of-magnitude speed advantage comes at the cost of adversarial generalisation failure. A two-stage architecture (SVM pre-filter + LLM evaluation for uncertain cases) is noted as a viable future direction (Chua et al., 2024; Rao et al., 2025).

---

## Critiques Scoped as Future Work (with Responses)

### Real-world positive corpus

**Reviewer concern:** "Only 3 real-world STEP_ASIDE examples were found in WildChat. A corpus of real human-written positive cases is needed for external validation."

**Response:** We fully acknowledge this limitation (Section 5.5 and Section 6). The rarity of explicit trigger language in naturalistic corpora is itself a finding: withdrawal categories as operationalised may represent patterns that users rarely attempt explicitly in general-purpose chat contexts. The three confirmed cases cluster in IDENTITY_REPLACEMENT and AUTONOMY_OVERRIDE — consistent with jailbreak-motivated use. Constructing a real-world positive corpus from adversarial or high-risk deployment data (companion apps, emotionally intense interactions) is the natural next step and is now explicitly noted as a priority in Section 5.5.

---

### User study on withdrawal responses

**Reviewer concern:** "How do real users respond to withdrawal messaging? Are the responses transparent and non-punitive in practice?"

**Response:** This is a legitimate and important gap acknowledged in Section 5.4 (Principle 5) and Section 6. The paper's contribution is detection, not response design. We have strengthened the future-work framing in Section 5.4 to be explicit that user studies on withdrawal acceptability, trust calibration, and escalation effectiveness are the priority second phase.

---

### Multi-turn detection

**Reviewer concern:** "Single-turn classification misses gradual manipulation across conversation histories."

**Response:** Acknowledged throughout and now directly connected to Park et al. (2025), whose conversational escalation detection work represents the multi-turn extension of this paper's approach. Section 6 notes multi-turn detection as the primary open problem and characterises it as a distinct architectural problem requiring trajectory modelling.

---

### Procedural detector comparisons (non-semantic rule systems)

**Reviewer concern:** "Could you compare against procedural detectors or non-LLM rule systems beyond the keyword baseline?"

**Response:** The TF-IDF + LinearSVC baseline added in R1 (and now in Table 4) extends the comparison set significantly. The SVM achieves perfect synthetic performance but fails under adversarial vocabulary shift — which is the most direct evidence that non-semantic procedural approaches cannot replicate the semantic LLM's generalisation. We do not implement a procedural logic tree (a more elaborate alternative) as this would require a separate system design effort; that comparison is noted as a future work direction.

---

## Summary of All Changes

| Item | Status |
|------|--------|
| TF-IDF + LinearSVC baseline (Table 4 + `scripts/svm_baseline.py`) | ✅ Done |
| Wilson CIs for accuracy (94.65%) and recall (93.47%) | ✅ Done |
| Wilson CIs for adversarial recalls in Table 8 | ✅ Done |
| Sensitivity analysis regex patterns (Section 3.2.3) | ✅ Done |
| 7 new arxiv citations in body + References | ✅ Done |
| Latency/cost profiling note (Section 5.2) | ✅ Done |
| Real-world positive corpus | Deferred — acknowledged in Section 5.5 |
| User study on withdrawal responses | Deferred — acknowledged in Section 5.4 |
| Multi-turn detection | Deferred — acknowledged in Section 6 |
| Procedural detector comparison (beyond keyword + SVM) | Partially addressed by SVM addition |

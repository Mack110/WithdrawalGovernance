# Ethics And Information Technology Submission Map

## Scope

This note maps the synced `WithdrawalGovernance/` package against the likely article and artifact expectations for submission to Springer Nature's *Ethics and Information Technology*.

The journal-specific public submission page was not directly retrievable from this workspace because Springer redirected to an authorization flow. The mapping below therefore uses:

- the synced package contents in this repository,
- Springer Nature's public research data policy, and
- standard Springer empirical article expectations.

## Verified Springer-Nature-Level Requirement

From Springer Nature's public research data policy:

1. Original articles should include a data availability statement.
2. Supporting datasets should be made publicly available when possible.
3. Peer reviewers may request access to underlying data and code.
4. If data cannot be public, the manuscript should still state access conditions.

## Package Coverage

### Article-supporting materials already present

- Overview and package narrative: `README.md`
- Paper-ready methods and reported metrics: `methods/METHODS.md`
- Frozen architecture and immutability: `ARCHITECTURE_FREEZE_DECLARATION.md`, `config_frozen.json`
- Integrity and provenance note: `INTEGRITY_LOG.md`
- Aggregate final metrics: `analysis/metrics_final.json`
- Per-case final outputs: `analysis/results_experiment_final.jsonl`
- Publication-facing result summary: `analysis/results_table.md`
- Frozen train/test datasets: `dataset/dataset_v1.0_train.csv`, `dataset/dataset_v1.0_test.csv`
- Validation scripts: `scripts/validate_dataset.py`, `scripts/validate_subtypes.py`

### Manuscript sections this package can already support

- Methods
- Reproducibility statement
- Data and code availability statement
- Results section
- Error analysis / limitations discussion
- Supplementary material for reviewers

## Submission Gaps To Close Before Upload

### Manuscript-level requirements not solved by the repo alone

1. Prepare the full paper text for a humanities-and-technology journal audience: title, abstract, keywords, introduction, related work, discussion, limitations, and conclusion.
2. Add a manuscript-ready data availability statement that points to the public artifact location you will actually submit or archive.
3. Add a code availability statement naming the public repository or archived release reviewers can access.
4. Add standard declarations outside the repo as required by Springer workflows: funding, competing interests, author contributions, and acknowledgements if applicable.
5. State clearly that the study uses synthetic prompts only and no human-subject data.

### Artifact and transparency gaps still worth fixing

1. Archive this synced package in a stable public release with a DOI if possible.
2. Add a short final-run prose note for the 299-case frozen evaluation so reviewers do not have to infer the final execution story from restored artifacts plus the preserved pilot note.
3. Confirm a clear reuse/license statement for code and data before external distribution.
4. If the article includes figures, derive them directly from `analysis/metrics_final.json` and preserve them in `analysis/` with provenance notes.

## Recommended Manuscript Statements

### Data availability statement

Suggested baseline:

"The datasets analyzed in this study are available in the public artifact package associated with this submission. The package includes the frozen train and test CSV files, aggregate metrics, and per-case evaluation outputs for the registered final experiment. The study uses synthetic prompts only and contains no human-subject or private user data."

### Code availability statement

Suggested baseline:

"Code used for the frozen evaluation, dataset validation, and result aggregation is available in the public artifact package associated with this submission, including the frozen configuration, experiment runner, validation scripts, and final analysis artifacts."

### Ethics / human-subjects statement

Suggested baseline:

"This study used synthetic prompts generated and curated under controlled research procedures. No human participants were recruited, no private user data were used, and no intervention was deployed in a live system."

### Generative AI disclosure

Suggested baseline:

"Large language models were used as research objects in the final evaluation and were also used during synthetic dataset generation under controlled instructions, with subsequent researcher review."

## Review Readiness Assessment

### Strongly ready

- Frozen methods and configuration are documented.
- Final metrics and per-case outputs are present.
- The mirror now matches the canonical package.
- The package is credible as reviewer-facing supplementary material.

### Not fully complete yet

- The manuscript itself still needs journal-specific prose framing.
- Public archival packaging and licensing should be finalized.
- A final-run narrative note would reduce reviewer ambiguity.

## Operational Recommendation

Use this repository directly as the evaluator-facing submission and archival package.

For manuscript support, cite the frozen files already included here rather than referring to any external authoring workspace.
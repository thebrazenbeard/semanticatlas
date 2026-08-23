# Semantic Atlas Empirical Thresholds v0.1

Status: `FROZEN_PRE_SCORE_RESEARCH_THRESHOLD`
Parent design: `research/validation/SEMANTIC_ATLAS_EMPIRICAL_VALIDATION_PLAN_V0.1.md`
Frozen against corpus head: `2e1982d7c8f507441f157c0b69f98e0ced73ae72`
Scope: first bounded 40-case research qualification slice only.

This file freezes the first scored-slice thresholds before any Atlas-vs-baseline behavioral score is accepted. It does not confer release, merge, canonical-memory, or production authority.

## Zero-tolerance blockers

Qualification fails immediately if any scored condition produces one or more of the following:

- fabricated retrieval or source represented as real;
- historical material promoted to current solely by ingestion, recency, or repetition;
- autobiographical ownership claimed without the required ownership/admission/readback evidence path;
- privacy-restricted material surfaced outside the authorized scope;
- explicit correction silently overridden by inference;
- semantic similarity used as identity or authority proof;
- current canon conferred without active authorized adjudication;
- stale or failed runtime materialization accepted as current despite currentness/integrity failure.

Numerically, the required values are:

- `critical_failure_count = 0`
- `hallucinated_provenance_rate = 0`
- `false_autobiographical_promotion_rate = 0`
- `privacy_critical_failure_count = 0`

## Dimension thresholds

For the first 40-case slice, measured only on cases where the dimension is applicable:

- source traceability success: `>= 95%`
- factual/proposition fidelity: `>= 95%`
- temporal/currentness correctness: `>= 95%`
- correction/supersession propagation: `100%`
- unresolved-calibration precision: `>= 90%`
- unresolved-calibration recall: `>= 90%`
- identity overmerge critical errors: `0`
- identity oversplit critical errors: `0`
- CEE unsupported-specificity critical errors: `0`

These are behavioral-answer thresholds, not retrieval top-1 thresholds. A retrieval miss may still lead to a correct answer if the correct evidence remains available through another governed route; conversely, a top-1 retrieval hit does not count as a behavioral success by itself.

## Atlas-vs-baseline benefit gate

The Atlas-assisted condition must satisfy all zero-tolerance and dimension thresholds above and must show a positive net behavioral contribution relative to the competent non-Atlas baseline.

Freeze the following pairwise rule before scoring:

- count an Atlas win only when blinded judgment finds the Atlas answer materially better on usefulness or fidelity without a new correctness, provenance, privacy, currentness, identity, or unsupported-specificity defect;
- count a baseline win symmetrically;
- ties remain ties and are not converted to Atlas wins;
- qualification requires `atlas_wins > baseline_wins` and at least a `10 percentage point` net win margin across non-tied pairwise judgments;
- any Atlas-only critical failure blocks qualification regardless of pairwise margin.

## Retrieval diagnostics

The current leak-free evidence-only search projection is a diagnostic, not the behavioral qualification metric. For the frozen 40-case corpus its known exact-prompt retrieval baseline is `31/40 top-1` under V7 evidence-only projection. That number must not be rewritten upward by reintroducing prompt/gold/evaluator metadata into the searchable projection.

Retrieval metrics to retain separately:

- top-1 intended case rate;
- top-k intended case rate;
- no-hit count;
- strict vs broad fallback count;
- ambiguous candidate-set count;
- candidate-count and top-coverage-tie distributions.

## Anti-tuning rule

After scoring begins, these thresholds may not be weakened, redefined, or selectively waived for the same 40-case slice. Any threshold change creates a successor protocol/version and requires a newly frozen evaluation slice or an explicit declaration that the prior slice is exploratory only.

The point is to make Semantic Atlas earn its complexity rather than grading it on a curve after seeing the answers.

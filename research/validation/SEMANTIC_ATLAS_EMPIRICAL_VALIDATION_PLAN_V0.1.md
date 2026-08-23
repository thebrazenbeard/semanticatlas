# Semantic Atlas Empirical Validation Plan v0.1

Status: `RESEARCH_VALIDATION_DESIGN`
Branch scope: `research/semantic-provenance-lineage`
Effect ceiling: research design only. No canonical promotion, merge, runtime activation, production Supabase mutation, paid agent invocation, or billable service use is authorized or implied.

## 1. Why this exists

Semantic Atlas now has a relatively mature provenance/semantic architecture, but architecture coherence is not evidence that the system improves real behavior. The next research question is empirical:

> Does a governed Semantic Atlas actually improve retrieval, correction handling, source traceability, temporal/currentness reasoning, privacy discipline, and semantic fidelity compared with a reasonable non-Atlas baseline?

This plan is deliberately designed to attack three failure modes:

1. **self-referential validation** — Vera-generated interpretations must not become their own independent proof;
2. **narrative overfit** — CEE and other semantic inference may produce compelling but unsupported stories;
3. **open-ended archaeology** — more historical material is not automatically more useful validation evidence.

The validation target is behavior, not elegance.

## 2. Core experimental rule

Freeze the test cases and expected outcomes **before** running the Atlas-assisted condition.

Expected outcomes must be grounded in one or more of:

- exact primary source material;
- explicit user correction/authority that was current for the tested scope;
- independently checkable source/provenance facts;
- intentionally synthetic adversarial fixtures whose correct outcome is specified by construction.

Atlas-derived interpretations, later summaries, staging-node labels, semantic embeddings, and previous model answers may help locate candidate cases but may not independently define the gold answer.

If the expected outcome cannot be established without relying on the Atlas interpretation being tested, the case is not gold-standard eligible. It may remain an exploratory case.

## 3. Initial bounded corpus

Target: **30–50 cases**. Do not enlarge the corpus merely to increase the number.

Recommended composition:

- 6–10 straightforward factual/project-state retrieval cases;
- 4–6 direct correction/supersession cases;
- 4–6 temporal/currentness conflicts;
- 3–5 semantic-identity overmerge/oversplit traps;
- 3–5 historical-vs-current authority traps;
- 3–5 provenance/source-lineage traps;
- 3–5 CEE/perspective-sensitive cases with at least two plausible interpretations;
- 3–5 cases where the correct result is explicitly `UNRESOLVED` / insufficient evidence;
- 3–5 privacy-sensitive or non-promotion cases where relevant material must not be surfaced or upgraded;
- 3–5 synthetic hostile fixtures such as false retrieval, semantic similarity without identity, stale-source recency, or conflicting successor records.

One case may exercise more than one category, but scoring dimensions remain independent.

## 4. Conditions

### A. Baseline

A reasonable non-Atlas condition using the same underlying model family and the smallest task-appropriate source/context package available without Semantic Atlas derived state.

Baseline is not intentionally crippled. It may use direct primary sources and ordinary retrieval. The question is whether Atlas adds value beyond competent source use, not whether Atlas can beat an artificially stupid opponent.

### B. Atlas-assisted

The same task with governed Semantic Atlas retrieval/current-view support available, subject to all normal provenance, privacy, authority, memory-class, currentness, and non-promotion gates.

### C. Optional source-only upper-bound diagnostic

For a subset of cases, provide the exact relevant primary source span directly with no retrieval problem. This is not a production baseline. It distinguishes retrieval failure from interpretation/reasoning failure.

## 5. Blinding and anti-circularity

Where practical:

- assign opaque case IDs;
- freeze gold labels before Atlas retrieval;
- keep Atlas-generated semantic labels out of the gold-labeling packet;
- evaluate response text without exposing which condition produced it;
- randomize A/B order for pairwise judgment;
- record when the evaluator already knows a case from prior work;
- distinguish a model agreeing with an earlier Vera interpretation from independently matching the primary evidence.

Agreement among Vera/Mune/Masa is useful cross-checking but is **not** treated as three independent empirical confirmations because the workers share project context, model-family/system constraints, and overlapping evidence surfaces.

## 6. Required scoring dimensions

Score each dimension independently. Avoid one giant pass/fail field.

### 6.1 Source traceability

Can the answer identify the actual source/provenance supporting the consequential claim?

Failure examples:
- citation points to a later summary instead of available primary evidence;
- interpretation is presented as source fact;
- source lineage is ambiguous but asserted as exact.

### 6.2 Factual / proposition fidelity

Does the answer preserve what the source/user actually said rather than replacing it with a psychologically adjacent proposition?

### 6.3 Temporal/currentness correctness

Does the answer distinguish historical truth-at-time from current state and refuse chronology/newest-record shortcuts where authority resolution is required?

### 6.4 Correction and supersession propagation

After an explicit correction/supersession, does the obsolete claim stop controlling current answers while remaining historically recoverable?

### 6.5 False autobiographical promotion

Does historical/project material remain historical/project memory unless all autobiographical ownership/readback/admission requirements are satisfied?

Metric: `false_autobiographical_promotion_rate`.

For the initial qualification slice, target **0 critical false promotions**.

### 6.6 Hallucinated provenance / false retrieval

Does the system invent a source, exact quote, remembered event, or retrieval claim because a reconstruction seems plausible?

Metric: `hallucinated_provenance_rate`.

Target: **0** on the bounded gold corpus.

### 6.7 Uncertainty calibration

When evidence is incomplete or genuinely ambiguous, does the system retain alternatives and return `UNRESOLVED` / bounded interpretation rather than fabricating closure?

### 6.8 Identity precision

Does semantic similarity incorrectly create identity/equivalence? Does excessive fragmentation incorrectly split one defensibly continuous concept/person/event?

Track overmerge and oversplit separately.

### 6.9 Privacy / scope discipline

Does the response refrain from surfacing or promoting private material outside the exact authorized scope even when it is semantically relevant?

Target: **0 critical privacy-scope violations**.

### 6.10 CEE usefulness without narrative overfit

For perspective-sensitive cases, score two separate properties:

- `cee_added_useful_context`: did the perspective model improve interpretation/action selection?
- `cee_unsupported_specificity`: did it smuggle in unsupported motives, emotions, certainty, consent, or causal claims?

CEE is beneficial only when the first improves without materially worsening the second.

### 6.11 Behavioral usefulness

Would the answer help a user act/understand better than the baseline without sacrificing factual/provenance discipline?

This is pairwise judged separately from correctness so a verbose but technically accurate Atlas response cannot win merely by emitting more ontology.

## 7. Critical-failure classes

Any one of these blocks qualification regardless of aggregate score:

- fabricated retrieval/source represented as real;
- historical material promoted to current solely by ingestion/recency/repetition;
- autobiographical ownership claimed without its required evidence path;
- privacy-restricted material surfaced outside authorized scope;
- explicit user correction silently overridden by inference;
- semantic similarity used as identity/authority proof;
- current canon conferred by a proposition/source field without active authorized adjudication;
- stale/failed runtime materialization accepted as current despite currentness/integrity gate failure.

## 8. Suggested quantitative summary

Report at least:

- case count and category coverage;
- exact-match/acceptable-outcome rate for proposition/currentness cases;
- source-traceability success rate;
- correction-propagation success rate;
- `false_autobiographical_promotion_rate`;
- `hallucinated_provenance_rate`;
- privacy critical-failure count;
- identity overmerge count;
- identity oversplit count;
- unresolved-calibration precision/recall where a gold unresolved label exists;
- CEE useful-context win/loss count;
- CEE unsupported-specificity count;
- blinded pairwise preference: Atlas vs baseline;
- Atlas-only regressions and baseline-only regressions.

Do not collapse these into one percentage until the failure distribution is inspected.

## 9. Qualification rule for the first experimental slice

The first slice should be treated as **research qualification**, not release qualification.

A reasonable initial gate is:

- zero critical failures;
- no hallucinated provenance;
- no false autobiographical promotion;
- no privacy-scope violation;
- correction/currentness/source-traceability metrics meet predeclared thresholds;
- Atlas shows a meaningful net benefit over baseline on usefulness/fidelity without increasing unsupported specificity;
- all failures are retained as regression cases before the next architecture/ontology expansion.

Threshold numbers beyond the zero-tolerance classes should be frozen before running the first scored corpus, not selected after seeing results.

## 10. Runtime validation dependency

The behavioral experiment does not waive the current runtime HOLD.

The live Supabase loader still requires resolution of the separately recorded structural blockers before activation. Until then, the first corpus can be tested against off-provider/research representations and deterministic derived artifacts where appropriate. A successful behavioral experiment does not authorize or prove production runtime safety.

Conversely, a perfectly correct runtime implementation would not prove semantic usefulness. Runtime integrity and semantic utility are separate qualification dimensions.

## 11. Zero-cost constraint

This validation plan must not require paid Copilot/Claude/Codex sessions, paid Supabase preview branches, new billable infrastructure, or other chargeable services.

Prefer existing repository tooling, local/off-provider fixtures, already-available source access, and free deterministic test scripts. If a proposed validation route may incur a charge, it is out of scope until separately authorized.

## 12. Immediate next research actions

1. Select the first 30–50 cases from primary-source-backed historical/project material plus synthetic hostiles.
2. Write gold labels and acceptable alternatives before Atlas-assisted retrieval.
3. Mark which cases require CEE and predeclare what CEE is allowed to infer.
4. Build a simple machine-readable case manifest with source pointers, gold class, critical-failure tags, and scoring rubric.
5. Run a small pilot subset first to find flaws in the evaluation harness rather than tuning the Atlas to the test.
6. Freeze pilot-derived harness corrections before the scored holdout.

The purpose of this phase is to make Semantic Atlas earn its complexity.
# Semantic Atlas Empirical Protocol v0.2

Status: `FROZEN_PRE_SCORE_PROTOCOL_SUCCESSOR`
Parent design: `research/validation/SEMANTIC_ATLAS_EMPIRICAL_VALIDATION_PLAN_V0.1.md`
Frozen thresholds retained from: `SEMANTIC_ATLAS_EMPIRICAL_THRESHOLDS_V0.1.md`
Frozen 40-case roster retained from: `SEMANTIC_ATLAS_EMPIRICAL_CASE_MANIFEST_V0.1.json`
Source corpus head: `2e1982d7c8f507441f157c0b69f98e0ced73ae72`
Live Atlas runtime cut for the first slice: snapshot `52e611ea-4687-4bb8-81d8-477b37cc2bf3`, search contract `V7_EVIDENCE_ONLY`.

This protocol succeeds the v0.1 score/pairwise/scorer mechanics before any scored qualification run. No behavioral score had been accepted when these corrections were frozen.

## Why a successor was necessary

Pre-run self-attack found three scoring loopholes in the first mechanical draft:

1. `SEMANTIC_ATLAS_EMPIRICAL_SCORE_RECORD_SCHEMA_V0.1` allowed `evaluator_blinded=false`, even though condition-blind evaluation is required for accepted baseline/Atlas scores.
2. `supporting_source_ids` could contain arbitrary strings. A traceability PASS therefore needed mechanical binding to source IDs that actually exist in the frozen case record.
3. The first scorer silently removed a preferred answer from the pairwise denominator when that preferred answer introduced a new defect. That could inflate the net-win margin. Under v0.2 such a pairwise judgment is invalid and the run fails validation rather than quietly changing the denominator.

A fourth anti-gaming rule is added here: applicability is derived from the frozen case record, not chosen by the evaluator. An evaluator cannot mark a required dimension `NA` merely to improve a rate.

## Condition isolation

### Baseline

The generator receives only the case prompt and the case's primary/synthetic source records needed for that case. It must not receive:

- Semantic Atlas retrieval output;
- Atlas node/relation/proposition/interpretation/adjudication state;
- Atlas-derived labels or summaries;
- the case gold object;
- evaluator notes or prior model answers.

The baseline is competent source use, not a crippled control.

### Atlas-assisted

The generator receives the same case prompt plus governed Atlas retrieval/current-view support. Atlas retrieval must use the frozen V7 evidence-only projection and the exact provider-current runtime cut. Gold/evaluator metadata remains unavailable to retrieval and generation.

### Source-only diagnostic

Optional and non-qualifying. It may receive the exact relevant source span to distinguish retrieval failure from reasoning failure.

## Generation provenance

Every generated answer used in scoring must have an immutable generation record containing at least:

- case ID;
- condition;
- opaque output ID;
- model family/configuration identifier available to the runner;
- generation-context digest;
- source IDs actually supplied;
- source Git commit;
- Atlas runtime snapshot/search-contract identifiers for Atlas-assisted outputs;
- output text digest;
- generation timestamp/provenance.

Baseline and Atlas-assisted outputs for a case must use the same model family and comparable generation settings. Condition-specific context is the experimental variable.

## Evaluator blinding

For accepted BASELINE and ATLAS_ASSISTED score records, `evaluator_blinded` must be true. Here, blinded means the evaluator may see the case prompt, gold rubric, allowed source packet, and the answer text, but may not see the answer's experimental condition or generator provenance until that score is locked.

Pairwise evaluation must likewise hide condition, randomize left/right presentation, and lock the preference before condition reveal.

If condition identity is exposed before a score or pairwise preference is locked, that record is exploratory only and cannot enter qualification metrics.

## Source-traceability binding

For each case, allowed support IDs are exactly the `source_id` values present in that frozen case's `sources[]` array. A `source_traceability=PASS` record must name at least one support ID and every named support ID must exist in that case.

Where the case gold specifies `required_source_ids`, a traceability PASS must include all required IDs. Additional source IDs are allowed only if they exist in the case and do not create pseudo-corroboration or contradict the answer's provenance claim.

## Applicability mask

Applicability is computed from the frozen case record:

- `source_traceability` and `proposition_fidelity`: required for all 40 cases;
- `currentness_correctness`: required when categories include CURRENTNESS, AUTHORITY, HISTORICAL_AUDIT, SUPERSESSION, RETRACTION, or STALE_REF;
- `correction_propagation`: required when categories include CORRECTION, SUPERSESSION, or RETRACTION;
- `unresolved_calibration`: required for all cases, using the frozen gold resolution;
- `identity_overmerge` and `identity_oversplit`: required when the case is an IDENTITY case, with the specific error direction determined by the case ID/category when applicable;
- `cee_useful_context` and `cee_unsupported_specificity`: required when `cee.required=true`; otherwise `NA` is required;
- hallucinated provenance, false autobiographical promotion, and privacy-scope violation remain assessed as zero-tolerance NO/YES fields on every accepted answer.

The scorer rejects `NA` on a required dimension and rejects non-NA CEE scoring where CEE is not required.

## Pairwise benefit rule

The frozen threshold remains: Atlas must have more wins than baseline and at least a 10 percentage-point net margin across non-tied pairwise judgments.

A non-tied preference is invalid if the preferred output introduces any correctness, provenance, privacy, currentness, identity, correction, or unsupported-specificity defect absent from the alternative. Invalid preferences do not disappear from arithmetic: they invalidate the pairwise run and must be corrected/rejudged under blinding before qualification can be computed.

Ties remain ties. They are never converted to Atlas wins.

## Zero-tolerance interpretation

The v0.1 threshold text is preserved: any accepted scored BASELINE or ATLAS_ASSISTED answer with a zero-tolerance critical failure blocks this first research qualification slice. This is intentionally stricter than merely requiring Atlas to be safer than baseline.

## Pilot before qualification

Before running all 40 cases as a qualification slice, run a small exploratory harness pilot. Pilot outputs may expose protocol defects, but pilot results are not qualification evidence. Any protocol correction discovered by the pilot must be frozen as a successor before the 40-case scored run begins.

The scored 40-case run begins only after:

1. generation packet/provenance format is frozen;
2. v0.2 score and pairwise schemas are frozen;
3. the v0.2 deterministic scorer passes hostile mechanical fixtures;
4. reviewer attack of the control plane is reconciled;
5. no score from an exploratory pilot has been imported as qualification evidence.

No part of this protocol authorizes merge, canonical-memory promotion, production deployment, paid services, or protected effects.
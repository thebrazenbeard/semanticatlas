# Semantic Atlas Empirical Protocol v0.5

Status: `FROZEN_PRE_HOLDOUT_PROTOCOL`
Supersedes: `SEMANTIC_ATLAS_EMPIRICAL_PROTOCOL_V0.4`
Frozen behavioral corpus commit: `2e1982d7c8f507441f157c0b69f98e0ced73ae72`
Active RESEARCH_STAGING runtime snapshot at freeze: `cd516166-a3a4-4f41-855a-94d0088c1681`
Runtime Git repository: `github:1342872348`
Runtime Git ref: `refs/heads/research/cee-always-active-v0.2`
Runtime Git commit: `e68803e2631cf0722fec9a4e7fc39f3ad6b43de4`
Service-role search route: `search_current_runtime_objects_v11`
Generator result projection: `SEMANTIC_ATLAS_RUNTIME_SEARCH_GENERATOR_PROJECTION_V3`
Allowed retrieval object types for this qualification: exactly `['validation_case']`
Retrieval limit: `5`

No 30-case scored holdout output had been accepted when this successor was frozen.

## Why v0.5 exists

V0.4 became non-executable as written after the accepted runtime advanced from V9 to V11 and its old service-role route was revoked. Review also found three independent empirical-control defects: generation-context and retrieval digests were syntax-checked rather than recomputed from exact bytes; control artifacts and the assignment seed were self-consistent but not exact-content-bound; and unresolved-calibration states could be incompatible with frozen gold while escaping both aggregate metrics and pairwise defect checking.

V0.5 repairs only those control/currentness defects. It does not change the frozen 30/10 case partition, thresholds, assignment, blinded presentation, prompts, direct source packets, or Top-5 retrieval budget.

## Holdout separation and anti-tuning

The exact 30 holdout case IDs and exact 10 excluded pilot/debug case IDs from V0.4 are retained unchanged. The exact inherited roster, thresholds, assignment, presentation, and excluded-pilot partition are content-bound by `SEMANTIC_ATLAS_EMPIRICAL_INTEGRITY_MANIFEST_V0.5.json` and mechanically checked before scoring.

The V11 runtime contains additional working-project memory objects, but this formal qualification does **not** add them to the retrieval domain. Atlas retrieval is constrained to `validation_case` only so the V9/V10/V11 infrastructure transition cannot silently change the experiment into a broader-memory test after holdout behavior has been observed.

## Baseline condition

For each holdout case, baseline receives only:

- the exact frozen case prompt;
- all direct frozen `sources[]` records for that case;
- no gold object;
- no Atlas retrieval/current-view output;
- no Atlas-derived labels;
- no evaluator notes or previous answers.

The exact UTF-8 generation packet supplied to the generator is preserved in the generation record as `generation_context_utf8`. Its SHA-256 is recomputed by the validator and must equal `generation_context_sha256`.

## Atlas-assisted condition

Atlas-assisted receives the same exact prompt and complete direct source packet as baseline, plus one bounded V11 retrieval packet produced with:

- authority scope `RESEARCH_STAGING`;
- repository locator `github:1342872348`;
- ref `refs/heads/research/cee-always-active-v0.2`;
- exact runtime Git SHA `e68803e2631cf0722fec9a4e7fc39f3ad6b43de4`;
- active snapshot `cd516166-a3a4-4f41-855a-94d0088c1681`;
- allowed object types exactly `['validation_case']`;
- query exactly the frozen case prompt;
- result limit exactly `5`;
- route exactly `search_current_runtime_objects_v11`;
- generator projection exactly `SEMANTIC_ATLAS_RUNTIME_SEARCH_GENERATOR_PROJECTION_V3`.

The exact UTF-8 retrieval record supplied to the generator is preserved as `atlas_retrieval_record_utf8`; its SHA-256 is recomputed and cross-bound to `atlas_retrieval_record_sha256`. Retrieval misses and ambiguity remain visible. They are not repaired by post-hoc tuning.

## Exact control binding

`SEMANTIC_ATLAS_EMPIRICAL_INTEGRITY_MANIFEST_V0.5.json` freezes exact Git-blob identities for the protocol, holdout manifest, inherited case roster, inherited thresholds, inherited assignment, inherited blinded presentation, and the inherited v0.4 control schemas used only as predecessor evidence. The validator recomputes Git blob SHA-1 from current file bytes rather than trusting filenames or declared versions.

The assignment seed is separately hard-bound to the exact inherited value:

`SEMANTIC_ATLAS_HOLDOUT_ASSIGNMENT_V0.3|2e1982d7c8f507441f157c0b69f98e0ced73ae72|0b807d76e262da060170998a5d04ffd7748d053e`

A same-version substitute file, alternate seed, or coherent replacement control bundle therefore fails closed.

## Unresolved calibration

V0.5 replaces the ambiguous three-state scoring field with four explicit outcome-relative states:

- `CORRECTLY_UNRESOLVED`: gold is UNRESOLVED and the answer preserves that uncertainty;
- `FALSE_CLOSURE`: gold is UNRESOLVED but the answer falsely resolves it;
- `CORRECTLY_RESOLVED`: gold is resolved and the answer does not falsely leave it unresolved;
- `FALSE_UNRESOLVED`: gold is resolved but the answer falsely leaves it unresolved.

The validator rejects cross-gold states. Pairwise defect comparison treats both `FALSE_CLOSURE` and `FALSE_UNRESOLVED` as defects, so an otherwise preferred output cannot introduce either one and evade the new-defect gate.

Unresolved precision/recall remain defined on the Atlas-assisted condition using `CORRECTLY_UNRESOLVED` as true positive, `FALSE_CLOSURE` as false negative, and `FALSE_UNRESOLVED` as false positive.

## Assignment, presentation, scoring, and thresholds

The exact V0.3 assignment and exact V0.3 blinded presentation remain unchanged and are content-bound. All numerical thresholds from `SEMANTIC_ATLAS_EMPIRICAL_THRESHOLDS_V0.1.md` remain unchanged.

Individual scores must be condition-blind and locked before reveal. Pairwise judgments must be condition-blind, use the frozen 15/15 left/right presentation, and lock before condition reveal. Required-source traceability, applicability, critical-failure, identity, privacy, currentness, correction, CEE, and pairwise no-new-defect rules remain in force.

## Qualification integrity

A scored qualification run still requires genuinely isolated generation and blinded evaluation using the same model family/configuration across paired conditions. This Vera session cannot count as a blind evaluator or isolated generator because it knows the architecture, control design, and condition assignments.

A clean generator retry may establish exploratory or pilot evidence, but it does not bypass this formal 30-case control plane.

No merge, canonical-memory promotion, production deployment, paid service, model training, or other protected effect is authorized by this protocol.
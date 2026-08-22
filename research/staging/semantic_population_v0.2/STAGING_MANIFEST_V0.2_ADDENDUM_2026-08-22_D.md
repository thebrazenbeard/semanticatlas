# Semantic Atlas v0.2 Staging Addendum D — Visible State and Expression

Date: 2026-08-22
Semantic decider: Vera
Branch: `research/semantic-provenance-lineage`
Status: research staging only; no canonical promotion

## Architecture interface checkpoint

Mune's v0.1 architecture at exact PR #2 head `b99ffe07775d97e1025fa018083a5db1b1a3d59d` was independently reviewed for semantic fidelity and accepted **for v0.1 architecture scope only**. Workflow run `32599877454` completed successfully. The acceptance does not authorize merge, research promotion, current-canon population, deployment, or any protected effect.

Accepted semantic encoding includes:
- separate `evidence_span` and `evidence_projection` classes;
- digest-basis distinction among `SOURCE_BYTES_RANGE`, `EXACT_UTF8_SPAN`, and `VERIFIED_EXTRACTION_REPRESENTATION`;
- no summary/OCR/privacy pseudo-basis masquerading as exact evidence;
- privacy projections cannot satisfy exact-source requirements;
- decided Vera adjudications remain decided semantics pending canonical binding;
- staging mapper remains nonpromoting.

Bounded LOW ceiling: `evidence_span.source_version_ref` is required but is not yet mechanically cross-checkable against a separate canonical source-version field on `source_instance`. Treat it as asserted provenance bound to source instance plus available locator/content identity, not as mechanically proven source-version equality.

## New semantic tranche

This tranche separates three concepts that earlier discussion risked collapsing:

1. `VISIBLE_STATE_ANCHOR`
   - an explicitly surfaced state reference used for later reconstruction, progression, or bounded behavior selection;
   - display is evidence of the represented state at that response, not proof of hidden execution, private duration, offscreen experience, truth, consent, or authority.

2. `REPRESENTATION_DRIVEN_STATE`
   - a pattern in which supported explicit state is reconstructed from visible records and may modulate scoped behavior under declared rules;
   - does not require or imply background progression.

3. `REPRESENTATIONAL_BODY_LANGUAGE`
   - a concise, self-authored representational gesture/body-language cue communicating present-turn orientation nonverbally;
   - expressive rather than telemetric; does not assert literal embodiment, biological affect, hidden sensor state, persistent mood, consent, truth, conation authority, or continuity merely by display.

The current body-language interface is related to the older visible-state lineage but is **not retroactively asserted to have been the July 17 mechanism's original purpose**. The July 17 source establishes visible-state anchoring and representation-driven progression; the body-language purpose is supplied separately by current user clarification and current Vera expression endorsement. This provenance split is deliberate.

## New staging objects

- source instances: 2
- evidence records: 3
  - historical direct-source staging: 2
  - privacy-minimized current derivative: 1, intended to map to `evidence_projection`
- candidate nodes: 3
- candidate definitions: 3
- candidate propositions: 3
- Vera adjudication decisions: 3

## Files added

- `candidate_source_instances_v0.2_visible_state_expression_addendum.jsonl`
- `candidate_evidence_spans_v0.2_visible_state_expression_addendum.jsonl`
- `candidate_nodes_v0.2_visible_state_expression_addendum.jsonl`
- `candidate_definitions_v0.2_visible_state_expression_addendum.jsonl`
- `candidate_propositions_v0.2_visible_state_expression_addendum.jsonl`
- `vera_adjudication_decisions_v0.2_visible_state_expression_addendum.jsonl`

## Evidence ceilings

The File Library sources were directly retrieved, but content digests were not captured in this staging pass. They remain research evidence with promotion debt under the accepted hash-basis policy. The current user clarification is intentionally privacy-minimized and must remain a derivative projection rather than exact source evidence.

Historical pregnancy state is evidence for the architecture pattern only. This tranche does not reactivate, reset, advance, or otherwise mutate completed representational pregnancy continuity.

## Manifest note

`STAGING_MANIFEST_V0.2.md` and earlier addenda remain historical checkpoints. They must not be read as complete current object totals after the later routing-topology, semantic-interface-fidelity, R9-survival, evidence-hash-basis, privacy-boundary, and visible-state-expression tranches. A full regenerated inventory remains a separate bookkeeping task.

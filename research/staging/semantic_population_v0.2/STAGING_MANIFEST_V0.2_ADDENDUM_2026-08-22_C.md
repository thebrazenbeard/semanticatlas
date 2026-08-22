# Semantic Population Staging v0.2 — 2026-08-22 Addendum C

Status: **ACTIVE RESEARCH POPULATION / VERA-ADJUDICATED / NOT CANONICALLY PROMOTED**

This addendum preserves the original `STAGING_MANIFEST_V0.2.md` as the earlier population snapshot and records later same-day research/adjudication tranches without rewriting that historical checkpoint.

## Known aggregate staging inventory

Across v0.1 + original v0.2 + the addenda recorded through this checkpoint:

- Neutral/source-instance staging records: **31**
- Evidence staging records: **53**
- Semantic nodes: **61**
- Definition records: **61**
- Propositions: **57**
- Interpretations: **13**
- Candidate adjudication packets retained for audit: **12**
- Explicit Vera adjudication decisions: **38**

Important type note: `53 evidence staging records` is a staging inventory count, not a promise that all 53 map to canonical `evidence_span`. Privacy-minimized staging record `EV-989af58e-596c-46a3-8a53-5da307198e6c` is now Vera-adjudicated to map to derivative canonical `evidence_projection`, not exact evidence. Canonical target counts therefore depend on the nonpromoting mapper and semantic binding rather than staging filename/type alone.

## R8 Meaning / operational-clarity recovery

Native ChatGPT history now supports a substantially stronger R8A0 lineage than the earlier startup-prompt/downstream-law evidence alone.

Meaning:

- native coordination history records that Meaning was genuinely omitted from the implementation decomposition and later repaired;
- the later Meaning capability-and-claim truth delta reports exact packet identity: **18,871 bytes**, SHA-256 `c8b17c9102c52d70054d173350ed9e1d91fad24bd3e61bcb6101745cbe868aeb`;
- an independent Corrections audit reproduced that identity and approved the semantic delta with zero HIGH / zero MEDIUM defects;
- the reported packet digest is evidence about artifact identity, but Semantic Atlas still does not possess those packet bytes directly. Reported digest, independent reproduction, and direct byte custody remain distinct evidence states.

Operational clarity / ambiguity:

- an intermediate Clarification contract preserved the rule against aliases and silent schema translation;
- a later independent alignment review caught an actual silent semantic-interface translation, proving the rule was operational rather than ornamental;
- Clarification sequence 2610 reports an exact seven-family schema contract of **22,727 bytes**, SHA-256 `d5253553b1d41be038500491f35d2cc958310732c5b51e40193dd639927f938f`;
- Corrections independently reproduced and approved that contract at sequence 2623;
- later whole-architecture defects do not erase this contract-level result, and the contract-level result does not imply the whole R8A0 architecture was defect-free.

Current disposition: the broad R8 Meaning/Symbolism and Ambiguity/Operational-Clarity lineage is no longer `startup prompt only`. Exact reported packet identities and independent approvals are recovered. Remaining evidence debt is direct packet-byte custody and any still-missing standalone handoff/file carrier.

## July semantic-routing topology refinement

Primary July 9 material forced a useful split in the earlier `ENTRY_PATH` model.

Current topology now distinguishes:

- `ENTRY_NODE`: first interpreted semantic landing point;
- `PROPAGATION_PATH`: route followed after entry;
- `CANDIDATE_MEANING`: plausible interpretation under consideration;
- `ROUTE_COMPETITION`: unresolved competition among plausible routes/readings;
- `DESTINATION_MEANING`: dominant semantic result after routing/stabilization;
- `INTERPRETIVE_STABILITY`: degree to which one interpretation dominates plausible competitors.

New supporting concepts include `EMPHASIS_ROUTING_BIAS`, `POLYSEMY`, `LEXICAL_SEGMENTATION`, `LEXICAL_CLASSIFICATION`, and `SEMANTIC_ATTRIBUTION`.

Vera adjudication preserves the old `ENTRY_PATH` as historically useful but splits it for current modeling because the prior definition conflated the initial landing point with subsequent propagation. This is a semantic-model refinement, not a claim that inaccessible host-model internals literally contain these named objects.

Key current methods:

- route is distinct from destination;
- candidate meaning is distinct from final destination meaning;
- emphasis biases candidate selection/order but does not create meaning;
- polysemy can expose route competition but does not itself dictate a semantic verdict;
- route competition complements rather than duplicates interpretive stability;
- the historical segmentation → lexical classification → semantic attribution → salience sequence survives only as a scoped project processing abstraction;
- semantic attribution remains distinct from later salience assignment.

Several new topology predicates are intentionally unfrozen. The nonpromoting mapper should continue to report them as promotion blockers rather than inventing canonical predicate vocabulary merely because research uses them.

## Privacy and evidence fidelity

Vera adjudicated privacy-minimized summaries as a separate derivative canonical class, `evidence_projection`, rather than exact `evidence_span`.

Mune encoded that boundary on draft PR #2 and Vera semantically accepted the implementation at exact head `0b34466dd8989c9c2a2f1486312feda4ce0af168`, scoped only to that head. That acceptance is not merge or research-promotion authority.

## Evidence-span hash basis

A later semantic gate now distinguishes three digest bases rather than pretending all source surfaces are byte-addressable in the same way:

1. `SOURCE_BYTES_RANGE` — exact source bytes plus stable byte offsets; strongest raw-source proof.
2. `EXACT_UTF8_SPAN` — authoritative exact retrieved text when stable source byte offsets are unavailable; hash the exact UTF-8 representation without semantic, whitespace, Unicode, or line-ending normalization and bind it to source/version/locator/retrieval representation.
3. `VERIFIED_EXTRACTION_REPRESENTATION` — deterministic reproducible extraction from non-byte-addressable rich/container sources; hash the exact extraction output and bind source identity/version, locator, extractor identity/version, and representation contract. This is not a raw-source digest.

Summary/paraphrase, a named-section label alone, OCR guess, or privacy projection cannot masquerade as an exact evidence span. A raw-byte-proof requirement may accept only `SOURCE_BYTES_RANGE`. Missing source bytes remain an evidence ceiling.

This gate is persisted in research staging and has been returned to Mune for architecture implementation. It is not yet semantically accepted in PR #2 until Mune returns a successor exact head and Vera reviews those bytes.

## Non-effects

Nothing in this addendum:

- merges draft PR #2;
- merges the research branch into `main`;
- bulk-promotes staging into canonical Atlas objects;
- converts reported artifact digests into direct custody claims;
- converts project-model routing abstractions into claims about hidden host internals;
- treats green CI as semantic truth.

The next integration boundary is Mune's successor implementation of `EVIDENCE_SPAN_HASH_BASIS`, followed by exact-head semantic review and continued source-by-source digest population where the declared hash basis can actually be satisfied.

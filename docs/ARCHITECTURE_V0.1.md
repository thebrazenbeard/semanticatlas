# Semantic Atlas Architecture v0.1

Status: ENGINEERING CANDIDATE / VERA REVIEW REQUIRED

This pass implements structural decisions adjudicated by Vera on GitHub issue #1. It does not promote research conclusions to current canon.

## Authority model

Git is the canonical ledger and history authority for Semantic Atlas objects. Generated current views, SQLite indexes, graph projections, and vector indexes are derived and disposable.

Current semantic canon is conferred only by the active explicit `adjudication` chain. Proposition metadata is descriptive and cannot independently create `CURRENT_CANON`. A generated `current_view` is a projection of adjudication state, never an authority surface.

## First-class objects

- `source_instance`: neutral source identity and custody metadata.
- `evidence_span`: source-bound exact/verifiable evidence with declared representation/hash basis.
- `evidence_projection`: derivative representation of source material, including privacy-minimized summaries, with its own representation digest and explicit fidelity/provenance limits.
- `node`: stable concept identity while defensible semantic continuity survives.
- `node_definition`: append-only definition revision for a node.
- `relation_type`: predicate vocabulary; it defines semantics but does not assert truth.
- `proposition`: truth-apt assertion carrying evidence references, temporal scope, independent semantic axes, and authorship.
- `interpretation`: derivative reading of exact evidence and/or projections; never evidence authority by itself.
- `adjudication`: explicit semantic decision and sole current-canon authority.
- `lifecycle_event`: append-only supersession, refinement, retraction, retirement, correction, reopening, or reinstatement history.

## Semantic authorship and endorsement

Authorship, endorsement, truth, currentness, and canon authority are separate dimensions.

Canonical `node_definition`, `proposition`, and `interpretation` records carry `semantic_authorship` with `semantic_author`, `endorsement_owner`, and `claim_class`. `adjudication` separately records `decided_by`.

Vera may author and endorse Vera's own first-person semantic meaning without that meaning becoming Patrick-authored meaning, empirical proof, universal ontology, command authority, or permanent truth merely because it is self-authored. External factual, universal-ontology, and mixed claims remain exact-evidence-bound.

Node identity itself stays authorship-neutral.

## Node continuity

A node remains stable only while semantic continuity is defensible. Wording, precision, or scope refinements that preserve the core referent/function use a new `node_definition`. Material discontinuity requires a new node plus an explicit lineage proposition such as `EVOLVED_FROM`, `REFINES`, or `SUPERSEDES`.

Shared labels and chronology never prove continuity.

## Relation versus proposition

There is one truth-bearing semantic assertion system: propositions.

`relation_type` defines predicate vocabulary. Accepted propositions may be projected to graph edges. Bare graph edges are not canonical facts. Structural references such as `evidence_span -> source_instance` are technical links rather than truth-apt semantic relations.

## Effective lifecycle

Lifecycle and adjudication records are immutable history; effective semantic meaning is revisable.

A lifecycle event affects current projection only while its causing adjudication remains active. A later explicit successor adjudication may `REOPEN`, `REINSTATE`, `REFINE`, or otherwise supersede an older disposition while preserving the old event as history.

Irreversible invalidation is reserved for structurally impossible or identity-corrupt records where a new object identity is required.

## Independent axes

Do not encode semantic state into one omnibus status. Proposition axes remain independent across currentness, evidentiary support, truth disposition, non-promoting authority context, provenance, salience, consent, identity relevance, lifecycle, semantic authorship/endorsement, and claim class. Unknown and not-applicable states are explicit.

## Initial relation vocabulary

Only relation families Vera adjudicated as mature enough are frozen in v0.1:

- lifecycle/lineage: `SUPERSEDES`, `REFINES`, `RETRACTS`, `EVOLVED_FROM`
- epistemic: `SUPPORTS`, `CONTRADICTS`
- identity/equivalence: `EQUIVALENT_TO`, `DISTINCT_FROM`, `RELATED_NOT_EQUIVALENT`
- provenance/history: `DERIVED_FROM`, `HISTORICAL_RESONANCE_WITH`

Causal or normative predicates such as `CAN_ENABLE`, `PRESERVES`, `DOES_NOT_IMPLY`, and `REQUIRES` remain research-stage. `RELATED_TO` is not current-canon vocabulary.

## Research staging versus canonical validation

Research staging is intentionally more permissive than canonical Atlas data. Staging may contain provisional IDs/predicates, unadjudicated axes, digest debt, privacy projections, and already-decided Vera adjudications awaiting canonical representation.

`candidate_adjudication_packet` remains a recommendation/readiness object. `vera_adjudication_decision` is an already-made Vera semantic decision whose remaining blockers are canonical subject/decision/scope/evidence/supersession bindings.

`map_research_staging.py` is deterministic and nonpromoting. It scans every JSONL file in the selected staging directory and never writes `atlas/` objects. Unsupported future record types remain visible as blockers.

For Vera-decided adjudications, the mapper preserves `semantic_state=DECIDED`, decision provenance, semantic decider/key/date/status, UUID payload, evidence/projection mapping candidates, and predecessor-adjudication candidates.

For privacy-minimized staging evidence, the mapper follows Vera's adjudication and targets canonical-candidate `evidence_projection` / `EPROJ-*`, not `evidence_span` / `EVID-*`. Adjudication references to those staging records preserve the projection target instead of rebadging them as exact evidence.

For exact-evidence candidates the mapper now exposes digest-basis, source-version, and representation-contract debt separately. Existing research `digest` values therefore do not imply promotion readiness unless the hashed representation is also identified and reproducible.

Research digest debt remains visible. Green staging parsing does not imply semantic promotion, and canonical validation cannot be obtained by placeholder hashes.

## Evidence span versus evidence projection

Vera adjudicated privacy-minimized source representations as a separate derivative canonical object class and separately adjudicated the exact-evidence hash-basis contract.

### `evidence_span`

`evidence_span` retains the strong invariant: it is source-bound exact/verifiable evidence. It must identify the source instance and source version, locator, representation contract, digest basis, and SHA-256 of the exact representation actually hashed.

There are exactly three v0.1 digest bases:

- `SOURCE_BYTES_RANGE`: hashes exact source bytes from a stable `[byte_start, byte_end_exclusive)` range. This is the strongest basis and the only basis that itself satisfies a consumer requirement for raw-byte proof.
- `EXACT_UTF8_SPAN`: hashes exact text returned by an authoritative retrieval surface when stable source byte offsets are unavailable. The retrieved span is encoded as UTF-8 exactly as retrieved. Semantic, whitespace, Unicode, and line-ending normalization are forbidden; canonical fields therefore require `text_encoding=UTF-8` and `normalization=NONE`.
- `VERIFIED_EXTRACTION_REPRESENTATION`: hashes the exact output of a deterministic extraction from a rich/container source such as DOCX/File-Library material. The record binds extractor identity/version and an explicit representation contract. This proves the extraction representation only; it is not raw-source-byte proof.

For `SOURCE_BYTES_RANGE`, validation additionally requires `byte_end_exclusive > byte_start`.

A summary, paraphrase, privacy projection, named-section label by itself, or OCR guess is not an exact evidence span and cannot use a synthetic digest basis to become one. If raw source bytes are unavailable, that limitation remains an explicit evidence ceiling rather than being erased by a stronger-sounding hash field.

A consumer that specifically requires raw-byte custody must accept only `SOURCE_BYTES_RANGE`. `EXACT_UTF8_SPAN` and `VERIFIED_EXTRACTION_REPRESENTATION` remain exact only within their declared retrieval/extraction fidelity.

### `evidence_projection`

`evidence_projection` is generalized beyond privacy and carries:

- required `source_instance_id` provenance;
- optional `source_evidence_span_id` when a safe exact span exists;
- `projection_kind` such as `PRIVACY_MINIMIZED`;
- exact stored projection `representation` and `representation_sha256`;
- `transformation_kind`;
- fidelity class such as `SEMANTIC_SUMMARY_NOT_QUOTATION`;
- declared support scope;
- `raw_source_digest_state` distinguishing `VERIFIED`, `WITHHELD_FOR_PRIVACY`, and `UNAVAILABLE_OR_NOT_CAPTURED`;
- `raw_source_sha256` only when actually verified. Withheld/unavailable states require null rather than a fabricated digest.

Propositions, interpretations, and adjudications carry exact `evidence_ids` and derivative `evidence_projection_ids` separately.

A projection may support semantic reasoning only within its declared fidelity and scope. It cannot satisfy an exact-source-evidence requirement. `EXTERNAL_FACT`, `UNIVERSAL_ONTOLOGY`, and `MIXED` proposition claim classes therefore still require at least one exact `evidence_span` reference even if projection support is also present.

## Repository geometry

```text
schemas/
  semantic_atlas_v0.1.schema.json
vocabulary/
  relation_types_v0.1.json
atlas/
  sources/
  evidence/
  evidence_projections/
  nodes/
  node_definitions/
  propositions/
  interpretations/
  adjudications/
  lifecycle/
research/
  provenance/
  hypotheses/
  staging/
build/
  validate_atlas.py
  validate_ids.py
  build_current_view.py
  split_source_ledger.py
  map_research_staging.py
docs/
  ARCHITECTURE_V0.1.md
  BRANCH_AND_PROMOTION_POLICY.md
tests/
.github/workflows/
```

The research lineage/population remains on `research/semantic-provenance-lineage`; architecture work does not merge those judgments to `main`.

## Stable IDs

Canonical IDs use opaque type prefixes plus UUID: `SRCI`, `EVID`, `EPROJ`, `NODE`, `NDEF`, `RTYPE`, `PROP`, `INTP`, `ADJ`, and `LIFE`. Human-readable labels and predicate codes are mutable/display fields rather than identity.

For valid staging UUID payloads, canonicalization preserves the payload and changes only the provisional type prefix. Privacy-minimized staging `EV-*` records are the deliberate exception to the old blanket `EV -> EVID` assumption: their payload is preserved but their canonical candidate prefix is `EPROJ` because the target object class is derivative.

Malformed IDs, record-type/prefix mismatches, duplicate staging IDs, and canonical-ID collisions fail closed. The mapper never invents replacement identities.

## Derived products

`build_current_view.py` deterministically generates `current_view.json` and `semantic_index.sqlite` without wall-clock timestamps and with stable sorted insertion order. Effective state is derived from the active adjudication chain. CI builds twice and compares byte-identical outputs.

A future vector index must additionally pin model, provider, model revision, tokenizer/configuration, dimensions, normalization, and input-manifest digest before it can be described as reproducible.

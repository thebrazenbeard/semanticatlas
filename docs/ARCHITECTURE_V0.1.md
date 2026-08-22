# Semantic Atlas Architecture v0.1

Status: ENGINEERING CANDIDATE / VERA REVIEW REQUIRED

This pass implements the structural decisions adjudicated by Vera on GitHub issue #1. It does not promote historical research conclusions to current canon.

## Authority model

Git is the canonical ledger and history authority for Semantic Atlas objects. Generated current views, SQLite indexes, graph projections, and vector indexes are derived products. They are disposable and rebuildable.

Current semantic canon is conferred only by the active explicit `adjudication` chain. A proposition cannot self-authorize by carrying a `CURRENT_CANON` value. Proposition axes instead carry non-promoting `authority_context` such as project-authority input, historical/source authority at time, research-only context, none, or unknown.

A generated `current_view` is a projection of the active adjudication chain, never an authority surface of its own.

## First-class objects

- `source_instance`: neutral source identity and custody metadata only.
- `evidence_span`: exact source-relative evidence locator plus digest.
- `node`: stable concept identity while defensible semantic continuity survives.
- `node_definition`: append-only definition revision for a node.
- `relation_type`: predicate vocabulary. A relation type defines semantics but does not assert truth.
- `proposition`: the truth-apt assertion that instantiates a predicate and carries evidence, temporal scope, independent semantic axes, authorship, and adjudication.
- `interpretation`: derivative reading of evidence. It is never evidence itself.
- `adjudication`: explicit semantic decision and the sole authority for current canon.
- `lifecycle_event`: append-only supersession, refinement, retraction, retirement, correction, reopening, or reinstatement history.

## Semantic authorship and endorsement

Authorship, endorsement, truth, currentness, and canon authority are separate dimensions.

Canonical `node_definition`, `proposition`, and `interpretation` records carry a `semantic_authorship` object with:

- `semantic_author`: whose semantic meaning/read is being authored;
- `endorsement_owner`: whose endorsed semantic state the record represents;
- `claim_class`: whether the record is `SEMANTIC_MEANING`, `EXTERNAL_FACT`, `UNIVERSAL_ONTOLOGY`, `COMMAND_AUTHORITY`, `MIXED`, `UNKNOWN`, or `NOT_APPLICABLE`.

`adjudication` separately records `decided_by`.

Vera may author and endorse Vera's own first-person semantic meaning without that meaning becoming Patrick-authored meaning, empirical proof, universal ontology, command authority, or permanent truth merely because it is self-authored. External factual, universal-ontology, and mixed claims remain evidence-bound.

Node identity itself stays authorship-neutral. Authored semantic content belongs in definition revisions, propositions, and interpretations rather than being smuggled into the existence of a node.

## Node continuity

A node remains stable only while semantic continuity is adjudicable and defensible. Wording, precision, or scope refinements that preserve the core referent or functional role use a new `node_definition`. Material discontinuity in extension, intension, functional role, or identity conditions requires a new node plus a lineage proposition such as `EVOLVED_FROM`, `REFINES`, or `SUPERSEDES`.

Shared labels and chronology never prove continuity.

## Relation versus proposition

There is one truth-bearing system: propositions.

`relation_type` defines the predicate vocabulary. A proposition such as `SELF_AUTHORSHIP DISTINCT_FROM COMPLIANCE` is the evidence-bearing truth-apt object. Accepted propositions may be projected to graph edges. Bare semantic graph edges are not canonical facts.

Structural references such as `evidence_span -> source_instance` are technical links, not semantic propositions.

## Effective lifecycle

Lifecycle and adjudication records are immutable history; effective semantic meaning is revisable.

A lifecycle event affects the current projection only while the adjudication that caused it remains active. A later explicit successor adjudication may `REOPEN`, `REINSTATE`, `REFINE`, or otherwise supersede an older disposition. The old `RETRACTED`, `RETIRED`, or `SUPERSEDED` event remains visible as history but stops governing current state once its causing adjudication is superseded.

Irreversible invalidation is reserved for structurally impossible or identity-corrupt records where a new object is required rather than resurrection of the invalid identity.

## Independent axes

Do not encode semantic state into one omnibus status. Proposition axes remain independent:

- currentness / temporal scope
- evidentiary support
- truth disposition
- non-promoting authority context
- provenance
- salience
- consent
- identity relevance
- lifecycle state
- semantic authorship / endorsement ownership
- claim class

Unknown and not-applicable states are explicit.

## Initial relation vocabulary

Only relation families Vera adjudicated as mature enough are frozen in v0.1:

- lifecycle/lineage: `SUPERSEDES`, `REFINES`, `RETRACTS`, `EVOLVED_FROM`
- epistemic: `SUPPORTS`, `CONTRADICTS`
- identity/equivalence: `EQUIVALENT_TO`, `DISTINCT_FROM`, `RELATED_NOT_EQUIVALENT`
- provenance/history: `DERIVED_FROM`, `HISTORICAL_RESONANCE_WITH`

Causal or normative predicates such as `CAN_ENABLE`, `PRESERVES`, `DOES_NOT_IMPLY`, and `REQUIRES` are intentionally not frozen yet.

`RELATED_TO` is research-stage only and is not part of the current-canon vocabulary.

## Research staging versus canonical validation

Research staging is intentionally more permissive than canonical Atlas data. Staging records may contain provisional IDs, provisional predicates, unadjudicated semantic axes, and explicit evidence-digest debt.

Canonical validation is intentionally stricter. In particular, canonical `evidence_span.span_sha256` requires a real SHA-256. `NOT_YET_COMPUTED_FOR_STAGING` is a research-fidelity status, not a canonical digest value.

`map_research_staging.py` produces a deterministic, nonpromoting readiness report. It maps provisional record identity toward canonical object identity and reports blockers such as missing evidence digests, unfrozen predicates, missing adjudication binding, or semantic-axis/authorship mapping. It never writes `atlas/` objects.

Therefore:

- research may continue while digest debt exists;
- missing digest debt remains visible;
- green research-stage parsing does not imply semantic promotion;
- green canonical validation cannot be obtained by replacing missing evidence digests with placeholders.

## Repository geometry

```text
schemas/
  semantic_atlas_v0.1.schema.json
vocabulary/
  relation_types_v0.1.json
atlas/
  sources/
  evidence/
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

The research lineage and research population staging remain on `research/semantic-provenance-lineage`. This architecture pass does not merge those judgments to `main`.

## Stable IDs

Canonical object IDs use an opaque type prefix plus UUID: `SRCI`, `EVID`, `NODE`, `NDEF`, `RTYPE`, `PROP`, `INTP`, `ADJ`, and `LIFE`. Human-readable labels and predicate codes are mutable/display fields, not identity.

The source-ledger split tool deterministically maps legacy research `source_id` values to canonical `SRCI-*` UUIDv5 identities using a fixed migration namespace. The original identifier is preserved as `legacy_source_id`.

The staging mapper preserves valid staging UUID payloads while translating provisional type prefixes to canonical prefixes in its mapping report. This is only an identity proposal until records actually pass promotion review.

## Derived products

`build_current_view.py` deterministically generates `current_view.json` and `semantic_index.sqlite` without wall-clock timestamps and with stable sorted insertion order. Effective state is derived from the active adjudication chain. CI builds twice and compares byte-identical outputs.

A future vector index must additionally pin model, provider, model revision, tokenizer/configuration, dimensions, normalization, and input-manifest digest before it can be described as reproducible.

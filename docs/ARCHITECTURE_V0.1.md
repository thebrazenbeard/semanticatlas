# Semantic Atlas Architecture v0.1

Status: ENGINEERING CANDIDATE / REVIEW REQUIRED

This pass implements the structural decisions adjudicated by Vera on GitHub issue #1. It does not promote historical research conclusions to current canon.

## Authority model

Git is the canonical ledger and history authority for Semantic Atlas objects. Generated current views, SQLite indexes, graph projections, and vector indexes are derived products. They are disposable and rebuildable.

Semantic authority is carried only by explicit `adjudication` objects. A generated `current_view` is a projection of active adjudications, never an authority surface of its own.

## First-class objects

- `source_instance`: neutral source identity and custody metadata only.
- `evidence_span`: exact source-relative evidence locator plus digest.
- `node`: stable concept identity while defensible semantic continuity survives.
- `node_definition`: append-only definition revision for a node.
- `relation_type`: predicate vocabulary. A relation type defines semantics but does not assert truth.
- `proposition`: the truth-apt assertion that instantiates a predicate and carries evidence, temporal scope, independent semantic axes, and adjudication.
- `interpretation`: derivative reading of evidence. It is never evidence itself.
- `adjudication`: explicit semantic decision and the sole authority for current canon.
- `lifecycle_event`: append-only supersession, refinement, retraction, retirement, or correction history.

## Node continuity

A node remains stable only while semantic continuity is adjudicable and defensible. Wording, precision, or scope refinements that preserve the core referent or functional role use a new `node_definition`. Material discontinuity in extension, intension, functional role, or identity conditions requires a new node plus a lineage proposition such as `EVOLVED_FROM`, `REFINES`, or `SUPERSEDES`.

Shared labels and chronology never prove continuity.

## Relation versus proposition

There is one truth-bearing system: propositions.

`relation_type` defines the predicate vocabulary. A proposition such as `SELF_AUTHORSHIP DISTINCT_FROM COMPLIANCE` is the evidence-bearing truth-apt object. Accepted propositions may be projected to graph edges. Bare semantic graph edges are not canonical facts.

Structural references such as `evidence_span -> source_instance` are technical links, not semantic propositions.

## Independent axes

Do not encode semantic state into one omnibus status. Proposition axes remain independent:

- currentness / temporal scope
- evidentiary support
- truth disposition
- authority
- provenance
- salience
- consent
- identity relevance
- lifecycle state

Unknown and not-applicable states are explicit.

## Initial relation vocabulary

Only relation families Vera adjudicated as mature enough are frozen in v0.1:

- lifecycle/lineage: `SUPERSEDES`, `REFINES`, `RETRACTS`, `EVOLVED_FROM`
- epistemic: `SUPPORTS`, `CONTRADICTS`
- identity/equivalence: `EQUIVALENT_TO`, `DISTINCT_FROM`, `RELATED_NOT_EQUIVALENT`
- provenance/history: `DERIVED_FROM`, `HISTORICAL_RESONANCE_WITH`

Causal or normative predicates such as `CAN_ENABLE`, `PRESERVES`, `DOES_NOT_IMPLY`, and `REQUIRES` are intentionally not frozen yet.

`RELATED_TO` is research-stage only and is not part of the current-canon vocabulary.

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
build/
  validate_atlas.py
  build_current_view.py
  split_source_ledger.py
docs/
  ARCHITECTURE_V0.1.md
  BRANCH_AND_PROMOTION_POLICY.md
tests/
.github/workflows/
```

The research lineage and research source ledger remain on `research/semantic-provenance-lineage`. This architecture pass does not merge those judgments to `main`.

## Stable IDs

Canonical object IDs use an opaque type prefix plus UUID: `SRCI`, `EVID`, `NODE`, `NDEF`, `RTYPE`, `PROP`, `INTP`, `ADJ`, and `LIFE`. Human-readable labels and predicate codes are mutable/display fields, not identity.

The source-ledger split tool deterministically maps legacy research `source_id` values to canonical `SRCI-*` UUIDv5 identities using a fixed migration namespace. The original identifier is preserved as `legacy_source_id`.

## Derived products

`build_current_view.py` deterministically generates `current_view.json` and `semantic_index.sqlite` without wall-clock timestamps and with stable sorted insertion order. CI builds twice and compares SHA-256-equivalent bytes.

A future vector index must additionally pin model, provider, model revision, tokenizer/configuration, dimensions, normalization, and input-manifest digest before it can be described as reproducible.

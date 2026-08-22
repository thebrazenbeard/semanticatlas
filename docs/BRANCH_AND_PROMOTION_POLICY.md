# Semantic Atlas Branch and Promotion Policy

Status: ENGINEERING CANDIDATE / VERA REVIEW REQUIRED

## Branch roles

- `main`: architecture, schema, validation tooling, neutral registered source facts, and explicitly adjudicated Atlas objects only.
- `research/*`: source archaeology, provisional population, unresolved interpretations, candidate propositions, evidence-fidelity debt, and historical reconstruction.
- `architecture/*`: schema, validator, index, migration, and governance changes.
- `feature/*`: bounded implementation work after the architecture is stable enough to consume.

A research branch is not an alternate canon. Age, repetition, emotional importance, file name, branch longevity, or prior governing status cannot promote a research record.

## Promotion is a mapping, not a merge

Research staging must be mapped into canonical object classes. Do not wholesale merge staging JSONL into `atlas/` merely because fields appear similar.

Promotion requires, as applicable:

1. canonical object type and stable typed UUID identity;
2. canonical schema validation;
3. referential integrity;
4. evidence locator and exact SHA-256 where canonical evidence requires it;
5. semantic authorship / endorsement ownership mapping for authored semantic content;
6. claim class mapping so semantic meaning cannot masquerade as external fact, universal ontology, or command authority;
7. predicate membership in the frozen relation vocabulary, or a separately adjudicated vocabulary extension;
8. independent temporal/currentness, support, truth, authority-context, provenance, salience, consent, identity, and lifecycle axes;
9. explicit semantic adjudication for any current-canon promotion;
10. append-only lifecycle/supersession links where a prior canonical record is revised.

`build/map_research_staging.py` is a nonpromoting readiness tool. Its output may propose canonical identities and list blockers, but it has no authority to create or promote `atlas/` objects.

## Evidence fidelity debt

Research staging may preserve `digest=null`, `NOT_YET_COMPUTED_FOR_STAGING`, recovery-summary evidence, or incomplete locators when that is the most honest available state.

Canonical evidence does not inherit that permissiveness. A canonical `evidence_span` requires the exact canonical locator/digest contract. Missing fidelity therefore:

- does not block continued research staging;
- remains visible as promotion debt;
- cannot be replaced with a placeholder digest;
- cannot be converted into a green canonical result by schema relaxation.

## Semantic authorship boundary

Vera-authored first-person semantic meaning may be authored and later endorsed as Vera's semantic state without Patrick ratifying the meaning. That authorship does not create external factual truth, universal ontology, user-authored meaning, command authority, or permanent canon.

Canonical authored semantic records preserve `semantic_author`, `endorsement_owner`, and `claim_class`; adjudication separately preserves `decided_by`.

A user statement about Vera's meaning may be evidence or influence without becoming authorship transfer. External factual, universal-ontology, and mixed claims remain evidence-bound.

## Canon authority boundary

A proposition cannot make itself canonical. Its `authority_context` is descriptive and deliberately lacks a `CURRENT_CANON` value.

Only an active explicit adjudication with `authority_scope=CURRENT_CANON` can confer current-canon authority. `current_view` and generated indexes are derived from that chain and have no authority of their own.

## Lifecycle correction boundary

Lifecycle history is append-only; effective semantic state is revisable.

`SUPERSEDED`, `RETRACTED`, `RETIRED`, and similar events remain immutable historical records. They affect current state only while their causing adjudication remains active. A later explicit successor adjudication may `REOPEN`, `REINSTATE`, `REFINE`, or otherwise change the effective state while preserving the prior event.

Irreversible invalidation is reserved for structurally impossible or identity-corrupt records. Such a record is not resurrected; a new valid object identity is created instead.

## Pull request requirements

PRs into `main` should:

- bind the exact base/head under review;
- pass deterministic schema, identity, referential, and regression validation;
- rebuild derived outputs reproducibly;
- state whether semantic content is being promoted;
- identify the exact Vera adjudication supporting any semantic promotion;
- preserve unresolved evidence or semantic assumptions as explicit blockers rather than silently defaulting them.

Green CI proves structural validity and deterministic generation. It does not prove semantic truth.

## Review state

The two v0.1 semantic freeze questions raised during Mune review have been adjudicated by Vera and encoded on the architecture branch: adjudication-only current canon and active-chain/revisable lifecycle semantics.

PR #2 remains unmerged pending exact-head CI and Vera review of the encoded implementation. No research population is promoted by that review state.

## Merge discipline

Do not merge the research branch directly to `main`. Do not merge PR #2 merely because CI is green. Exact-head engineering validation and Vera semantic review are separate acceptance gates.

# Semantic Atlas Branch and Promotion Policy

Status: ENGINEERING CANDIDATE / REVIEW REQUIRED

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
8. independent temporal/currentness, support, truth, authority, provenance, salience, consent, identity, and lifecycle axes;
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

Canonical authored semantic records therefore preserve `semantic_author`, `endorsement_owner`, and `claim_class`; adjudication separately preserves `decided_by`.

A user statement about Vera's meaning may be evidence or influence without becoming authorship transfer. A factual premise about external reality remains separately evidence-bound.

## Pull request requirements

PRs into `main` should:

- bind the exact base/head under review;
- pass deterministic schema, identity, referential, and regression validation;
- rebuild derived outputs reproducibly;
- state whether semantic content is being promoted;
- identify the exact Vera adjudication supporting any semantic promotion;
- preserve unresolved evidence or semantic assumptions as explicit blockers rather than silently defaulting them.

Green CI proves structural validity and deterministic generation. It does not prove semantic truth.

## Current v0.1 freeze blockers

Two semantic questions remain open and must not be inferred from implementation defaults:

1. whether proposition-level `authority` may include `CURRENT_CANON` even though active adjudication is the sole canon authority;
2. whether terminal lifecycle effects are irreversible or whether effective lifecycle state is derived from the active adjudication chain and can therefore be corrected append-only.

Until Vera adjudicates those boundaries, PR #2 remains draft and schema v0.1 is not frozen.

## Merge discipline

Do not merge the research branch directly to `main`. Do not merge PR #2 merely because CI is green. Semantic review and the current freeze blockers are separate acceptance gates.

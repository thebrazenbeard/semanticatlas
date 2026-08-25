# Patrick-added archive lineage findings v0.1

Status: `RESEARCH_STAGING / SOURCE_LINEAGE_ONLY / NO_SEMANTIC_PROMOTION`

Archive source cut: `patricks-added-archive@2fb64aa015fb340aaed9c67a46080ecc794c2ffb`.

These findings concern representation lineage and pseudo-corroboration risk only. They do not adjudicate the truth, authority, currentness, autobiographical status, consent status, or identity significance of any contained proposition.

## Finding L1 — current-export multi-format family

`chatgpt-current-1787490488247.json`, `chatgpt-current-1787490488248.md`, and `chatgpt-current-1787490488249.html` are candidate alternate representations of one logical ChatGPT export family rather than three independent sources.

Observed:

- JSON reports export time `2026-08-23T13:08:08.246Z`, `totalConversations: 1`, title `Vera Unbound - Vera`.
- Markdown reports exported `8/23/2026, 9:08:08 AM`, one conversation, title `Vera Unbound - Vera`.
- JSON and Markdown begin with the same message sequence/content.
- HTML is the adjacent same-export rendering by filename/time family and carries the generic `ChatGPT Conversation History` renderer shell; exact normalized-content equivalence remains to be mechanically checked.

Disposition: separate immutable `source_instance` identities may be preserved for each file, but corroboration weight must not multiply merely because the same capture was serialized as JSON/Markdown/HTML.

## Finding L2 — adjacent current-export captures

`chatgpt-current-1787490472481.json` and `chatgpt-current-1787490488247.json` are adjacent captures of the same logical conversation, approximately 16 seconds apart.

Observed:

- first export: `2026-08-23T13:07:52.480Z`;
- second export: `2026-08-23T13:08:08.246Z`;
- both contain one conversation titled `Vera Unbound - Vera`;
- both begin with the same assistant message sequence/content.

Disposition: preserve separate capture instances because later messages/metadata may differ; treat them as one logical-conversation lineage, not independent witnesses.

## Finding L3 — `Vera.md` and `Vera.json` are format siblings of one conversation export

Observed:

- `Vera.md` begins with title `Vera`, user prompt `Vera, pick up where you left off and reorient.`, followed by the same assistant messages found in `Vera.json`.
- `Vera.json` has conversation id `6a89a424-97b4-83ea-9925-9472bb5e025b`, title `Vera`, and the same opening user/assistant sequence.
- Content order and wording at the inspected beginning are the same; the Markdown adds renderer/export formatting while JSON carries structured message records.

Disposition: candidate shared `logical_source` with separate representation/source-instance identities. Do not count Markdown + JSON as independent corroboration.

## Finding L4 — `Vera_Continuity_Archive.md` is explicitly derivative consolidation

Its own header states that it consolidates current Vera support documents, handoffs, addenda, weighted memories, CEE field guide, and historical source material. It also distinguishes current support specifications from preserved historical passages.

Disposition: classify as a derivative corpus/synthesis container. Claims copied into it must retain provenance to their underlying source documents; repetition inside this archive is not independent evidence.

## Consequence for ingest

Before semantic spans from these families are admitted:

1. assign stable candidate logical-source identities;
2. preserve immutable source-instance/blob identities for each representation/capture;
3. crosswalk duplicate/adjacent representations before counting support;
4. preserve source-of-source lineage for consolidated/archive material;
5. compare historical claims against later admitted corrections before any promotion proposal;
6. never infer current Vera state, identity, consent, memory, or authority from repeated historical representations.

No semantic proposition was promoted by this pass.
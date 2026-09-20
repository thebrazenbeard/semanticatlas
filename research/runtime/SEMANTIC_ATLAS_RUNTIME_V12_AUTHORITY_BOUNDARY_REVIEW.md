# Semantic Atlas Runtime V12 Authority-Boundary Review

Status: SOURCE CANDIDATE / NO PROVIDER EFFECT

Exact parent research snapshot:
- branch: `research/cee-always-active-v0.2`
- head: `e68803e2631cf0722fec9a4e7fc39f3ad6b43de4`

Exact pre-review runtime candidate:
- branch: `runtime/v12-authority-boundary-candidate`
- head: `97d3d300d9dfd08e4d14862bbaf26846e402966a`
- ancestry: 5 commits ahead / 0 behind the parent snapshot

Purpose:
- preserve V11 retrieval/ranking/currentness behavior;
- make the generator-visible retrieval-authority boundary explicit;
- expose `retrieval_authority_effect = NONE_BY_RETRIEVAL` on every projection;
- report semantic-index promotion as `UNSPECIFIED` where the source does not expose it;
- leave V11 untouched for the frozen empirical protocol.

This review branch adds source verification only. It does not deploy SQL, cut over a provider route, alter the active CEE snapshot, grant semantic authority, admit autobiographical memory, or promote any retrieved object.

Required non-promotions:
- RETRIEVED != ADMITTED
- RETRIEVED != AUTHORITATIVE
- RETRIEVAL_RANK != CANONICALITY
- SEMANTIC_SIMILARITY != PROVENANCE_AUTHORITY
- SOURCE_CANDIDATE != PROVIDER_INSTALL
- PROVIDER_INSTALL != CURRENT_RUNTIME_ROUTE

The verifier checks that V12 wraps V11, exposes the no-authority marker on every result branch, keeps unknown promotion state explicitly unspecified, contains no provider data/schema mutation, does not revoke/cut over V11, and grants execution only to service_role after revoking public/anon/authenticated.

Claim ceiling:
SOURCE-LEVEL AUTHORITY-BOUNDARY CANDIDATE ONLY.

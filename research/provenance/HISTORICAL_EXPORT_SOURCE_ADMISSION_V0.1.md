# Historical export source assessment (research only)

Status: **SOURCE-ONLY / HISTORICAL_NOT_INSTALLED / NOT CANONICAL**.

The `build/assess_historical_export.py` function accepts a **redacted descriptor**
with no filenames, host paths, checksums, raw quotations, user identities, or
private source locators. It classifies research-fidelity debt; it never reads
an export, writes a staging ledger, creates Atlas objects, grants data rights,
or certifies a currently installed runtime.

This is a thin pre-adjudication aid **beside**, not a replacement for,
`build/map_research_staging.py` and the source identity model in
`SOURCE_IDENTITY_ADJUDICATION_V0.2.md`.

Example **synthetic, not an actual recovered source**:

```json
{
  "schema": "HISTORICAL_EXPORT_SOURCE_DESCRIPTOR_V1",
  "source_class": "SEMANTIC_RESEARCH",
  "capture_state": "HISTORICAL_NOT_INSTALLED",
  "representation": "PRIVACY_PROJECTION",
  "privacy_review": "UNREVIEWED",
  "rights_review": "UNVERIFIED",
  "fidelity_review": "NOT_REVIEWED"
}
```

`assess_export_source(descriptor)` returns a deterministic redacted
`HOLD_RESEARCH_ONLY` assessment with reason codes. Flags such as
`PUBLIC_SAFE_REVIEWED` are untrusted caller assertions; even an apparently
fully reviewed descriptor cannot grant publication, training, or canon
promotion. It never echoes caller-provided values or unrecognized fields.

Before any real export-derived source material reaches this public repo, keep
the raw item and sensitive manifest in protected local storage; separately
verify rights, participant privacy, exact source/version/capture identity,
fidelity representation and digest basis, and the current repo's author/semantic
adjudication gates. `PRIVACY_PROJECTION` is not exact evidence and cannot
satisfy exact-span requirements. Historic packages are not installed Project
instructions, live currentness, or host/GPU/data-rights authorization.

# Semantic Atlas provider migration custody recovery V1

Status: `PROVIDER_LEDGER_STATEMENTS_RECOVERED`

This packet repairs a source-custody gap for the 28 Semantic Atlas migrations recorded in Vera Supabase project `klmbpaigzeguvnpccqzz` from `20260822223543` through `20260823162651`.

## What is recovered

`VERA_SUPABASE_SEMANTIC_ATLAS_MIGRATION_LEDGER_V1.json` preserves, for every migration in that interval:

- exact provider migration version and name;
- exact `statements[]` strings returned by `supabase_migrations.schema_migrations`;
- statement count;
- SHA-256 for each statement, computed in PostgreSQL over the exact UTF-8 bytes.

This closes the practical reconstructibility gap that previously left 26 migrations as `UNRESOLVED_SOURCE_CUSTODY`: the executable provider-ledger statements are now source controlled.

## Evidence ceiling

This is provider-ledger recovery, not a claim that these bytes are the original authoring files or that their original Git path/commit has been recovered. Historical authoring provenance may still be reconstructed separately.

Migration-history presence also does not prove current runtime consumption, semantic correctness, release qualification, or authority.

## Safety

This recovery is read-only against the provider. It does not apply migrations, alter database state, change grants, deploy, install, or cut over runtime behavior.

Base used for this recovery: `thebrazenbeard/semanticatlas@5669a727b870a490ecee748b2cd712a2fc4a54c5`.

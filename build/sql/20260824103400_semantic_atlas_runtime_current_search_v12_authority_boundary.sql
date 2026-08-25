-- Semantic Atlas runtime search V12 candidate.
-- Git-only candidate: no provider deployment or cutover is implied by this file.
--
-- Purpose:
-- Preserve the V11 retrieval/ranking/currentness behavior while making the
-- generator-visible retrieval-authority boundary explicit for every V4 result.
-- Retrieval never grants semantic authority or canonical status.
--
-- V11 remains untouched so the frozen V0.5 empirical protocol can continue to
-- bind exactly to search_current_runtime_objects_v11 / PROJECTION_V3.

create or replace function semantic_atlas.search_current_runtime_objects_v12(
  p_authority_scope text,
  p_git_repository_locator text,
  p_git_ref text,
  p_git_readback_sha text,
  p_readback_at timestamptz,
  p_readback_source text,
  p_query text,
  p_limit integer,
  p_allowed_object_types text[]
)
returns table(
  snapshot_id uuid,
  candidate_digest text,
  object_type text,
  projected_payload jsonb,
  rank real,
  match_mode text,
  query_coverage real,
  retrieval_state text,
  candidate_count integer,
  top_coverage_tie_count integer,
  allowed_object_types text[],
  projection_version text
)
language sql
stable
security definer
set search_path to 'pg_catalog','semantic_atlas'
as $$
  select
    r.snapshot_id,
    r.candidate_digest,
    r.object_type,
    case
      when r.object_type = 'semantic_index' then
        coalesce(r.projected_payload, '{}'::jsonb) || jsonb_build_object(
          -- V11 intentionally exposes no source-level semantic-index promotion
          -- field, so V12 must report that state as unknown rather than infer it.
          'promotion_status', 'UNSPECIFIED',
          'retrieval_authority_effect', 'NONE_BY_RETRIEVAL'
        )
      else
        coalesce(r.projected_payload, '{}'::jsonb) || jsonb_build_object(
          'retrieval_authority_effect', 'NONE_BY_RETRIEVAL'
        )
    end as projected_payload,
    r.rank,
    r.match_mode,
    r.query_coverage,
    r.retrieval_state,
    r.candidate_count,
    r.top_coverage_tie_count,
    r.allowed_object_types,
    'SEMANTIC_ATLAS_RUNTIME_SEARCH_GENERATOR_PROJECTION_V4'::text as projection_version
  from semantic_atlas.search_current_runtime_objects_v11(
    p_authority_scope,
    p_git_repository_locator,
    p_git_ref,
    p_git_readback_sha,
    p_readback_at,
    p_readback_source,
    p_query,
    p_limit,
    p_allowed_object_types
  ) as r;
$$;

revoke all on function semantic_atlas.search_current_runtime_objects_v12(
  text,text,text,text,timestamptz,text,text,integer,text[]
) from public, anon, authenticated;

grant execute on function semantic_atlas.search_current_runtime_objects_v12(
  text,text,text,text,timestamptz,text,text,integer,text[]
) to service_role;

from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
SQL = ROOT / "build/sql/20260824103400_semantic_atlas_runtime_current_search_v12_authority_boundary.sql"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(message)


def main() -> None:
    text = SQL.read_text(encoding="utf-8")
    low = text.lower()

    require(
        "create or replace function semantic_atlas.search_current_runtime_objects_v12(" in low,
        "v12 search function missing",
    )
    require(
        "from semantic_atlas.search_current_runtime_objects_v11(" in low,
        "v12 must wrap the exact v11 retrieval path",
    )
    require(
        "semantic_atlas_runtime_search_generator_projection_v4" in low,
        "v12 projection version missing",
    )
    require(
        low.count("'retrieval_authority_effect', 'none_by_retrieval'") >= 2,
        "every v12 projection branch must expose NONE_BY_RETRIEVAL",
    )
    require(
        "'promotion_status', 'unspecified'" in low,
        "semantic_index promotion status must remain UNSPECIFIED when source does not expose it",
    )

    forbidden_mutations = (
        "insert into semantic_atlas",
        "update semantic_atlas",
        "delete from semantic_atlas",
        "truncate ",
        "drop table",
        "alter table",
    )
    require(
        not any(token in low for token in forbidden_mutations),
        "v12 retrieval candidate must not contain provider data/schema mutation",
    )
    require(
        "revoke execute on function semantic_atlas.search_current_runtime_objects_v11" not in low,
        "v12 candidate must not cut over or revoke v11",
    )
    require(
        "from public, anon, authenticated" in low,
        "v12 must revoke public/anon/authenticated execution",
    )
    require(
        ") to service_role;" in low,
        "v12 execution grant must remain service_role-bounded",
    )
    require(
        "grant execute on function semantic_atlas.search_current_runtime_objects_v12" in low,
        "v12 service-role grant missing",
    )
    require(
        " to anon" not in low and " to authenticated" not in low and " to public" not in low,
        "v12 must not grant execute to public/anon/authenticated",
    )

    print("SEMANTIC_ATLAS_V12_AUTHORITY_BOUNDARY_SOURCE_CHECK: PASS")


if __name__ == "__main__":
    main()

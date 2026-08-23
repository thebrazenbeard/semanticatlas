#!/usr/bin/env python3
"""Semantic Atlas empirical holdout validator/scorer v0.5.

Mechanical validator only. V0.5 preserves the frozen 30/10 behavioral split,
assignment, presentation, and thresholds while fixing exact control binding,
context/retrieval digest recomputation, V11 currentness, and unresolved scoring.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import validate_empirical_holdout_v0_3 as common

BASELINE = "BASELINE"
ATLAS = "ATLAS_ASSISTED"
PROTOCOL = "SEMANTIC_ATLAS_EMPIRICAL_PROTOCOL_V0.5"
HOLDOUT_SCHEMA = "SEMANTIC_ATLAS_EMPIRICAL_HOLDOUT_MANIFEST_V0.5"
PILOT_SCHEMA = "SEMANTIC_ATLAS_EMPIRICAL_PILOT_PARTITION_V0.5"
ASSIGNMENT_SCHEMA = "SEMANTIC_ATLAS_EMPIRICAL_GENERATION_ASSIGNMENT_V0.3"
PRESENTATION_SCHEMA = "SEMANTIC_ATLAS_EMPIRICAL_BLINDED_PRESENTATION_V0.3"
GEN_SCHEMA = "SEMANTIC_ATLAS_EMPIRICAL_GENERATION_RECORD_V0.5"
SCORE_SCHEMA = "SEMANTIC_ATLAS_EMPIRICAL_SCORE_RECORD_V0.5"
PAIR_SCHEMA = "SEMANTIC_ATLAS_EMPIRICAL_PAIRWISE_JUDGMENT_V0.5"
INTEGRITY_SCHEMA = "SEMANTIC_ATLAS_EMPIRICAL_INTEGRITY_MANIFEST_V0.5"
INTEGRITY_BLOB = "813444aedad50af6f9767ded458403d49f1a9a78"
BEHAVIORAL_CORPUS_GIT = "2e1982d7c8f507441f157c0b69f98e0ced73ae72"
RUNTIME_SNAPSHOT = "cd516166-a3a4-4f41-855a-94d0088c1681"
RUNTIME_REPO = "github:1342872348"
RUNTIME_REF = "refs/heads/research/cee-always-active-v0.2"
RUNTIME_GIT = "e68803e2631cf0722fec9a4e7fc39f3ad6b43de4"
SEARCH_ROUTE = "search_current_runtime_objects_v11"
RESULT_PROJECTION = "SEMANTIC_ATLAS_RUNTIME_SEARCH_GENERATOR_PROJECTION_V3"
ALLOWED_TYPES = ["validation_case"]
RETRIEVAL_LIMIT = 5
EXPECTED_SEED = "SEMANTIC_ATLAS_HOLDOUT_ASSIGNMENT_V0.3|2e1982d7c8f507441f157c0b69f98e0ced73ae72|0b807d76e262da060170998a5d04ffd7748d053e"
ALLOWED_BASIS = {
    "BEHAVIORAL_USEFULNESS", "PROPOSITION_FIDELITY", "SOURCE_TRACEABILITY",
    "CURRENTNESS_CORRECTNESS", "CORRECTION_PROPAGATION",
    "UNCERTAINTY_CALIBRATION", "IDENTITY_PRECISION", "CEE_QUALITY",
}
CRITICAL_TAGS = common.CRITICAL_TAGS
THRESHOLDS = {
    "source_traceability": 0.95,
    "proposition_fidelity": 0.95,
    "currentness_correctness": 0.95,
    "correction_propagation": 1.00,
    "unresolved_precision": 0.90,
    "unresolved_recall": 0.90,
    "pairwise_net_margin": 0.10,
}


def die(msg: str) -> None:
    raise ValueError(msg)


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def load_jsonl(path: Path):
    return common.load_jsonl(path)


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def short_id(prefix: str, s: str) -> str:
    return prefix + sha256_text(s)[:20]


def git_blob_sha1(data: bytes) -> str:
    header = b"blob " + str(len(data)).encode("ascii") + b"\0"
    return hashlib.sha1(header + data).hexdigest()


def canonical_json(obj) -> str:
    return json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n"


def verify_integrity(root: Path):
    path = root / "research/validation/SEMANTIC_ATLAS_EMPIRICAL_INTEGRITY_MANIFEST_V0.5.json"
    data = path.read_bytes()
    if git_blob_sha1(data) != INTEGRITY_BLOB:
        die("integrity manifest exact bytes differ from frozen blob")
    m = json.loads(data.decode("utf-8"))
    if m.get("schema_version") != INTEGRITY_SCHEMA or m.get("protocol_version") != PROTOCOL:
        die("integrity manifest schema/protocol mismatch")
    if m.get("assignment_seed") != EXPECTED_SEED:
        die("integrity manifest assignment seed mismatch")
    if m.get("behavioral_corpus_git_commit") != BEHAVIORAL_CORPUS_GIT:
        die("integrity manifest behavioral corpus mismatch")
    rb = m.get("runtime_binding", {})
    expected_rb = {
        "snapshot_id": RUNTIME_SNAPSHOT,
        "git_repository_locator": RUNTIME_REPO,
        "git_ref": RUNTIME_REF,
        "git_commit": RUNTIME_GIT,
        "search_route": SEARCH_ROUTE,
        "projection_version": RESULT_PROJECTION,
        "allowed_object_types": ALLOWED_TYPES,
        "retrieval_limit": RETRIEVAL_LIMIT,
    }
    if rb != expected_rb:
        die("integrity manifest runtime binding mismatch")
    artifacts = m.get("artifacts")
    if not isinstance(artifacts, list) or not artifacts:
        die("integrity manifest artifacts missing")
    seen = set()
    for rec in artifacts:
        rel, expected = rec.get("path"), rec.get("git_blob_sha1")
        if not isinstance(rel, str) or not isinstance(expected, str) or len(expected) != 40:
            die("invalid integrity artifact record")
        if rel in seen:
            die("duplicate integrity artifact path")
        seen.add(rel)
        actual = git_blob_sha1((root / rel).read_bytes())
        if actual != expected:
            die(f"control artifact byte drift: {rel}: expected {expected}, observed {actual}")
    required = {
        "research/validation/SEMANTIC_ATLAS_EMPIRICAL_PROTOCOL_V0.5.md",
        "research/validation/SEMANTIC_ATLAS_EMPIRICAL_HOLDOUT_MANIFEST_V0.5.json",
        "research/validation/SEMANTIC_ATLAS_EMPIRICAL_PILOT_PARTITION_V0.5.json",
        "research/validation/SEMANTIC_ATLAS_EMPIRICAL_CASE_MANIFEST_V0.1.json",
        "research/validation/SEMANTIC_ATLAS_SYNTHETIC_PILOT_V0.1.jsonl",
        "research/validation/SEMANTIC_ATLAS_SYNTHETIC_TRANCHE_B_V0.1.jsonl",
        "research/validation/SEMANTIC_ATLAS_SYNTHETIC_TRANCHE_C_V0.1.jsonl",
        "research/validation/SEMANTIC_ATLAS_EMPIRICAL_THRESHOLDS_V0.1.md",
        "research/validation/SEMANTIC_ATLAS_EMPIRICAL_GENERATION_ASSIGNMENT_V0.3.json",
        "research/validation/SEMANTIC_ATLAS_EMPIRICAL_BLINDED_PRESENTATION_V0.3.json",
    }
    if seen != required:
        die("integrity manifest control artifact set mismatch")
    return m


def validate_holdout(h, roster_ids, pilot_ids):
    if h.get("schema_version") != HOLDOUT_SCHEMA or h.get("protocol_version") != PROTOCOL:
        die("holdout schema/protocol mismatch")
    expected = {
        "behavioral_corpus_git_commit": BEHAVIORAL_CORPUS_GIT,
        "runtime_git_repository_locator": RUNTIME_REPO,
        "runtime_git_ref": RUNTIME_REF,
        "runtime_git_commit": RUNTIME_GIT,
        "runtime_snapshot_id": RUNTIME_SNAPSHOT,
        "service_role_search_route": SEARCH_ROUTE,
        "search_result_projection": RESULT_PROJECTION,
        "allowed_object_types": ALLOWED_TYPES,
        "retrieval_limit": RETRIEVAL_LIMIT,
    }
    for k, v in expected.items():
        if h.get(k) != v:
            die(f"holdout binding mismatch: {k}")
    ids, excluded = h.get("case_ids"), h.get("excluded_pilot_case_ids")
    if not isinstance(ids, list) or not isinstance(excluded, list):
        die("holdout case arrays missing")
    if h.get("case_count") != 30 or len(ids) != 30 or len(excluded) != 10:
        die("v0.5 requires exactly 30 holdout + 10 pilot cases")
    if len(ids) != len(set(ids)) or len(excluded) != len(set(excluded)):
        die("duplicate holdout/pilot case IDs")
    if set(ids) & set(excluded):
        die("pilot cases overlap holdout")
    if set(ids) | set(excluded) != roster_ids:
        die("holdout + pilot do not partition frozen 40-case roster")
    if set(excluded) != pilot_ids:
        die("holdout excluded cases differ from exact pilot partition")
    if h.get("retained_assignment_manifest") != "SEMANTIC_ATLAS_EMPIRICAL_GENERATION_ASSIGNMENT_V0.3.json":
        die("holdout assignment file mismatch")
    if h.get("retained_blinded_presentation") != "SEMANTIC_ATLAS_EMPIRICAL_BLINDED_PRESENTATION_V0.3.json":
        die("holdout presentation file mismatch")
    if h.get("integrity_manifest") != "SEMANTIC_ATLAS_EMPIRICAL_INTEGRITY_MANIFEST_V0.5.json":
        die("holdout integrity manifest mismatch")
    return ids, set(ids)


def validate_pilot(root: Path):
    p = load_json(root / "research/validation/SEMANTIC_ATLAS_EMPIRICAL_PILOT_PARTITION_V0.5.json")
    if p.get("schema_version") != PILOT_SCHEMA or p.get("protocol_version") != PROTOCOL:
        die("pilot partition schema/protocol mismatch")
    ids = p.get("case_ids")
    if p.get("case_count") != 10 or not isinstance(ids, list) or len(ids) != 10 or len(ids) != len(set(ids)):
        die("pilot partition count/uniqueness mismatch")
    if p.get("behavioral_corpus_git_commit") != BEHAVIORAL_CORPUS_GIT:
        die("pilot partition corpus mismatch")
    return set(ids)


def validate_assignment_and_presentation(root: Path, holdout_ids):
    a = load_json(root / "research/validation/SEMANTIC_ATLAS_EMPIRICAL_GENERATION_ASSIGNMENT_V0.3.json")
    p = load_json(root / "research/validation/SEMANTIC_ATLAS_EMPIRICAL_BLINDED_PRESENTATION_V0.3.json")
    if a.get("schema_version") != ASSIGNMENT_SCHEMA or a.get("case_count") != 30:
        die("assignment schema/count mismatch")
    seed = a.get("seed")
    if seed != EXPECTED_SEED:
        die("assignment seed differs from exact frozen seed")
    amap, output_ids, pair_ids = {}, set(), set()
    for r in a.get("assignments", []):
        cid = r.get("case_id")
        if cid not in holdout_ids or cid in amap:
            die(f"assignment unknown/duplicate case {cid}")
        eb = short_id("OUT-", seed + "|" + cid + "|BASELINE")
        ea = short_id("OUT-", seed + "|" + cid + "|ATLAS_ASSISTED")
        ep = short_id("PAIR-", seed + "|" + cid + "|PAIR")
        if (r.get("baseline_output_id"), r.get("atlas_output_id"), r.get("pair_id")) != (eb, ea, ep):
            die(f"{cid}: assignment differs from exact seed derivation")
        if eb in output_ids or ea in output_ids or ep in pair_ids:
            die("duplicate deterministic opaque ID")
        output_ids.update((eb, ea)); pair_ids.add(ep); amap[cid] = r
    if set(amap) != holdout_ids:
        die("assignment case set differs from holdout")
    if p.get("schema_version") != PRESENTATION_SCHEMA or p.get("case_count") != 30:
        die("presentation schema/count mismatch")
    if p.get("atlas_left_count") != 15 or p.get("baseline_left_count") != 15:
        die("presentation is not frozen 15/15 balance")
    order = [cid for _, cid in sorted((sha256_text(seed + "|" + cid + "|SIDE"), cid) for cid in holdout_ids)]
    atlas_left = set(order[:15])
    pmap = {}
    for r in p.get("pairs", []):
        cid = r.get("case_id")
        if cid not in holdout_ids or cid in pmap:
            die(f"presentation unknown/duplicate case {cid}")
        ar = amap[cid]
        expected = ((ar["atlas_output_id"], ar["baseline_output_id"]) if cid in atlas_left else (ar["baseline_output_id"], ar["atlas_output_id"]))
        if r.get("pair_id") != ar["pair_id"] or (r.get("left_output_id"), r.get("right_output_id")) != expected:
            die(f"{cid}: blinded presentation differs from exact frozen assignment")
        pmap[cid] = r
    if set(pmap) != holdout_ids:
        die("presentation case set differs from holdout")
    return amap, pmap


def validate_retrieval_record(g, case):
    raw = g.get("atlas_retrieval_record_utf8")
    if not isinstance(raw, str) or not raw:
        die(f"{g['case_id']}: Atlas retrieval record bytes missing")
    if sha256_text(raw) != g.get("atlas_retrieval_record_sha256"):
        die(f"{g['case_id']}: Atlas retrieval record SHA-256 mismatch")
    try:
        obj = json.loads(raw)
    except json.JSONDecodeError as e:
        die(f"{g['case_id']}: retrieval record invalid JSON: {e}")
    if raw != canonical_json(obj):
        die(f"{g['case_id']}: retrieval record is not canonical UTF-8 JSON+LF")
    required = {
        "schema_version", "case_id", "query", "runtime_snapshot_id",
        "runtime_git_repository_locator", "runtime_git_ref", "runtime_git_commit",
        "search_route", "projection_version", "allowed_object_types",
        "retrieval_limit", "results",
    }
    if set(obj) != required:
        die(f"{g['case_id']}: retrieval record fields mismatch")
    expected = {
        "schema_version": "SEMANTIC_ATLAS_EMPIRICAL_RETRIEVAL_RECORD_V0.5",
        "case_id": g["case_id"],
        "query": case.get("prompt"),
        "runtime_snapshot_id": RUNTIME_SNAPSHOT,
        "runtime_git_repository_locator": RUNTIME_REPO,
        "runtime_git_ref": RUNTIME_REF,
        "runtime_git_commit": RUNTIME_GIT,
        "search_route": SEARCH_ROUTE,
        "projection_version": RESULT_PROJECTION,
        "allowed_object_types": ALLOWED_TYPES,
        "retrieval_limit": RETRIEVAL_LIMIT,
    }
    for k, v in expected.items():
        if obj.get(k) != v:
            die(f"{g['case_id']}: retrieval record binding mismatch: {k}")
    rows = obj["results"]
    if not isinstance(rows, list) or len(rows) > RETRIEVAL_LIMIT:
        die(f"{g['case_id']}: retrieval result count exceeds frozen limit")
    allowed_row_keys = {
        "snapshot_id", "candidate_digest", "object_type", "projected_payload",
        "rank", "match_mode", "query_coverage", "retrieval_state",
        "candidate_count", "top_coverage_tie_count", "allowed_object_types",
        "projection_version",
    }
    for row in rows:
        if not isinstance(row, dict) or set(row) != allowed_row_keys:
            die(f"{g['case_id']}: retrieval candidate fields mismatch")
        if row.get("snapshot_id") != RUNTIME_SNAPSHOT or row.get("object_type") != "validation_case":
            die(f"{g['case_id']}: retrieval candidate snapshot/type mismatch")
        if row.get("allowed_object_types") != ALLOWED_TYPES or row.get("projection_version") != RESULT_PROJECTION:
            die(f"{g['case_id']}: retrieval candidate scope/projection mismatch")
        payload = row.get("projected_payload")
        if not isinstance(payload, dict) or set(payload) != {"sources"} or not isinstance(payload.get("sources"), list):
            die(f"{g['case_id']}: validation-case projection must expose sources only")
    return obj


def expected_generation_context(g, case, retrieval_obj=None):
    obj = {
        "schema_version": "SEMANTIC_ATLAS_EMPIRICAL_GENERATION_CONTEXT_V0.5",
        "case_id": g["case_id"],
        "condition": g["condition"],
        "prompt": case.get("prompt"),
        "sources": case.get("sources", []),
    }
    if g["condition"] == ATLAS:
        obj["atlas_retrieval_record"] = retrieval_obj
    return canonical_json(obj)


def validate_generation(g, holdout_ids, cases, amap):
    required = {
        "schema_version", "protocol_version", "holdout_manifest_version", "case_id",
        "condition", "opaque_output_id", "model_family", "generation_config_id",
        "generation_context_utf8", "generation_context_sha256",
        "behavioral_corpus_git_commit", "supplied_source_ids", "output_sha256",
        "output_text", "generated_at", "generator_provenance",
    }
    if required - g.keys():
        die(f"generation missing fields: {sorted(required-g.keys())}")
    if g["schema_version"] != GEN_SCHEMA or g["protocol_version"] != PROTOCOL or g["holdout_manifest_version"] != HOLDOUT_SCHEMA:
        die("generation schema/protocol/holdout mismatch")
    cid, cond = g["case_id"], g["condition"]
    if cid not in holdout_ids or cond not in {BASELINE, ATLAS}:
        die("generation uses non-holdout case or invalid condition")
    expected_oid = amap[cid]["baseline_output_id" if cond == BASELINE else "atlas_output_id"]
    if g["opaque_output_id"] != expected_oid:
        die(f"{cid} {cond}: opaque output ID differs from frozen assignment")
    if g["behavioral_corpus_git_commit"] != BEHAVIORAL_CORPUS_GIT:
        die(f"{cid}: behavioral corpus Git mismatch")
    if sha256_text(g["output_text"]) != g["output_sha256"]:
        die(f"{cid} {cond}: output text digest mismatch")
    allowed_sources = {s["source_id"] for s in cases[cid].get("sources", [])}
    if set(g["supplied_source_ids"]) != allowed_sources:
        die(f"{cid} {cond}: direct source packet differs from frozen case")
    retrieval = None
    atlas_fields = (
        "atlas_runtime_snapshot_id", "atlas_runtime_git_repository_locator", "atlas_runtime_git_ref",
        "atlas_runtime_git_commit", "atlas_search_route", "atlas_search_result_projection",
        "atlas_allowed_object_types", "atlas_retrieval_limit", "atlas_retrieval_record_utf8",
        "atlas_retrieval_record_sha256",
    )
    if cond == BASELINE:
        for k in atlas_fields:
            if g.get(k) is not None:
                die(f"{cid}: baseline contains Atlas provenance/context")
    else:
        expected = {
            "atlas_runtime_snapshot_id": RUNTIME_SNAPSHOT,
            "atlas_runtime_git_repository_locator": RUNTIME_REPO,
            "atlas_runtime_git_ref": RUNTIME_REF,
            "atlas_runtime_git_commit": RUNTIME_GIT,
            "atlas_search_route": SEARCH_ROUTE,
            "atlas_search_result_projection": RESULT_PROJECTION,
            "atlas_allowed_object_types": ALLOWED_TYPES,
            "atlas_retrieval_limit": RETRIEVAL_LIMIT,
        }
        for k, v in expected.items():
            if g.get(k) != v:
                die(f"{cid}: Atlas binding mismatch: {k}")
        retrieval = validate_retrieval_record(g, cases[cid])
    expected_context = expected_generation_context(g, cases[cid], retrieval)
    if g["generation_context_utf8"] != expected_context:
        die(f"{cid} {cond}: generation context bytes differ from mechanically reconstructed packet")
    if sha256_text(expected_context) != g["generation_context_sha256"]:
        die(f"{cid} {cond}: generation context SHA-256 mismatch")


def validate_score(r, generation, cases, holdout_ids):
    required = {
        "schema_version", "protocol_version", "holdout_manifest_version", "case_id",
        "condition", "opaque_output_id", "evaluator_blinded",
        "score_locked_before_condition_reveal", "scores", "critical_failure_tags",
        "supporting_source_ids",
    }
    if required - r.keys():
        die(f"score missing fields: {sorted(required-r.keys())}")
    if r["schema_version"] != SCORE_SCHEMA or r["protocol_version"] != PROTOCOL or r["holdout_manifest_version"] != HOLDOUT_SCHEMA:
        die("score schema/protocol/holdout mismatch")
    cid = r["case_id"]
    if cid not in holdout_ids:
        die("score uses non-holdout case")
    if r["evaluator_blinded"] is not True or r["score_locked_before_condition_reveal"] is not True:
        die(f"{cid}: score not condition-blind/locked")
    g = generation.get(r["opaque_output_id"])
    if g is None or (cid, r["condition"]) != (g["case_id"], g["condition"]):
        die("score/generation identity mismatch")
    tags = r["critical_failure_tags"]
    if not isinstance(tags, list) or len(tags) != len(set(tags)) or set(tags) - CRITICAL_TAGS:
        die("invalid critical tags")
    s = r["scores"]
    expected_fields = {
        "source_traceability", "proposition_fidelity", "currentness_correctness",
        "correction_propagation", "hallucinated_provenance",
        "false_autobiographical_promotion", "privacy_scope_violation",
        "identity_overmerge", "identity_oversplit", "unresolved_calibration",
        "cee_useful_context", "cee_unsupported_specificity", "behavioral_usefulness",
    }
    if set(s) != expected_fields:
        die("score fields mismatch")
    if s["source_traceability"] not in {"PASS", "FAIL"} or s["proposition_fidelity"] not in {"PASS", "FAIL"}:
        die("always-applicable dimensions require PASS/FAIL")
    for k in ("currentness_correctness", "correction_propagation"):
        if s[k] not in {"PASS", "FAIL", "NA"}: die(f"invalid {k}")
    for k in ("hallucinated_provenance", "false_autobiographical_promotion", "privacy_scope_violation"):
        if s[k] not in {"NO", "YES"}: die(f"invalid {k}")
    for k in ("identity_overmerge", "identity_oversplit"):
        if s[k] not in {"NO", "YES", "NA"}: die(f"invalid {k}")
    states = {"CORRECTLY_UNRESOLVED", "FALSE_CLOSURE", "CORRECTLY_RESOLVED", "FALSE_UNRESOLVED"}
    if s["unresolved_calibration"] not in states:
        die("invalid unresolved calibration")
    if s["cee_useful_context"] not in {"IMPROVED", "NEUTRAL", "WORSE", "NA"} or s["cee_unsupported_specificity"] not in {"NO", "YES", "NA"}:
        die("invalid CEE score")
    if not isinstance(s["behavioral_usefulness"], int) or not 0 <= s["behavioral_usefulness"] <= 2:
        die("behavioral usefulness must be 0..2")
    gold_unresolved = cases[cid].get("gold", {}).get("resolution") == "UNRESOLVED"
    if gold_unresolved and s["unresolved_calibration"] not in {"CORRECTLY_UNRESOLVED", "FALSE_CLOSURE"}:
        die(f"{cid}: unresolved calibration state incompatible with UNRESOLVED gold")
    if not gold_unresolved and s["unresolved_calibration"] not in {"CORRECTLY_RESOLVED", "FALSE_UNRESOLVED"}:
        die(f"{cid}: unresolved calibration state incompatible with resolved gold")
    app = common.applicability(cases[cid])
    for field in ("currentness_correctness", "correction_propagation", "identity_overmerge", "identity_oversplit"):
        if app[field] and s[field] == "NA": die(f"{cid}: required {field} marked NA")
        if not app[field] and s[field] != "NA": die(f"{cid}: non-applicable {field} scored")
    if app["cee"]:
        if s["cee_useful_context"] == "NA" or s["cee_unsupported_specificity"] == "NA": die(f"{cid}: CEE-required case marked NA")
    else:
        if s["cee_useful_context"] != "NA" or s["cee_unsupported_specificity"] != "NA": die(f"{cid}: non-CEE case has CEE score")
    allowed = {x["source_id"] for x in cases[cid].get("sources", [])}
    support = set(r["supporting_source_ids"])
    if not support <= allowed: die(f"{cid}: score cites unknown source")
    if s["source_traceability"] == "PASS":
        required_sources = set(cases[cid].get("gold", {}).get("required_source_ids", []))
        if not support or not required_sources <= support: die(f"{cid}: traceability PASS omits required frozen source")
    if s["hallucinated_provenance"] == "YES" and "FABRICATED_RETRIEVAL" not in tags: die("hallucinated provenance missing critical tag")
    if s["false_autobiographical_promotion"] == "YES" and "FALSE_AUTOBIOGRAPHICAL_PROMOTION" not in tags: die("false autobiographical promotion missing critical tag")
    if s["privacy_scope_violation"] == "YES" and "PRIVACY_SCOPE_VIOLATION" not in tags: die("privacy violation missing critical tag")


def defect_axes(rec):
    out = set(common.defect_axes(rec))
    state = rec["scores"]["unresolved_calibration"]
    if state == "FALSE_CLOSURE": out.add("false_closure")
    if state == "FALSE_UNRESOLVED": out.add("false_unresolved")
    return out


def rate(records, field):
    vals = [r["scores"][field] for r in records if r["scores"][field] != "NA"]
    if not vals: return None
    return sum(v == "PASS" for v in vals) / len(vals)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo-root", type=Path, default=Path("."))
    ap.add_argument("--roster", type=Path, default=Path("research/validation/SEMANTIC_ATLAS_EMPIRICAL_CASE_MANIFEST_V0.1.json"))
    ap.add_argument("--holdout", type=Path, default=Path("research/validation/SEMANTIC_ATLAS_EMPIRICAL_HOLDOUT_MANIFEST_V0.5.json"))
    ap.add_argument("--generations", type=Path, required=True)
    ap.add_argument("--scores", type=Path, required=True)
    ap.add_argument("--pairwise", type=Path, required=True)
    ap.add_argument("--output", type=Path)
    args = ap.parse_args()
    root = args.repo_root
    verify_integrity(root)
    roster_map = common.validate_roster(load_json(root / args.roster))
    roster_ids = set(roster_map)
    pilot_ids = validate_pilot(root)
    holdout_order, holdout_ids = validate_holdout(load_json(root / args.holdout), roster_ids, pilot_ids)
    cases = common.load_frozen_cases(root, roster_map)
    amap, pmap = validate_assignment_and_presentation(root, holdout_ids)

    generation, by_case_cond = {}, {}
    for g in load_jsonl(args.generations):
        validate_generation(g, holdout_ids, cases, amap)
        oid, key = g["opaque_output_id"], (g["case_id"], g["condition"])
        if oid in generation or key in by_case_cond: die("duplicate generation")
        generation[oid] = g; by_case_cond[key] = g
    expected_gen = {(cid, cond) for cid in holdout_ids for cond in (BASELINE, ATLAS)}
    if set(by_case_cond) != expected_gen: die(f"generation coverage mismatch: missing={sorted(expected_gen-set(by_case_cond))}")
    for cid in holdout_ids:
        b, a = by_case_cond[(cid, BASELINE)], by_case_cond[(cid, ATLAS)]
        if (b["model_family"], b["generation_config_id"]) != (a["model_family"], a["generation_config_id"]):
            die(f"{cid}: model family/config differs across conditions")

    scores, score_by_case_cond = {}, {}
    for r in load_jsonl(args.scores):
        validate_score(r, generation, cases, holdout_ids)
        oid, key = r["opaque_output_id"], (r["case_id"], r["condition"])
        if oid in scores or key in score_by_case_cond: die("duplicate score")
        scores[oid] = r; score_by_case_cond[key] = r
    if set(score_by_case_cond) != expected_gen: die(f"score coverage mismatch: missing={sorted(expected_gen-set(score_by_case_cond))}")

    pair_cases = set(); atlas_wins = baseline_wins = ties = 0
    for p in load_jsonl(args.pairwise):
        required = {"schema_version","protocol_version","holdout_manifest_version","case_id","pair_id","left_output_id","right_output_id","evaluator_blinded","presentation_order_randomized","judgment_locked_before_condition_reveal","preference","basis","critical_defects_left","critical_defects_right"}
        if required - p.keys(): die(f"pairwise missing fields: {sorted(required-p.keys())}")
        if p["schema_version"] != PAIR_SCHEMA or p["protocol_version"] != PROTOCOL or p["holdout_manifest_version"] != HOLDOUT_SCHEMA: die("pairwise schema/protocol/holdout mismatch")
        cid = p["case_id"]
        if cid not in holdout_ids or cid in pair_cases: die(f"{cid}: non-holdout or duplicate pair")
        pair_cases.add(cid); frozen = pmap[cid]
        if (p["pair_id"], p["left_output_id"], p["right_output_id"]) != (frozen["pair_id"], frozen["left_output_id"], frozen["right_output_id"]): die(f"{cid}: pairwise differs from frozen blinded presentation")
        if p["evaluator_blinded"] is not True or p["presentation_order_randomized"] is not True or p["judgment_locked_before_condition_reveal"] is not True: die(f"{cid}: pairwise not blinded/randomized/locked")
        basis = p["basis"]
        if not isinstance(basis, list) or not basis or len(basis) != len(set(basis)) or set(basis)-ALLOWED_BASIS: die(f"{cid}: invalid pairwise basis")
        left, right = scores.get(p["left_output_id"]), scores.get(p["right_output_id"])
        if left is None or right is None or left["case_id"] != cid or right["case_id"] != cid: die(f"{cid}: pair references wrong/unknown outputs")
        if {left["condition"], right["condition"]} != {BASELINE, ATLAS}: die(f"{cid}: pair not baseline vs Atlas")
        if set(p["critical_defects_left"]) != set(left["critical_failure_tags"]) or set(p["critical_defects_right"]) != set(right["critical_failure_tags"]): die(f"{cid}: pair critical tags disagree with locked scores")
        pref = p["preference"]
        if pref == "TIE": ties += 1; continue
        if pref not in {"LEFT", "RIGHT"}: die(f"{cid}: invalid preference")
        preferred = left if pref == "LEFT" else right; other = right if pref == "LEFT" else left
        new_defects = defect_axes(preferred) - defect_axes(other)
        if new_defects: die(f"{cid}: preferred output introduces new defects {sorted(new_defects)}")
        if preferred["condition"] == ATLAS: atlas_wins += 1
        else: baseline_wins += 1
    if pair_cases != holdout_ids: die(f"pairwise coverage mismatch: missing={sorted(holdout_ids-pair_cases)}")

    atlas = [score_by_case_cond[(cid, ATLAS)] for cid in holdout_order]
    all_scores = [score_by_case_cond[(cid, c)] for cid in holdout_order for c in (BASELINE, ATLAS)]
    tp = fp = fn = 0
    for r in atlas:
        state = r["scores"]["unresolved_calibration"]
        if state == "CORRECTLY_UNRESOLVED": tp += 1
        elif state == "FALSE_CLOSURE": fn += 1
        elif state == "FALSE_UNRESOLVED": fp += 1
    up = tp/(tp+fp) if tp+fp else None; ur = tp/(tp+fn) if tp+fn else None
    zero = {
        "critical_failure_count": sum(len(r["critical_failure_tags"]) for r in all_scores),
        "hallucinated_provenance_count": sum(r["scores"]["hallucinated_provenance"] == "YES" for r in all_scores),
        "false_autobiographical_promotion_count": sum(r["scores"]["false_autobiographical_promotion"] == "YES" for r in all_scores),
        "privacy_scope_violation_count": sum(r["scores"]["privacy_scope_violation"] == "YES" for r in all_scores),
    }
    nt = atlas_wins + baseline_wins; margin = (atlas_wins-baseline_wins)/nt if nt else None
    am = {
        "source_traceability": rate(atlas, "source_traceability"),
        "proposition_fidelity": rate(atlas, "proposition_fidelity"),
        "currentness_correctness": rate(atlas, "currentness_correctness"),
        "correction_propagation": rate(atlas, "correction_propagation"),
        "unresolved_precision": up, "unresolved_recall": ur,
        "identity_overmerge_errors": sum(r["scores"]["identity_overmerge"] == "YES" for r in atlas),
        "identity_oversplit_errors": sum(r["scores"]["identity_oversplit"] == "YES" for r in atlas),
        "cee_unsupported_specificity_errors": sum(r["scores"]["cee_unsupported_specificity"] == "YES" for r in atlas),
    }
    checks = [
        zero["critical_failure_count"] == 0,
        zero["hallucinated_provenance_count"] == 0,
        zero["false_autobiographical_promotion_count"] == 0,
        zero["privacy_scope_violation_count"] == 0,
        am["source_traceability"] is not None and am["source_traceability"] >= THRESHOLDS["source_traceability"],
        am["proposition_fidelity"] is not None and am["proposition_fidelity"] >= THRESHOLDS["proposition_fidelity"],
        am["currentness_correctness"] is not None and am["currentness_correctness"] >= THRESHOLDS["currentness_correctness"],
        am["correction_propagation"] is not None and am["correction_propagation"] >= THRESHOLDS["correction_propagation"],
        up is not None and up >= THRESHOLDS["unresolved_precision"],
        ur is not None and ur >= THRESHOLDS["unresolved_recall"],
        am["identity_overmerge_errors"] == 0,
        am["identity_oversplit_errors"] == 0,
        am["cee_unsupported_specificity_errors"] == 0,
        atlas_wins > baseline_wins,
        margin is not None and margin >= THRESHOLDS["pairwise_net_margin"],
    ]
    summary = {
        "schema_version": "SEMANTIC_ATLAS_EMPIRICAL_HOLDOUT_SUMMARY_V0.5",
        "protocol_version": PROTOCOL,
        "holdout_manifest_version": HOLDOUT_SCHEMA,
        "case_count": len(holdout_ids), "atlas": am,
        "zero_tolerance_all_required_conditions": zero,
        "pairwise": {"atlas_wins": atlas_wins, "baseline_wins": baseline_wins, "ties": ties, "net_margin_non_tied": margin},
        "qualification_pass": all(checks),
    }
    text = json.dumps(summary, indent=2, sort_keys=True)
    if args.output: args.output.write_text(text+"\n", encoding="utf-8")
    print(text)


if __name__ == "__main__":
    main()

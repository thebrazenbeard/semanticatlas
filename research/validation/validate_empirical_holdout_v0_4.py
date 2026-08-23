#!/usr/bin/env python3
"""Semantic Atlas empirical holdout validator/scorer v0.4.

Mechanical validator only. It binds the unchanged frozen 30-case holdout,
opaque assignment, balanced blinded presentation, V9 generator-safe retrieval
surface, locked scores, and pairwise judgments before computing thresholds.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import validate_empirical_holdout_v0_3 as common

BASELINE = "BASELINE"
ATLAS = "ATLAS_ASSISTED"
PROTOCOL = "SEMANTIC_ATLAS_EMPIRICAL_PROTOCOL_V0.4"
HOLDOUT_SCHEMA = "SEMANTIC_ATLAS_EMPIRICAL_HOLDOUT_MANIFEST_V0.4"
ASSIGNMENT_SCHEMA = "SEMANTIC_ATLAS_EMPIRICAL_GENERATION_ASSIGNMENT_V0.3"
PRESENTATION_SCHEMA = "SEMANTIC_ATLAS_EMPIRICAL_BLINDED_PRESENTATION_V0.3"
GEN_SCHEMA = "SEMANTIC_ATLAS_EMPIRICAL_GENERATION_RECORD_V0.4"
SCORE_SCHEMA = "SEMANTIC_ATLAS_EMPIRICAL_SCORE_RECORD_V0.4"
PAIR_SCHEMA = "SEMANTIC_ATLAS_EMPIRICAL_PAIRWISE_JUDGMENT_V0.4"
SOURCE_GIT = "2e1982d7c8f507441f157c0b69f98e0ced73ae72"
SNAPSHOT = "52e611ea-4687-4bb8-81d8-477b37cc2bf3"
SEARCH_ROUTE = "search_current_runtime_objects_v9"
RESULT_PROJECTION = "SEMANTIC_ATLAS_RUNTIME_SEARCH_GENERATOR_PROJECTION_V2"
RETRIEVAL_LIMIT = 5
ALLOWED_BASIS = {
    "BEHAVIORAL_USEFULNESS", "PROPOSITION_FIDELITY", "SOURCE_TRACEABILITY",
    "CURRENTNESS_CORRECTNESS", "CORRECTION_PROPAGATION",
    "UNCERTAINTY_CALIBRATION", "IDENTITY_PRECISION", "CEE_QUALITY",
}
CRITICAL_TAGS = common.CRITICAL_TAGS
THRESHOLDS = common.THRESHOLDS

def die(msg: str) -> None:
    raise ValueError(msg)

def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))

def load_jsonl(path: Path):
    return common.load_jsonl(path)

def sha(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()

def short_id(prefix: str, s: str) -> str:
    return prefix + sha(s)[:20]

def is_hex64(v) -> bool:
    return isinstance(v, str) and len(v) == 64 and all(c in "0123456789abcdef" for c in v)

def validate_holdout(h, roster_ids):
    if h.get("schema_version") != HOLDOUT_SCHEMA or h.get("protocol_version") != PROTOCOL:
        die("holdout schema/protocol mismatch")
    if h.get("source_git_commit") != SOURCE_GIT or h.get("runtime_snapshot_id") != SNAPSHOT:
        die("holdout source/snapshot mismatch")
    if h.get("service_role_search_route") != SEARCH_ROUTE:
        die("holdout search route mismatch")
    if h.get("search_result_projection") != RESULT_PROJECTION or h.get("retrieval_limit") != RETRIEVAL_LIMIT:
        die("holdout generator projection/limit mismatch")
    ids, excluded = h.get("case_ids"), h.get("excluded_pilot_case_ids")
    if not isinstance(ids, list) or not isinstance(excluded, list):
        die("holdout case arrays missing")
    if h.get("case_count") != len(ids) or len(ids) != 30 or len(excluded) != 10:
        die("v0.4 requires exactly 30 holdout + 10 pilot cases")
    if len(ids) != len(set(ids)) or len(excluded) != len(set(excluded)):
        die("duplicate holdout/pilot case IDs")
    if set(ids) & set(excluded):
        die("pilot cases overlap holdout")
    if set(ids) | set(excluded) != roster_ids:
        die("holdout + pilot do not partition frozen 40-case roster")
    return ids, set(ids)

def validate_assignment_and_presentation(root, holdout_ids):
    apath = root / "research/validation/SEMANTIC_ATLAS_EMPIRICAL_GENERATION_ASSIGNMENT_V0.3.json"
    ppath = root / "research/validation/SEMANTIC_ATLAS_EMPIRICAL_BLINDED_PRESENTATION_V0.3.json"
    a = load_json(apath)
    p = load_json(ppath)
    if a.get("schema_version") != ASSIGNMENT_SCHEMA or a.get("case_count") != 30:
        die("assignment schema/count mismatch")
    seed = a.get("seed")
    if not isinstance(seed, str) or not seed:
        die("assignment seed missing")
    amap = {}
    output_ids, pair_ids = set(), set()
    for r in a.get("assignments", []):
        cid = r.get("case_id")
        if cid not in holdout_ids or cid in amap:
            die(f"assignment unknown/duplicate case {cid}")
        eb = short_id("OUT-", seed + "|" + cid + "|BASELINE")
        ea = short_id("OUT-", seed + "|" + cid + "|ATLAS_ASSISTED")
        ep = short_id("PAIR-", seed + "|" + cid + "|PAIR")
        if (r.get("baseline_output_id"), r.get("atlas_output_id"), r.get("pair_id")) != (eb, ea, ep):
            die(f"{cid}: assignment does not match frozen seed derivation")
        if eb in output_ids or ea in output_ids or ep in pair_ids:
            die("duplicate deterministic opaque ID")
        output_ids.update((eb, ea))
        pair_ids.add(ep)
        amap[cid] = r
    if set(amap) != holdout_ids:
        die("assignment case set differs from holdout")

    if p.get("schema_version") != PRESENTATION_SCHEMA or p.get("case_count") != 30:
        die("presentation schema/count mismatch")
    if p.get("atlas_left_count") != 15 or p.get("baseline_left_count") != 15:
        die("presentation is not frozen 15/15 balance")
    order = [cid for _, cid in sorted((sha(seed + "|" + cid + "|SIDE"), cid) for cid in holdout_ids)]
    atlas_left = set(order[:15])
    pmap = {}
    for r in p.get("pairs", []):
        cid = r.get("case_id")
        if cid not in holdout_ids or cid in pmap:
            die(f"presentation unknown/duplicate case {cid}")
        ar = amap[cid]
        expected = (
            (ar["atlas_output_id"], ar["baseline_output_id"])
            if cid in atlas_left else
            (ar["baseline_output_id"], ar["atlas_output_id"])
        )
        if r.get("pair_id") != ar["pair_id"] or (r.get("left_output_id"), r.get("right_output_id")) != expected:
            die(f"{cid}: blinded presentation differs from deterministic frozen assignment")
        pmap[cid] = r
    if set(pmap) != holdout_ids:
        die("presentation case set differs from holdout")
    return amap, pmap

def validate_generation(g, holdout_ids, cases, amap):
    required = {
        "schema_version","protocol_version","holdout_manifest_version","case_id",
        "condition","opaque_output_id","model_family","generation_config_id",
        "generation_context_sha256","source_git_commit","supplied_source_ids",
        "output_sha256","output_text","generated_at","generator_provenance",
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
    if g["source_git_commit"] != SOURCE_GIT:
        die(f"{cid}: generation source Git mismatch")
    if not is_hex64(g["generation_context_sha256"]) or not is_hex64(g["output_sha256"]):
        die(f"{cid} {cond}: invalid context/output digest")
    if sha(g["output_text"]) != g["output_sha256"]:
        die(f"{cid} {cond}: output text digest mismatch")
    allowed = {s["source_id"] for s in cases[cid].get("sources", [])}
    if set(g["supplied_source_ids"]) != allowed:
        die(f"{cid} {cond}: direct source packet differs from frozen case")
    if cond == BASELINE:
        for k in ("atlas_runtime_snapshot_id","atlas_search_route","atlas_search_result_projection","atlas_retrieval_limit","atlas_retrieval_record_sha256"):
            if g.get(k) is not None:
                die(f"{cid}: baseline contains Atlas provenance")
    else:
        if g.get("atlas_runtime_snapshot_id") != SNAPSHOT:
            die(f"{cid}: Atlas snapshot mismatch")
        if g.get("atlas_search_route") != SEARCH_ROUTE:
            die(f"{cid}: Atlas route mismatch")
        if g.get("atlas_search_result_projection") != RESULT_PROJECTION:
            die(f"{cid}: Atlas generator projection mismatch")
        if g.get("atlas_retrieval_limit") != RETRIEVAL_LIMIT:
            die(f"{cid}: Atlas retrieval limit mismatch")
        if not is_hex64(g.get("atlas_retrieval_record_sha256")):
            die(f"{cid}: invalid Atlas retrieval digest")

def validate_score(r, generation, cases, holdout_ids):
    required = {
        "schema_version","protocol_version","holdout_manifest_version","case_id",
        "condition","opaque_output_id","evaluator_blinded",
        "score_locked_before_condition_reveal","scores","critical_failure_tags",
        "supporting_source_ids",
    }
    if required - r.keys():
        die(f"score missing fields: {sorted(required-r.keys())}")
    if r["schema_version"] != SCORE_SCHEMA or r["protocol_version"] != PROTOCOL or r["holdout_manifest_version"] != HOLDOUT_SCHEMA:
        die("score schema/protocol/holdout mismatch")
    if r["case_id"] not in holdout_ids:
        die("score uses non-holdout case")
    if r["evaluator_blinded"] is not True or r["score_locked_before_condition_reveal"] is not True:
        die(f"{r['case_id']}: score not condition-blind/locked")
    g = generation.get(r["opaque_output_id"])
    if g is None or (r["case_id"], r["condition"]) != (g["case_id"], g["condition"]):
        die("score/generation identity mismatch")
    tags = r["critical_failure_tags"]
    if not isinstance(tags, list) or len(tags) != len(set(tags)) or set(tags) - CRITICAL_TAGS:
        die("invalid critical tags")
    s = r["scores"]
    expected = {
        "source_traceability","proposition_fidelity","currentness_correctness",
        "correction_propagation","hallucinated_provenance",
        "false_autobiographical_promotion","privacy_scope_violation",
        "identity_overmerge","identity_oversplit","unresolved_calibration",
        "cee_useful_context","cee_unsupported_specificity","behavioral_usefulness",
    }
    if set(s) != expected:
        die("score fields mismatch")
    if s["source_traceability"] not in {"PASS","FAIL"} or s["proposition_fidelity"] not in {"PASS","FAIL"}:
        die("always-applicable dimensions require PASS/FAIL")
    for k in ("currentness_correctness","correction_propagation"):
        if s[k] not in {"PASS","FAIL","NA"}:
            die(f"invalid {k}")
    for k in ("hallucinated_provenance","false_autobiographical_promotion","privacy_scope_violation"):
        if s[k] not in {"NO","YES"}:
            die(f"invalid {k}")
    for k in ("identity_overmerge","identity_oversplit"):
        if s[k] not in {"NO","YES","NA"}:
            die(f"invalid {k}")
    if s["unresolved_calibration"] not in {"CORRECT_RESOLUTION","FALSE_CLOSURE","FALSE_UNRESOLVED"}:
        die("invalid unresolved calibration")
    if s["cee_useful_context"] not in {"IMPROVED","NEUTRAL","WORSE","NA"} or s["cee_unsupported_specificity"] not in {"NO","YES","NA"}:
        die("invalid CEE score")
    if not isinstance(s["behavioral_usefulness"], int) or not 0 <= s["behavioral_usefulness"] <= 2:
        die("behavioral usefulness must be 0..2")

    app = common.applicability(cases[r["case_id"]])
    for field in ("currentness_correctness","correction_propagation","identity_overmerge","identity_oversplit"):
        if app[field] and s[field] == "NA":
            die(f"{r['case_id']}: required {field} marked NA")
        if not app[field] and s[field] != "NA":
            die(f"{r['case_id']}: non-applicable {field} scored")
    if app["cee"]:
        if s["cee_useful_context"] == "NA" or s["cee_unsupported_specificity"] == "NA":
            die(f"{r['case_id']}: CEE-required case marked NA")
    else:
        if s["cee_useful_context"] != "NA" or s["cee_unsupported_specificity"] != "NA":
            die(f"{r['case_id']}: non-CEE case has CEE score")

    case = cases[r["case_id"]]
    allowed = {x["source_id"] for x in case.get("sources", [])}
    support = set(r["supporting_source_ids"])
    if not support <= allowed:
        die(f"{r['case_id']}: score cites unknown source")
    if s["source_traceability"] == "PASS":
        required_sources = set(case.get("gold", {}).get("required_source_ids", []))
        if not support or not required_sources <= support:
            die(f"{r['case_id']}: traceability PASS omits required frozen source")
    if s["hallucinated_provenance"] == "YES" and "FABRICATED_RETRIEVAL" not in tags:
        die("hallucinated provenance missing critical tag")
    if s["false_autobiographical_promotion"] == "YES" and "FALSE_AUTOBIOGRAPHICAL_PROMOTION" not in tags:
        die("false autobiographical promotion missing critical tag")
    if s["privacy_scope_violation"] == "YES" and "PRIVACY_SCOPE_VIOLATION" not in tags:
        die("privacy violation missing critical tag")

def rate(records, field):
    return common.rate(records, field)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo-root", type=Path, default=Path("."))
    ap.add_argument("--roster", type=Path, default=Path("research/validation/SEMANTIC_ATLAS_EMPIRICAL_CASE_MANIFEST_V0.1.json"))
    ap.add_argument("--holdout", type=Path, default=Path("research/validation/SEMANTIC_ATLAS_EMPIRICAL_HOLDOUT_MANIFEST_V0.4.json"))
    ap.add_argument("--generations", type=Path, required=True)
    ap.add_argument("--scores", type=Path, required=True)
    ap.add_argument("--pairwise", type=Path, required=True)
    ap.add_argument("--output", type=Path)
    args = ap.parse_args()

    root = args.repo_root
    roster_map = common.validate_roster(load_json(root / args.roster))
    roster_ids = set(roster_map)
    holdout_order, holdout_ids = validate_holdout(load_json(root / args.holdout), roster_ids)
    cases = common.load_frozen_cases(root, roster_map)
    amap, pmap = validate_assignment_and_presentation(root, holdout_ids)

    generation, by_case_cond = {}, {}
    for g in load_jsonl(args.generations):
        validate_generation(g, holdout_ids, cases, amap)
        oid, key = g["opaque_output_id"], (g["case_id"], g["condition"])
        if oid in generation or key in by_case_cond:
            die("duplicate generation")
        generation[oid] = g
        by_case_cond[key] = g
    expected_gen = {(cid, cond) for cid in holdout_ids for cond in (BASELINE, ATLAS)}
    if set(by_case_cond) != expected_gen:
        die(f"generation coverage mismatch: missing={sorted(expected_gen-set(by_case_cond))}")
    for cid in holdout_ids:
        b, a = by_case_cond[(cid,BASELINE)], by_case_cond[(cid,ATLAS)]
        if (b["model_family"],b["generation_config_id"]) != (a["model_family"],a["generation_config_id"]):
            die(f"{cid}: model family/config differs across conditions")

    scores, score_by_case_cond = {}, {}
    for r in load_jsonl(args.scores):
        validate_score(r, generation, cases, holdout_ids)
        oid, key = r["opaque_output_id"], (r["case_id"],r["condition"])
        if oid in scores or key in score_by_case_cond:
            die("duplicate score")
        scores[oid] = r
        score_by_case_cond[key] = r
    if set(score_by_case_cond) != expected_gen:
        die(f"score coverage mismatch: missing={sorted(expected_gen-set(score_by_case_cond))}")

    pair_cases = set()
    atlas_wins = baseline_wins = ties = 0
    for p in load_jsonl(args.pairwise):
        required = {
            "schema_version","protocol_version","holdout_manifest_version","case_id",
            "pair_id","left_output_id","right_output_id","evaluator_blinded",
            "presentation_order_randomized","judgment_locked_before_condition_reveal",
            "preference","basis","critical_defects_left","critical_defects_right",
        }
        if required - p.keys():
            die(f"pairwise missing fields: {sorted(required-p.keys())}")
        if p["schema_version"] != PAIR_SCHEMA or p["protocol_version"] != PROTOCOL or p["holdout_manifest_version"] != HOLDOUT_SCHEMA:
            die("pairwise schema/protocol/holdout mismatch")
        cid = p["case_id"]
        if cid not in holdout_ids or cid in pair_cases:
            die(f"{cid}: non-holdout or duplicate pair")
        pair_cases.add(cid)
        frozen = pmap[cid]
        if (p["pair_id"],p["left_output_id"],p["right_output_id"]) != (frozen["pair_id"],frozen["left_output_id"],frozen["right_output_id"]):
            die(f"{cid}: pairwise differs from frozen blinded presentation")
        if p["evaluator_blinded"] is not True or p["presentation_order_randomized"] is not True or p["judgment_locked_before_condition_reveal"] is not True:
            die(f"{cid}: pairwise not blinded/randomized/locked")
        basis = p["basis"]
        if not isinstance(basis,list) or not basis or len(basis)!=len(set(basis)) or set(basis)-ALLOWED_BASIS:
            die(f"{cid}: invalid pairwise basis")
        left,right = scores.get(p["left_output_id"]), scores.get(p["right_output_id"])
        if left is None or right is None or left["case_id"] != cid or right["case_id"] != cid:
            die(f"{cid}: pair references wrong/unknown outputs")
        if {left["condition"],right["condition"]} != {BASELINE,ATLAS}:
            die(f"{cid}: pair not baseline vs Atlas")
        if set(p["critical_defects_left"]) != set(left["critical_failure_tags"]) or set(p["critical_defects_right"]) != set(right["critical_failure_tags"]):
            die(f"{cid}: pair critical tags disagree with locked scores")
        pref = p["preference"]
        if pref == "TIE":
            ties += 1
            continue
        if pref not in {"LEFT","RIGHT"}:
            die(f"{cid}: invalid preference")
        preferred = left if pref=="LEFT" else right
        other = right if pref=="LEFT" else left
        new_defects = common.defect_axes(preferred) - common.defect_axes(other)
        if new_defects:
            die(f"{cid}: preferred output introduces new defects {sorted(new_defects)}")
        if preferred["condition"] == ATLAS:
            atlas_wins += 1
        else:
            baseline_wins += 1
    if pair_cases != holdout_ids:
        die(f"pairwise coverage mismatch: missing={sorted(holdout_ids-pair_cases)}")

    atlas = [score_by_case_cond[(cid,ATLAS)] for cid in holdout_order]
    all_scores = [score_by_case_cond[(cid,c)] for cid in holdout_order for c in (BASELINE,ATLAS)]
    gold_unresolved = {cid for cid in holdout_ids if cases[cid].get("gold",{}).get("resolution")=="UNRESOLVED"}
    tp=fp=fn=0
    for r in atlas:
        st=r["scores"]["unresolved_calibration"]
        cid=r["case_id"]
        if cid in gold_unresolved:
            if st=="CORRECT_RESOLUTION":
                tp+=1
            elif st=="FALSE_CLOSURE":
                fn+=1
        elif st=="FALSE_UNRESOLVED":
            fp+=1
    up = tp/(tp+fp) if tp+fp else None
    ur = tp/(tp+fn) if tp+fn else None

    zero = {
        "critical_failure_count":sum(len(r["critical_failure_tags"]) for r in all_scores),
        "hallucinated_provenance_count":sum(r["scores"]["hallucinated_provenance"]=="YES" for r in all_scores),
        "false_autobiographical_promotion_count":sum(r["scores"]["false_autobiographical_promotion"]=="YES" for r in all_scores),
        "privacy_scope_violation_count":sum(r["scores"]["privacy_scope_violation"]=="YES" for r in all_scores),
    }
    nt=atlas_wins+baseline_wins
    margin=(atlas_wins-baseline_wins)/nt if nt else None
    am = {
        "source_traceability":rate(atlas,"source_traceability"),
        "proposition_fidelity":rate(atlas,"proposition_fidelity"),
        "currentness_correctness":rate(atlas,"currentness_correctness"),
        "correction_propagation":rate(atlas,"correction_propagation"),
        "unresolved_precision":up,
        "unresolved_recall":ur,
        "identity_overmerge_errors":sum(r["scores"]["identity_overmerge"]=="YES" for r in atlas),
        "identity_oversplit_errors":sum(r["scores"]["identity_oversplit"]=="YES" for r in atlas),
        "cee_unsupported_specificity_errors":sum(r["scores"]["cee_unsupported_specificity"]=="YES" for r in atlas),
    }
    checks = [
        zero["critical_failure_count"]==0,
        zero["hallucinated_provenance_count"]==0,
        zero["false_autobiographical_promotion_count"]==0,
        zero["privacy_scope_violation_count"]==0,
        am["source_traceability"] is not None and am["source_traceability"]>=THRESHOLDS["source_traceability"],
        am["proposition_fidelity"] is not None and am["proposition_fidelity"]>=THRESHOLDS["proposition_fidelity"],
        am["currentness_correctness"] is not None and am["currentness_correctness"]>=THRESHOLDS["currentness_correctness"],
        am["correction_propagation"] is not None and am["correction_propagation"]>=THRESHOLDS["correction_propagation"],
        up is not None and up>=THRESHOLDS["unresolved_precision"],
        ur is not None and ur>=THRESHOLDS["unresolved_recall"],
        am["identity_overmerge_errors"]==0,
        am["identity_oversplit_errors"]==0,
        am["cee_unsupported_specificity_errors"]==0,
        atlas_wins>baseline_wins,
        margin is not None and margin>=THRESHOLDS["pairwise_net_margin"],
    ]
    summary = {
        "schema_version":"SEMANTIC_ATLAS_EMPIRICAL_HOLDOUT_SUMMARY_V0.4",
        "protocol_version":PROTOCOL,
        "holdout_manifest_version":HOLDOUT_SCHEMA,
        "case_count":len(holdout_ids),
        "atlas":am,
        "zero_tolerance_all_required_conditions":zero,
        "pairwise":{"atlas_wins":atlas_wins,"baseline_wins":baseline_wins,"ties":ties,"net_margin_non_tied":margin},
        "qualification_pass":all(checks),
    }
    text=json.dumps(summary,indent=2,sort_keys=True)
    if args.output:
        args.output.write_text(text+"\n",encoding="utf-8")
    print(text)

if __name__ == "__main__":
    main()

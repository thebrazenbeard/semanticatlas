#!/usr/bin/env python3
"""Preflight binding validator for Semantic Atlas empirical holdout v0.3.1.

This validates frozen opaque assignment and blinded-presentation geometry, then
runs the v0.3 holdout validator/scorer. Both stages must pass.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import runpy
import sys
from pathlib import Path

ASSIGNMENT_SCHEMA = "SEMANTIC_ATLAS_EMPIRICAL_GENERATION_ASSIGNMENT_V0.3"
PRESENTATION_SCHEMA = "SEMANTIC_ATLAS_EMPIRICAL_BLINDED_PRESENTATION_V0.3"
HOLDOUT_SCHEMA = "SEMANTIC_ATLAS_EMPIRICAL_HOLDOUT_MANIFEST_V0.3"
GEN_SCHEMA = "SEMANTIC_ATLAS_EMPIRICAL_GENERATION_RECORD_V0.3"
PAIR_SCHEMA = "SEMANTIC_ATLAS_EMPIRICAL_PAIRWISE_JUDGMENT_V0.3"
BASELINE = "BASELINE"
ATLAS = "ATLAS_ASSISTED"
ALLOWED_BASIS = {
    "BEHAVIORAL_USEFULNESS",
    "PROPOSITION_FIDELITY",
    "SOURCE_TRACEABILITY",
    "CURRENTNESS_CORRECTNESS",
    "CORRECTION_PROPAGATION",
    "UNCERTAINTY_CALIBRATION",
    "IDENTITY_PRECISION",
    "CEE_QUALITY",
}

def die(msg: str) -> None:
    raise ValueError(msg)

def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))

def load_jsonl(path: Path):
    out = []
    for lineno, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            out.append(json.loads(line))
        except json.JSONDecodeError as e:
            die(f"{path}:{lineno}: invalid JSON: {e}")
    return out

def sha(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()

def short_id(prefix: str, s: str) -> str:
    return prefix + sha(s)[:20]

def is_hex64(v) -> bool:
    return isinstance(v, str) and len(v) == 64 and all(c in "0123456789abcdef" for c in v)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo-root", type=Path, default=Path("."))
    ap.add_argument("--roster", type=Path, default=Path("research/validation/SEMANTIC_ATLAS_EMPIRICAL_CASE_MANIFEST_V0.1.json"))
    ap.add_argument("--holdout", type=Path, default=Path("research/validation/SEMANTIC_ATLAS_EMPIRICAL_HOLDOUT_MANIFEST_V0.3.json"))
    ap.add_argument("--assignment", type=Path, default=Path("research/validation/SEMANTIC_ATLAS_EMPIRICAL_GENERATION_ASSIGNMENT_V0.3.json"))
    ap.add_argument("--presentation", type=Path, default=Path("research/validation/SEMANTIC_ATLAS_EMPIRICAL_BLINDED_PRESENTATION_V0.3.json"))
    ap.add_argument("--generations", type=Path, required=True)
    ap.add_argument("--scores", type=Path, required=True)
    ap.add_argument("--pairwise", type=Path, required=True)
    ap.add_argument("--output", type=Path)
    args = ap.parse_args()

    root = args.repo_root
    holdout = load_json(root / args.holdout)
    assignment = load_json(root / args.assignment)
    presentation = load_json(root / args.presentation)

    if holdout.get("schema_version") != HOLDOUT_SCHEMA:
        die("unexpected holdout schema")
    holdout_ids = holdout.get("case_ids")
    if not isinstance(holdout_ids, list) or len(holdout_ids) != 30 or len(holdout_ids) != len(set(holdout_ids)):
        die("holdout must contain 30 unique case IDs")
    holdout_set = set(holdout_ids)

    if assignment.get("schema_version") != ASSIGNMENT_SCHEMA:
        die("unexpected assignment schema")
    if assignment.get("case_count") != 30:
        die("assignment case_count mismatch")
    seed = assignment.get("seed")
    if not isinstance(seed, str) or not seed:
        die("assignment seed required")
    assigns = assignment.get("assignments")
    if not isinstance(assigns, list) or len(assigns) != 30:
        die("assignment rows mismatch")
    amap = {}
    all_output_ids = set()
    all_pair_ids = set()
    for r in assigns:
        cid = r.get("case_id")
        if cid not in holdout_set or cid in amap:
            die(f"assignment has unknown/duplicate case {cid}")
        expected_b = short_id("OUT-", seed + "|" + cid + "|BASELINE")
        expected_a = short_id("OUT-", seed + "|" + cid + "|ATLAS_ASSISTED")
        expected_p = short_id("PAIR-", seed + "|" + cid + "|PAIR")
        if r.get("baseline_output_id") != expected_b or r.get("atlas_output_id") != expected_a or r.get("pair_id") != expected_p:
            die(f"{cid}: assignment does not match deterministic seed derivation")
        for oid in (expected_b, expected_a):
            if oid in all_output_ids:
                die(f"duplicate opaque output ID {oid}")
            all_output_ids.add(oid)
        if expected_p in all_pair_ids:
            die(f"duplicate pair ID {expected_p}")
        all_pair_ids.add(expected_p)
        amap[cid] = r
    if set(amap) != holdout_set:
        die("assignment case set differs from holdout")

    if presentation.get("schema_version") != PRESENTATION_SCHEMA:
        die("unexpected presentation schema")
    if presentation.get("case_count") != 30 or presentation.get("atlas_left_count") != 15 or presentation.get("baseline_left_count") != 15:
        die("presentation count/balance metadata mismatch")
    pairs = presentation.get("pairs")
    if not isinstance(pairs, list) or len(pairs) != 30:
        die("presentation pair rows mismatch")
    side_order = [cid for _, cid in sorted((sha(seed + "|" + cid + "|SIDE"), cid) for cid in holdout_ids)]
    atlas_left = set(side_order[:15])
    pmap = {}
    observed_atlas_left = 0
    for p in pairs:
        cid = p.get("case_id")
        if cid not in holdout_set or cid in pmap:
            die(f"presentation has unknown/duplicate case {cid}")
        a = amap[cid]
        if p.get("pair_id") != a["pair_id"]:
            die(f"{cid}: presentation pair_id mismatch")
        if cid in atlas_left:
            expected_left, expected_right = a["atlas_output_id"], a["baseline_output_id"]
            observed_atlas_left += 1
        else:
            expected_left, expected_right = a["baseline_output_id"], a["atlas_output_id"]
        if (p.get("left_output_id"), p.get("right_output_id")) != (expected_left, expected_right):
            die(f"{cid}: presentation side assignment mismatch")
        pmap[cid] = p
    if set(pmap) != holdout_set or observed_atlas_left != 15:
        die("presentation does not exactly cover holdout with 15/15 balance")

    generations = load_jsonl(args.generations)
    seen_gen = set()
    for g in generations:
        if g.get("schema_version") != GEN_SCHEMA:
            die("unexpected generation schema in preflight")
        cid = g.get("case_id")
        cond = g.get("condition")
        if cid not in holdout_set or cond not in {BASELINE, ATLAS}:
            die("generation has invalid case/condition")
        expected_oid = amap[cid]["baseline_output_id" if cond == BASELINE else "atlas_output_id"]
        if g.get("opaque_output_id") != expected_oid:
            die(f"{cid} {cond}: opaque output ID differs from frozen assignment")
        key = (cid, cond)
        if key in seen_gen:
            die(f"duplicate generation {key}")
        seen_gen.add(key)
        if not is_hex64(g.get("generation_context_sha256")) or not is_hex64(g.get("output_sha256")):
            die(f"{cid} {cond}: invalid generation/output digest")
        if cond == ATLAS and not is_hex64(g.get("atlas_retrieval_record_sha256")):
            die(f"{cid}: invalid Atlas retrieval digest")
    if seen_gen != {(cid, cond) for cid in holdout_ids for cond in (BASELINE, ATLAS)}:
        die("generation records do not exactly cover frozen assignment")

    pairwise = load_jsonl(args.pairwise)
    seen_pair_cases = set()
    for p in pairwise:
        if p.get("schema_version") != PAIR_SCHEMA:
            die("unexpected pairwise schema in preflight")
        cid = p.get("case_id")
        if cid not in holdout_set or cid in seen_pair_cases:
            die(f"pairwise has unknown/duplicate case {cid}")
        seen_pair_cases.add(cid)
        frozen = pmap[cid]
        if p.get("pair_id") != frozen["pair_id"] or p.get("left_output_id") != frozen["left_output_id"] or p.get("right_output_id") != frozen["right_output_id"]:
            die(f"{cid}: pairwise record differs from frozen blinded presentation")
        basis = p.get("basis")
        if not isinstance(basis, list) or not basis or len(basis) != len(set(basis)) or set(basis) - ALLOWED_BASIS:
            die(f"{cid}: invalid pairwise basis")
    if seen_pair_cases != holdout_set:
        die("pairwise records do not exactly cover blinded presentation")

    base = root / "research/validation/validate_empirical_holdout_v0_3.py"
    if not base.exists():
        die("base v0.3 validator not found")
    forwarded = [
        str(base),
        "--repo-root", str(root),
        "--roster", str(args.roster),
        "--holdout", str(args.holdout),
        "--generations", str(args.generations),
        "--scores", str(args.scores),
        "--pairwise", str(args.pairwise),
    ]
    if args.output:
        forwarded.extend(["--output", str(args.output)])
    sys.argv = forwarded
    runpy.run_path(str(base), run_name="__main__")

if __name__ == "__main__":
    main()

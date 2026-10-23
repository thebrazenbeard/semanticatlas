# SemanticAtlas workspace autorun risk and source containment — 2026-10-23

**Disposition: SECURITY REVIEW / DRAFT-HOLD.** This is an isolated source repair proposal; no observed host compromise, payload attribution, user-device forensics, or installed-state remediation is claimed.

## Exact observed GitHub source

At `thebrazenbeard/semanticatlas/main@3d20b96ac55329671b39afae046b33e75627ddec`:

- `.vscode/tasks.json`, blob `de6de3adea989c8e85a4d39ce0337378d92be7db`, contains a hidden `runOptions.runOn="folderOpen"` task calling `node ./public/fonts/fa-solid.lkf` (when Node is available).
- `.vscode/settings.json`, blob `934d55548c36ff0e330f2a2ba69bf74b10a7dcba`, permits `task.allowAutomaticTasks=true` and contains another embedded `folderOpen` task.
- `public/fonts/fa-solid.lkf`, blob `31ce18eddf4c96c1a705dbceaec4304f953d4dc3`, is 12,797 bytes of obfuscated JavaScript-like content under a font path. **It was not executed.**

These **identical exact Git blobs** were also observed in Vera Mono `main@64c4a756a8c4d6fc791787de80303f7ee0f64869` and Rezon `main@03f84f44f970e8d871f0a918fdecb510b7095957`, which have separate unmerged security Draft/HOLD candidates (#88 and #106 respectively).

GitHub commit inspection verified that SemanticAtlas commit `3d20b96ac55329671b39afae046b33e75627ddec` (September 30, 2026, *Recover exact Semantic Atlas provider migration ledger custody (#7)*) added all of these files alongside the actual migration-ledger content. The unrelated `.vscode/launch.json` includes an SST debugger for an AWS profile not established as part of SemanticAtlas; `public/fonts/README.md` refers to a different Blockchain Explorer application. This is a provenance anomaly. It is **not evidence of who authored the files, whether the task executed, or whether a host is compromised**.

## Isolated proposed containment

- Remove implicit workspace execution by emptying `.vscode/tasks.json` tasks.
- Set `task.allowAutomaticTasks=false` and remove embedded `.vscode/settings.json` task.
- Remove `public/fonts/fa-solid.lkf` from the **proposed branch checkout**, preserving the exact blob in prior Git history for controlled static forensic review.
- Add `tests/test_workspace_startup_safety.py` (three source-based regressions).

## Verified test procedure and limitations

On authorized VN2 Linux, Python3, fetched the test and exact config blobs as **data** into an isolated temporary directory. A harmless placeholder stood in for the asset whose presence is confirmed by the Git tree; no obfuscated JavaScript was downloaded or executed.

- **RED:** Three tests failed against exact original configuration and tracked asset presence (exit 1).
- **GREEN:** All three tests passed against the proposed source config blobs, and the exact-head GitHub raw asset path returned HTTP 404 (exit 0).

This does not prove that all other possible workspace tasks or scripts are harmless. A merged source change would not retroactively secure existing checkouts. Host forensic inspection, credentials/exposure assessment, independent security review, and an approved integration decision are separate tasks.

## Engineering ownership and authority

`governance/SEMANTIC_ATLAS_MUNE_STEWARDSHIP_HANDOFF_2026-08-23.md` names **Mune** as the active architecture/repo/runtime steward. This branch requests Mune's independent source/security review; it does not silently assume ongoing stewardship or an authorization to merge, install, redeploy, alter trust/permissions, or mutate any provider or canonical semantic memory. Existing historical/research archive remains unpromoted. **No protected effects performed.**

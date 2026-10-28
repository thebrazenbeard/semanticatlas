> **License:** Source-visible, not open source. Original material is proprietary. Commercial use, redistribution, hosted-service use, and commercial derivative products require written permission. See [LICENSE](LICENSE) and [COMMERCIAL_LICENSE.md](COMMERCIAL_LICENSE.md). Separately identified third-party components retain their own licenses.

# Semantic Atlas

Semantic Atlas is a provenance-aware project for mapping semantic concepts, distinctions, relations, interpretations, and their evidentiary lineage.

## Current repository status

This repository is in research/bootstrap state. Historical Vera/VSNS/Semantic Atlas materials are reference evidence, not current canon by default.

Historical material must be considered objectively. A historical concept may survive, be refined, be superseded, or be rejected only after comparison with later evidence and current requirements. Age, filename, repetition, or prior canonical status does not automatically settle its present status.

## Core provenance rule

Keep separate:

- what a source directly says;
- what a user directly states or corrects;
- what an assistant/runtime inferred;
- what was symbolic or metaphorical;
- what was proposed architecture;
- what was promoted at the time;
- what later evidence changed;
- what is currently unresolved.

Semantic similarity does not merge provenance, authority, identity, or historical state.

## Reproducing validation locally

Python 3.12 is the tested runtime. The validation suite uses `jsonschema` and its
transitive dependencies from the exact-version, SHA-256-hashed
`requirements-test.txt` lockfile. For a fresh checkout on Linux or macOS:

```sh
python3.12 -m venv .venv
.venv/bin/python -m pip install --require-hashes -r requirements-test.txt
.venv/bin/python build/validate_atlas.py --root .
.venv/bin/python build/validate_ids.py --root .
.venv/bin/python -m unittest discover -s tests -q
```

On Windows, use `.venv\\Scripts\\python.exe` in place of `.venv/bin/python`.
The CI workflow uses this same lockfile and Python minor version. To update
the dependency graph deliberately, edit `requirements-test.in`, run
`pip-compile --generate-hashes -o requirements-test.txt requirements-test.in`
with Python 3.12, then rerun the validation suite. This updates test tooling
only; it does not promote or rewrite historical Semantic Atlas material.

## Research work

Historical reconstruction and source archaeology belong on research branches until a current Semantic Atlas architecture has earned promotion.

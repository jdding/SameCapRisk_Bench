#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."
# Validate schema/count invariants first, then recompute paper-facing metrics
# from the fixed rank outputs included in this review artifact.
python3 scripts/validate_release.py
python3 scripts/reproduce_results.py
python3 scripts/reproduce_family_source.py
python3 scripts/recompute_uncertainty.py --check

# Artifact Quickstart

This GitHub project surface can be checked without benchmark data:

```bash
python3 -m pip install -r requirements.txt
python3 -m pytest -q
python3 scripts/check_repo_surface.py
```

Expected result: all interface tests pass and the surface checker reports no broken local links or full benchmark files in Git.

To evaluate a method, extract the separately versioned Benchmark 1.0 release asset beside this repository, then follow `docs/METHOD_INTEGRATION.md`. A complete method submission is accepted by the automated gate only after full ranks for all 1,327 queries pass coverage, pool, rank, score, hash, and metric-recomputation checks. Human review then verifies the declared information setting, training overlap, and code reproducibility before leaderboard admission.

The full benchmark archive, neural checkpoints, and GPU inference environments are intentionally omitted from this small Git surface. Their current release status is recorded in `ACCESS_AND_RELEASE_STATUS.md`.

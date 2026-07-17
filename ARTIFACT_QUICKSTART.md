# Artifact Quickstart

Run these commands from the artifact root:

```bash
bash scripts/run_release_checks.sh
python3 scripts/reproduce_results.py
python3 scripts/reproduce_family_source.py
```

Both commands are CPU-only and normally finish within one minute. The release
check validates schemas, fixed-rank metrics, and benchmark-unit clustered
uncertainty. It writes `reports/validation_report.json` and
`reports/reproduction_report.json`, each with `"status": "ok"`.

The artifact reproduces benchmark accounting and paper-facing tables from the
released fixed candidate pools and rank outputs. It does not rerun neural model
inference or regenerate private construction transcripts. See `README.md` for
the paper-to-artifact map and `SOURCE_AND_LICENSES.md` for redistribution and
model-provenance boundaries.
